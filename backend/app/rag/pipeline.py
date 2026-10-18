import os
import math
import re
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings

class RAGPipeline:
    """
    Local-first Retrieval-Augmented Generation pipeline.
    Uses TF-IDF + cosine similarity as a robust zero-dependency offline local embedding engine,
    and connects to local Ollama (llama3.2:3b) when running, with graceful deterministic fallback.
    """
    def __init__(self, knowledge_base_dir: Optional[str] = None):
        self.kb_dir = knowledge_base_dir or settings.KNOWLEDGE_BASE_DIR
        self.documents: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[Dict[str, float]] = []
        self._load_and_index_documents()

    def _tokenize(self, text: str) -> List[str]:
        return [word.lower() for word in re.findall(r'\b[a-zA-Z0-9_-]{2,}\b', text)]

    def _load_and_index_documents(self):
        """Loads and indexes text & markdown files from the local knowledge base directory."""
        self.documents = []
        if not os.path.exists(self.kb_dir):
            os.makedirs(self.kb_dir, exist_ok=True)

        for root, _, files in os.walk(self.kb_dir):
            for file in files:
                if file.endswith((".md", ".txt", ".json")):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Chunk document by paragraphs/sections
                            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 40]
                            for idx, para in enumerate(paragraphs):
                                self.documents.append({
                                    "doc_id": f"{file}#chunk{idx+1}",
                                    "source": file,
                                    "section": f"Chunk {idx+1}",
                                    "content": para
                                })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

        # Compute TF-IDF Index for retrieved chunks
        self._build_tfidf_index()

    def _build_tfidf_index(self):
        if not self.documents:
            return

        doc_count = len(self.documents)
        df: Dict[str, int] = {}
        doc_tokens_list = []

        for doc in self.documents:
            tokens = set(self._tokenize(doc["content"]))
            doc_tokens_list.append(self._tokenize(doc["content"]))
            for t in tokens:
                df[t] = df.get(t, 0) + 1

        self.idf = {term: math.log((doc_count + 1) / (freq + 1)) + 1.0 for term, freq in df.items()}
        self.doc_vectors = []

        for tokens in doc_tokens_list:
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            
            vec = {}
            norm_sq = 0.0
            for term, count in tf.items():
                w = (count / len(tokens)) * self.idf.get(term, 1.0)
                vec[term] = w
                norm_sq += w * w
            
            norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
            vec = {k: v / norm for k, v in vec.items()}
            self.doc_vectors.append(vec)

    def retrieve(self, query: str, top_k: int = 3, threshold: float = 0.08) -> List[Dict[str, Any]]:
        """Cosine similarity retrieval against indexed chunks with similarity scores."""
        q_tokens = self._tokenize(query)
        if not q_tokens or not self.doc_vectors:
            return []

        q_tf: Dict[str, int] = {}
        for t in q_tokens:
            q_tf[t] = q_tf.get(t, 0) + 1

        q_vec = {}
        norm_sq = 0.0
        for term, count in q_tf.items():
            w = (count / len(q_tokens)) * self.idf.get(term, 1.0)
            q_vec[term] = w
            norm_sq += w * w
        q_norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        q_vec = {k: v / q_norm for k, v in q_vec.items()}

        scores = []
        for idx, d_vec in enumerate(self.doc_vectors):
            dot = sum(q_vec[t] * d_vec.get(t, 0.0) for t in q_vec)
            if dot >= threshold:
                scores.append((dot, self.documents[idx]))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scores[:top_k]:
            results.append({
                "source": doc["source"],
                "section": doc["section"],
                "content": doc["content"],
                "similarity_score": round(float(score), 4)
            })
        return results

    async def generate_response(
        self,
        query: str,
        skill_context: Optional[str] = None,
        hint_step: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Coordinates retrieval, prompt grounding, Ollama query, and deterministic fallback.
        """
        retrieved_passages = self.retrieve(query, top_k=3)
        context_str = "\n\n".join(
            [f"Source [{p['source']} - {p['section']}]: {p['content']}" for p in retrieved_passages]
        )

        hint_instructions = ""
        if hint_step == 1:
            hint_instructions = "HINT LEVEL 1 (Conceptual Hint): Explain the core idea without giving code."
        elif hint_step == 2:
            hint_instructions = "HINT LEVEL 2 (Specific Hint): Identify the specific library function or control structure to consider."
        elif hint_step == 3:
            hint_instructions = "HINT LEVEL 3 (Guided Reasoning): Provide pseudo-code logic or step-by-step thinking questions."
        elif hint_step == 4:
            hint_instructions = "HINT LEVEL 4 (Worked Example): Show an analogous small code snippet, but do not solve their exact homework."

        system_prompt = (
            "You are MERIDIAN AI Learning Assistant. You help students understand concepts through graduated hints "
            "and grounded technical explanations. AI assistance helps learning, but independent mastery must be proven separately. "
            "Always cite the provided sources if you use information from them. Never make up citations.\n"
            f"{hint_instructions}\n\n"
            f"REFERENCE KNOWLEDGE CONTEXT:\n{context_str if context_str else 'No specific textbook passage found.'}"
        )

        # Attempt local Ollama inference
        ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                res = await client.post(
                    ollama_url,
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": f"System: {system_prompt}\n\nUser Question: {query}\n\nAssistant:",
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    reply = data.get("response", "").strip()
                    return {
                        "reply": reply,
                        "is_fallback": False,
                        "model_used": settings.OLLAMA_MODEL,
                        "source_citations": [
                            {"source": p["source"], "section": p["section"]} for p in retrieved_passages
                        ],
                        "retrieved_passages": retrieved_passages
                    }
        except Exception as e:
            # Ollama not reachable or model not responding: use deterministic fallback
            pass

        # Deterministic offline fallback engine
        fallback_reply = self._build_deterministic_fallback(query, retrieved_passages, hint_step)
        return {
            "reply": fallback_reply,
            "is_fallback": True,
            "model_used": "Deterministic Rule-Based Knowledge Engine (Offline)",
            "source_citations": [
                {"source": p["source"], "section": p["section"]} for p in retrieved_passages
            ],
            "retrieved_passages": retrieved_passages
        }

    def _build_deterministic_fallback(
        self,
        query: str,
        retrieved: List[Dict[str, Any]],
        hint_step: Optional[int]
    ) -> str:
        intro = "[DETERMINISTIC FALLBACK MODE: Local Ollama service is currently idle/unreachable. Response generated deterministically from local indexed repository.]\n\n"
        if not retrieved:
            return intro + (
                "MERIDIAN Knowledge Engine: No matching local textbook chunks were found with sufficient similarity for your query. "
                "Try searching for specific technical concepts such as 'loops', 'classes', 'FastAPI routes', or 'HTML DOM'."
            )

        top_chunk = retrieved[0]
        step_text = f"Guided Step {hint_step or 1}: "
        return (
            f"{intro}{step_text}Based on verified reference material in **{top_chunk['source']}** ({top_chunk['section']}):\n\n"
            f"> \"{top_chunk['content']}\"\n\n"
            f"**Key Takeaway**: Apply this concept to your current task by verifying your preconditions and control flow step by step. "
            f"Review the citations below for full documentation."
        )

rag_pipeline = RAGPipeline()
