const API_BASE = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
  ? (window.location.port === "5173" ? "http://localhost:8000/api/v1" : "/api/v1")
  : "/api/v1";

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  target_role: string;
  is_instructor: boolean;
}

export interface SkillEvidence {
  id: number;
  skill_id: string;
  skill_name: string;
  status: 'unassessed' | 'needs_development' | 'developing' | 'demonstrated_assisted' | 'demonstrated_independently';
  mastery_score: number;
  assisted_attempts_count: number;
  independent_attempts_count: number;
  evidence_notes: string;
}

export interface AssessmentTask {
  id: string;
  role_name: string;
  skill_id: string;
  title: string;
  task_type: string;
  prompt: string;
  instructions: string;
  initial_code_or_template: string;
  is_independent: boolean;
  hints_available: string[];
}

export interface Recommendation {
  id: number;
  skill_id: string;
  title: string;
  recommendation_type: string;
  priority: string;
  rationale: string;
  fired_rule_id: string;
}

export interface ChatResponse {
  reply: string;
  is_fallback: boolean;
  model_used: string;
  source_citations: { source: string; section: string }[];
  retrieved_passages: { source: string; section: string; content: string; similarity_score: number }[];
}

export interface AgentRunOut {
  run_id: number;
  goal: string;
  status: string;
  state_history: {
    step: number;
    state: string;
    decision: string;
    tool_called: string;
    [key: string]: any;
  }[];
  final_output: any;
  execution_time_ms: number;
}

export const api = {
  getAuthHeader: (): Record<string, string> => {
    const token = localStorage.getItem("meridian_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  login: async (username_or_email: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_email, password }),
    });
    if (!res.ok) throw new Error("Invalid login credentials");
    return res.json();
  },

  getMe: async (): Promise<User> => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: api.getAuthHeader(),
    });
    if (!res.ok) throw new Error("Unauthorized");
    return res.json();
  },

  updateTargetRole: async (role_name: string): Promise<User> => {
    const res = await fetch(`${API_BASE}/auth/target-role?role_name=${encodeURIComponent(role_name)}`, {
      method: "PUT",
      headers: api.getAuthHeader(),
    });
    return res.json();
  },

  getEvidence: async (): Promise<SkillEvidence[]> => {
    const res = await fetch(`${API_BASE}/skills/evidence`, {
      headers: api.getAuthHeader(),
    });
    return res.json();
  },

  getTasks: async (role_name?: string): Promise<AssessmentTask[]> => {
    const url = role_name 
      ? `${API_BASE}/assessments/tasks?role_name=${encodeURIComponent(role_name)}`
      : `${API_BASE}/assessments/tasks`;
    const res = await fetch(url);
    return res.json();
  },

  submitAssessment: async (data: {
    task_id: string;
    submission_text: string;
    hints_used: number;
    time_taken_seconds: number;
  }) => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...api.getAuthHeader()
    };
    const res = await fetch(`${API_BASE}/assessments/submit`, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
    return res.json();
  },

  getRecommendations: async (): Promise<Recommendation[]> => {
    const res = await fetch(`${API_BASE}/recommendations`, {
      headers: api.getAuthHeader(),
    });
    return res.json();
  },

  exploreRules: async () => {
    const res = await fetch(`${API_BASE}/rules/explore`, {
      headers: api.getAuthHeader(),
    });
    return res.json();
  },

  chatQuery: async (message: string, hint_step?: number): Promise<ChatResponse> => {
    const res = await fetch(`${API_BASE}/chat/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, hint_step }),
    });
    return res.json();
  },

  runAgent: async (goal?: string): Promise<AgentRunOut> => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...api.getAuthHeader()
    };
    const res = await fetch(`${API_BASE}/agent/run`, {
      method: "POST",
      headers,
      body: JSON.stringify({ goal }),
    });
    return res.json();
  },

  runPractical: async (id: number, param?: string) => {
    const url = param 
      ? `${API_BASE}/algorithms/practical/${id}?param=${encodeURIComponent(param)}`
      : `${API_BASE}/algorithms/practical/${id}`;
    const res = await fetch(url);
    return res.json();
  },
};
