import { useState, useEffect } from 'react';
import { api } from './api';
import type { User, SkillEvidence, AssessmentTask, Recommendation, AgentRunOut } from './api';
import { 
  CheckCircle, AlertCircle, Compass, Cpu, 
  HelpCircle, ShieldCheck, Play, ArrowRight
} from 'lucide-react';

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [evidence, setEvidence] = useState<SkillEvidence[]>([]);
  const [tasks, setTasks] = useState<AssessmentTask[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'assessments' | 'ai_assistant' | 'agent' | 'rules'>('dashboard');
  const [loading, setLoading] = useState(false);

  // Chat State
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [selectedHintLevel, setSelectedHintLevel] = useState<number>(1);

  // Assessment Workbench State
  const [selectedTask, setSelectedTask] = useState<AssessmentTask | null>(null);
  const [submissionCode, setSubmissionCode] = useState('');
  const [hintsUsedCount, setHintsUsedCount] = useState(0);
  const [revealedHints, setRevealedHints] = useState<string[]>([]);
  const [assessmentFeedback, setAssessmentFeedback] = useState<any>(null);

  // Agent State
  const [agentRun, setAgentRun] = useState<AgentRunOut | null>(null);
  const [agentRunning, setAgentRunning] = useState(false);

  // Rules Explorer State
  const [rulesAudit, setRulesAudit] = useState<any>(null);

  // Auto-login synthetic demo student on initial mount
  useEffect(() => {
    initDemoSession();
  }, []);

  const initDemoSession = async () => {
    try {
      setLoading(true);
      const loginRes = await api.login('student_demo', 'meridian2026');
      localStorage.setItem('meridian_token', loginRes.access_token);
      setUser(loginRes.user);
      await refreshData();
    } catch (e) {
      console.error("Auth init error:", e);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    try {
      const [ev, recs, t] = await Promise.all([
        api.getEvidence(),
        api.getRecommendations(),
        api.getTasks()
      ]);
      setEvidence(ev);
      setRecommendations(recs);
      setTasks(t);
      if (t.length > 0 && !selectedTask) {
        setSelectedTask(t[0]);
        setSubmissionCode(t[0].initial_code_or_template || '');
      }
    } catch (err) {
      console.error("Refresh error:", err);
    }
  };

  const handleRoleChange = async (newRole: string) => {
    if (!user) return;
    setLoading(true);
    await api.updateTargetRole(newRole);
    setUser({ ...user, target_role: newRole });
    await refreshData();
    setLoading(false);
  };

  const handleRevealHint = () => {
    if (!selectedTask) return;
    if (selectedTask.is_independent) {
      alert("HINTS DISABLED: This is an Independent Verification assessment. No AI assistance or hints are permitted.");
      return;
    }
    if (hintsUsedCount < selectedTask.hints_available.length) {
      const nextHint = selectedTask.hints_available[hintsUsedCount];
      setRevealedHints([...revealedHints, nextHint]);
      setHintsUsedCount(hintsUsedCount + 1);
    }
  };

  const handleSubmitAssessment = async () => {
    if (!selectedTask) return;
    setLoading(true);
    try {
      const res = await api.submitAssessment({
        task_id: selectedTask.id,
        submission_text: submissionCode,
        hints_used: hintsUsedCount,
        time_taken_seconds: 45
      });
      setAssessmentFeedback(res);
      await refreshData();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim()) return;
    const userMsg = { role: 'user', content: chatInput };
    setChatMessages([...chatMessages, userMsg]);
    setChatInput('');
    try {
      const res = await api.chatQuery(chatInput, selectedHintLevel);
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: res.reply,
        is_fallback: res.is_fallback,
        citations: res.source_citations,
        model: res.model_used
      }]);
    } catch (e) {
      console.error(e);
    }
  };

  const handleTriggerAgent = async () => {
    setAgentRunning(true);
    try {
      const res = await api.runAgent("Formulate optimal next milestone based on current weaknesses");
      setAgentRun(res);
      await refreshData();
    } catch (e) {
      console.error(e);
    } finally {
      setAgentRunning(false);
    }
  };

  const handleLoadRulesAudit = async () => {
    try {
      const data = await api.exploreRules();
      setRulesAudit(data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded bg-teal-600 flex items-center justify-center font-bold text-slate-950 text-lg">
            M
          </div>
          <div>
            <div className="font-semibold text-lg text-slate-100 tracking-tight flex items-center space-x-2">
              <span>MERIDIAN</span>
              <span className="text-xs bg-teal-950 text-teal-300 border border-teal-800 px-2 py-0.5 rounded">Student Edition</span>
            </div>
            <p className="text-xs text-slate-400">Learn intelligently. Demonstrate independently.</p>
          </div>
        </div>

        {/* Global Navigation Tabs */}
        <nav className="flex space-x-1">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: Compass },
            { id: 'assessments', label: 'Assessment Workbench', icon: CheckCircle },
            { id: 'ai_assistant', label: 'AI Assistant & RAG', icon: HelpCircle },
            { id: 'agent', label: 'Bounded Agent', icon: Cpu },
            { id: 'rules', label: 'Rule Explorer', icon: ShieldCheck },
          ].map(tab => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id as any);
                  if (tab.id === 'rules') handleLoadRulesAudit();
                }}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition ${
                  active 
                    ? 'bg-teal-600 text-slate-950 shadow-sm font-semibold' 
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Icon size={14} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* User Pill */}
        <div className="flex items-center space-x-3">
          {user && (
            <div className="text-right">
              <div className="text-xs font-medium text-slate-200">{user.full_name}</div>
              <div className="text-[10px] text-teal-400 font-mono">{user.target_role}</div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {/* ===================== TAB: DASHBOARD ===================== */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Target Role Selector Banner */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-slate-100">Target Role Roadmap</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Skill maps, prerequisites, and automated recommendations adapt to your selected technical role.
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-slate-400">Current Role:</span>
                <select 
                  value={user?.target_role || "Junior Python Developer"} 
                  onChange={(e) => handleRoleChange(e.target.value)}
                  className="bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded px-3 py-1.5 focus:outline-none focus:border-teal-500"
                >
                  <option value="Junior Python Developer">Junior Python Developer</option>
                  <option value="Junior Java Developer">Junior Java Developer</option>
                  <option value="Entry-Level Web Developer">Entry-Level Web Developer</option>
                </select>
              </div>
            </div>

            {/* Core Principle Callout */}
            <div className="bg-slate-900/60 border border-teal-900/60 rounded-lg p-4 flex items-start space-x-3">
              <ShieldCheck className="text-teal-400 shrink-0 mt-0.5" size={18} />
              <div className="text-xs text-slate-300 leading-relaxed">
                <strong className="text-teal-300">Meridian Core Principle:</strong> AI assistance helps learning, but it must not be treated as proof that a student independently possesses a skill. Tasks completed with hints receive <span className="text-amber-300 font-mono">demonstrated_assisted</span> and require a fresh, unassisted reassessment for <span className="text-teal-300 font-mono">demonstrated_independently</span> certification.
              </div>
            </div>

            {/* Competency Gap Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 md:col-span-2">
                <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center justify-between">
                  <span>Assessed Competency Matrix</span>
                  <span className="text-[11px] text-slate-400 font-normal">Real Persistent Evidence</span>
                </h3>
                <div className="space-y-3">
                  {evidence.map(item => {
                    const statusColors = {
                      unassessed: 'text-slate-400 border-slate-700 bg-slate-800',
                      needs_development: 'text-rose-400 border-rose-900/50 bg-rose-950/20',
                      developing: 'text-amber-400 border-amber-900/50 bg-amber-950/20',
                      demonstrated_assisted: 'text-sky-400 border-sky-900/50 bg-sky-950/20',
                      demonstrated_independently: 'text-teal-400 border-teal-900/50 bg-teal-950/20'
                    };
                    return (
                      <div key={item.id} className="border border-slate-800/80 bg-slate-950/50 rounded p-3 flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
                        <div>
                          <div className="text-xs font-medium text-slate-200">{item.skill_name}</div>
                          <div className="text-[11px] text-slate-400 mt-0.5">{item.evidence_notes}</div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`text-[10px] font-mono border px-2 py-0.5 rounded uppercase tracking-wider ${statusColors[item.status]}`}>
                            {item.status.replace('_', ' ')}
                          </span>
                          <span className="text-xs font-semibold text-slate-300 font-mono w-12 text-right">
                            {item.mastery_score}%
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Explainable Recommendations Panel */}
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center justify-between">
                    <span>Active Recommendations</span>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">Rule Engine</span>
                  </h3>
                  {recommendations.length === 0 ? (
                    <div className="text-xs text-slate-500 py-6 text-center">No active remediation rules fired.</div>
                  ) : (
                    <div className="space-y-3">
                      {recommendations.map(rec => (
                        <div key={rec.id} className="border border-slate-800 bg-slate-950 p-3 rounded">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-mono text-teal-400">{rec.fired_rule_id}</span>
                            <span className="text-[10px] uppercase font-semibold text-rose-400 bg-rose-950/40 px-1 rounded">{rec.priority}</span>
                          </div>
                          <h4 className="text-xs font-medium text-slate-200 mt-1">{rec.title}</h4>
                          <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{rec.rationale}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => setActiveTab('assessments')}
                  className="mt-4 w-full bg-slate-800 hover:bg-slate-700 text-xs font-medium py-2 rounded text-slate-200 transition flex items-center justify-center space-x-1"
                >
                  <span>Go to Assessment Workbench</span>
                  <ArrowRight size={13} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ===================== TAB: ASSESSMENTS ===================== */}
        {activeTab === 'assessments' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Task List */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">Available Tasks</h3>
              {tasks.map(t => {
                const isSelected = selectedTask?.id === t.id;
                return (
                  <div
                    key={t.id}
                    onClick={() => {
                      setSelectedTask(t);
                      setSubmissionCode(t.initial_code_or_template || '');
                      setHintsUsedCount(0);
                      setRevealedHints([]);
                      setAssessmentFeedback(null);
                    }}
                    className={`cursor-pointer border rounded-lg p-3 transition ${
                      isSelected ? 'border-teal-600 bg-slate-900' : 'border-slate-800 bg-slate-950 hover:bg-slate-900/60'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded ${
                        t.is_independent ? 'bg-amber-950 text-amber-300 border border-amber-800' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {t.is_independent ? 'Independent (No Hints)' : 'Assisted Practice'}
                      </span>
                      <span className="text-[10px] text-slate-500">{t.role_name}</span>
                    </div>
                    <div className="text-xs font-medium text-slate-200 mt-2">{t.title}</div>
                  </div>
                );
              })}
            </div>

            {/* Code / Response Workbench */}
            <div className="md:col-span-2 space-y-4">
              {selectedTask ? (
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h3 className="text-sm font-semibold text-slate-100">{selectedTask.title}</h3>
                      <p className="text-xs text-slate-400 mt-0.5">{selectedTask.instructions}</p>
                    </div>
                    {selectedTask.is_independent ? (
                      <span className="text-xs bg-rose-950 border border-rose-800 text-rose-300 px-2 py-1 rounded font-mono">
                        STRICT UNASSISTED EVALUATION
                      </span>
                    ) : (
                      <button
                        onClick={handleRevealHint}
                        disabled={hintsUsedCount >= selectedTask.hints_available.length}
                        className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded transition disabled:opacity-40"
                      >
                        Request Graduated Hint ({hintsUsedCount}/{selectedTask.hints_available.length})
                      </button>
                    )}
                  </div>

                  {/* Task Prompt */}
                  <div className="bg-slate-950 border border-slate-800 p-3 rounded text-xs text-slate-300 font-mono leading-relaxed">
                    {selectedTask.prompt}
                  </div>

                  {/* Revealed Hints */}
                  {revealedHints.length > 0 && (
                    <div className="space-y-2">
                      {revealedHints.map((hint, idx) => (
                        <div key={idx} className="bg-amber-950/30 border border-amber-900/50 p-2.5 rounded text-xs text-amber-200 flex items-start space-x-2">
                          <AlertCircle size={14} className="mt-0.5 shrink-0 text-amber-400" />
                          <div>
                            <strong>Hint Level {idx + 1}:</strong> {hint}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Code Editor Area */}
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">Submission Workspace (Deterministic Rubric Evaluation):</label>
                    <textarea
                      value={submissionCode}
                      onChange={(e) => setSubmissionCode(e.target.value)}
                      rows={9}
                      className="w-full bg-slate-950 border border-slate-800 rounded p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-teal-500"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500">
                      Hints used: <strong className="text-slate-300">{hintsUsedCount}</strong>
                    </span>
                    <button
                      onClick={handleSubmitAssessment}
                      disabled={loading}
                      className="bg-teal-600 hover:bg-teal-500 text-slate-950 font-semibold px-4 py-2 rounded text-xs transition"
                    >
                      {loading ? 'Evaluating...' : 'Submit Assessment'}
                    </button>
                  </div>

                  {/* Evaluation Result Banner */}
                  {assessmentFeedback && (
                    <div className="mt-4 border border-teal-900/80 bg-teal-950/30 p-4 rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-teal-300">
                          {assessmentFeedback.message}
                        </span>
                        <span className="text-xs font-mono font-bold text-teal-400">
                          Score: {assessmentFeedback.score_percentage}%
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-300">
                        Updated State: <strong className="font-mono text-teal-200">{assessmentFeedback.new_skill_status}</strong>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-xs text-slate-500 p-8 border border-slate-800 rounded text-center">Select an assessment task to begin.</div>
              )}
            </div>
          </div>
        )}

        {/* ===================== TAB: AI ASSISTANT & RAG ===================== */}
        {activeTab === 'ai_assistant' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 bg-slate-900 border border-slate-800 rounded-lg flex flex-col h-[520px]">
              <div className="border-b border-slate-800 p-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-100">Grounded AI Learning Assistant</h3>
                  <p className="text-xs text-slate-400">Local RAG pipeline retrieving verified textbook passages with zero external API cost.</p>
                </div>
                {/* Hint Level Selector */}
                <div className="flex items-center space-x-1">
                  <span className="text-xs text-slate-400">Policy:</span>
                  <select
                    value={selectedHintLevel}
                    onChange={(e) => setSelectedHintLevel(Number(e.target.value))}
                    className="bg-slate-950 border border-slate-700 text-xs text-slate-300 rounded px-2 py-1"
                  >
                    <option value={1}>Hint 1: Conceptual</option>
                    <option value={2}>Hint 2: Specific</option>
                    <option value={3}>Hint 3: Guided Reasoning</option>
                    <option value={4}>Hint 4: Worked Example</option>
                  </select>
                </div>
              </div>

              {/* Chat Thread */}
              <div className="flex-1 p-4 overflow-y-auto space-y-3">
                {chatMessages.length === 0 && (
                  <div className="text-xs text-slate-500 text-center py-12">
                    Ask a technical question about Python OOP, FastAPI architecture, Java loops, or algorithmic principles.
                  </div>
                )}
                {chatMessages.map((m, idx) => (
                  <div key={idx} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`max-w-[85%] rounded-lg p-3 text-xs leading-relaxed ${
                      m.role === 'user' 
                        ? 'bg-teal-900 text-teal-100' 
                        : 'bg-slate-950 border border-slate-800 text-slate-200'
                    }`}>
                      <div className="whitespace-pre-wrap">{m.content}</div>

                      {/* Source Citations */}
                      {m.citations && m.citations.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-800 text-[10px] text-teal-400">
                          <strong>Citations: </strong>
                          {m.citations.map((c: any, cIdx: number) => (
                            <span key={cIdx} className="bg-slate-900 px-1 py-0.5 rounded mr-1">
                              [{c.source} - {c.section}]
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Model & Fallback Badge */}
                      {m.model && (
                        <div className="mt-1 text-[9px] text-slate-500 font-mono">
                          Source: {m.model} {m.is_fallback ? '(Offline Fallback)' : ''}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Input Area */}
              <div className="border-t border-slate-800 p-3 flex space-x-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                  placeholder="Ask a technical question regarding syllabus topics or tasks..."
                  className="flex-1 bg-slate-950 border border-slate-800 rounded px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                />
                <button
                  onClick={handleSendChat}
                  className="bg-teal-600 hover:bg-teal-500 text-slate-950 font-semibold px-4 py-2 rounded text-xs transition"
                >
                  Send
                </button>
              </div>
            </div>

            {/* Local Knowledge Base Docs Panel */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">Indexed Local Documents</h3>
              <p className="text-xs text-slate-400">
                All RAG passages are stored on disk in <code className="text-teal-300 font-mono text-[10px]">data/knowledge_base</code>. No data is transmitted to third-party cloud APIs.
              </p>
              <div className="space-y-2 pt-2">
                {[
                  { title: "Python OOP Guide", file: "python_oop_guide.md", topic: "Classes, Inheritance, Encapsulation" },
                  { title: "FastAPI Architecture", file: "fastapi_architecture.md", topic: "REST, Pydantic, Dependency Injection" },
                  { title: "Java Core Principles", file: "java_core_principles.md", topic: "Loops, Arrays, Memory layout" }
                ].map((doc, i) => (
                  <div key={i} className="border border-slate-800 bg-slate-950 p-2.5 rounded">
                    <div className="text-xs font-medium text-slate-200">{doc.title}</div>
                    <div className="text-[10px] font-mono text-teal-400">{doc.file}</div>
                    <div className="text-[10px] text-slate-500 mt-1">{doc.topic}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===================== TAB: BOUNDED AGENT ===================== */}
        {activeTab === 'agent' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h3 className="text-sm font-semibold text-slate-100">Observable Bounded Agent Workflow</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Constrained finite state machine with strictly allowlisted tools. Inspect decisions at each discrete step.
                </p>
              </div>
              <button
                onClick={handleTriggerAgent}
                disabled={agentRunning}
                className="bg-teal-600 hover:bg-teal-500 text-slate-950 font-semibold px-4 py-2 rounded text-xs transition flex items-center space-x-1.5"
              >
                <Play size={14} />
                <span>{agentRunning ? 'Executing Workflow...' : 'Execute Bounded Agent'}</span>
              </button>
            </div>

            {agentRun && (
              <div className="space-y-4">
                <div className="flex items-center space-x-4 text-xs font-mono text-slate-400 bg-slate-900 p-3 rounded border border-slate-800">
                  <span>Status: <strong className="text-teal-300">{agentRun.status}</strong></span>
                  <span>Execution Time: <strong className="text-slate-200">{agentRun.execution_time_ms} ms</strong></span>
                  <span>Steps Taken: <strong className="text-slate-200">{agentRun.state_history.length}</strong></span>
                </div>

                {/* State History Timeline */}
                <div className="border border-slate-800 bg-slate-900/60 rounded-lg p-4 space-y-3">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Finite State Transition Trace</h4>
                  <div className="space-y-2">
                    {agentRun.state_history.map(s => (
                      <div key={s.step} className="bg-slate-950 border border-slate-800 p-3 rounded flex flex-col md:flex-row md:items-center justify-between gap-2">
                        <div className="flex items-center space-x-3">
                          <span className="h-5 w-5 rounded bg-slate-800 text-slate-300 flex items-center justify-center font-mono text-[10px] font-bold">
                            {s.step}
                          </span>
                          <div>
                            <span className="text-xs font-mono text-teal-400 font-semibold">{s.state}</span>
                            <div className="text-xs text-slate-300 mt-0.5">{s.decision}</div>
                          </div>
                        </div>
                        <div className="text-[10px] font-mono text-slate-500 bg-slate-900 px-2 py-1 rounded">
                          Tool: {s.tool_called}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ===================== TAB: RULE EXPLORER ===================== */}
        {activeTab === 'rules' && (
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-100">Rule Engine Inspector</h3>
                <p className="text-xs text-slate-400">Forward chaining rule evaluation and conflict resolution trace.</p>
              </div>
              <button
                onClick={handleLoadRulesAudit}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded transition"
              >
                Re-evaluate Facts
              </button>
            </div>

            {rulesAudit && (
              <div className="space-y-3">
                {rulesAudit.audit_trail?.map((item: any) => (
                  <div key={item.rule_id} className={`border rounded-lg p-3 ${
                    item.fired ? 'border-teal-800/80 bg-teal-950/20' : 'border-slate-800/60 bg-slate-950/40 opacity-70'
                  }`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className={`h-2 w-2 rounded-full ${item.fired ? 'bg-teal-400' : 'bg-slate-600'}`} />
                        <span className="text-xs font-mono font-medium text-slate-200">{item.rule_id}</span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">Priority: {item.priority}</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1">{item.description}</p>
                    <div className="text-[10px] font-mono mt-2 text-slate-400">
                      Outcome: <strong className={item.fired ? 'text-teal-300' : 'text-slate-500'}>{item.fired ? 'FIRED' : 'DID NOT FIRE'}</strong> — {item.reason}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
