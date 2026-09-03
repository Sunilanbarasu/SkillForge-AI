import React, { useState } from 'react';
import {
  startAssessment,
  submitAssessment,
  getAssessmentHistory,
  getAssessmentResult,
  generateAIAnalysis,
  generateStudyPlan,
  getCurrentStudyPlan,
  updateTaskStatus
} from '../api/client';

export function Assessment() {
  const [viewState, setViewState] = useState('start'); // 'start', 'taking', 'results', 'history'
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [planLoading, setPlanLoading] = useState(false);
  const [studyPlan, setStudyPlan] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  
  // Active Assessment State
  const [assessmentId, setAssessmentId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  // Result State
  const [resultData, setResultData] = useState(null);
  const [aiData, setAiData] = useState(null);

  // History State
  const [historyList, setHistoryList] = useState([]);

  const handleStartTest = async () => {
    setLoading(true);
    setErrorMsg('');
    setAiData(null);
    const res = await startAssessment();
    setLoading(false);

    if (res.success) {
      setAssessmentId(res.data.assessment_id);
      setQuestions(res.data.questions);
      setCurrentIndex(0);
      setUserAnswers({});
      setViewState('taking');
    } else {
      setErrorMsg(res.error);
    }
  };

  const handleSelectOption = (qId, optionKey) => {
    setUserAnswers(prev => ({
      ...prev,
      [qId]: optionKey
    }));
  };

  const handleConfirmSubmit = async () => {
    setShowConfirmModal(false);
    setLoading(true);
    setErrorMsg('');

    const answersList = questions.map(q => ({
      question_id: q.id,
      selected_answer: userAnswers[q.id] || 'A'
    }));

    const res = await submitAssessment(assessmentId, answersList);
    setLoading(false);

    if (res.success) {
      setResultData(res.data);
      setAiData(null);
      setViewState('results');
    } else {
      setErrorMsg(res.error);
    }
  };

  const handleGenerateAI = async () => {
    if (!resultData?.id) return;
    setAiLoading(true);
    setErrorMsg('');

    const res = await generateAIAnalysis(resultData.id);
    setAiLoading(false);

    if (res.success) {
      setAiData(res.data);
    } else {
      setErrorMsg(res.error);
    }
  };

  const handleGenerateStudyPlan = async () => {
    setPlanLoading(true);
    setErrorMsg('');

    const res = await generateStudyPlan();
    setPlanLoading(false);

    if (res.success) {
      setStudyPlan(res.data);
    } else {
      setErrorMsg(res.error);
    }
  };

  const loadStudyPlan = async () => {
    const res = await getCurrentStudyPlan();
    if (res.success) {
      setStudyPlan(res.data);
    }
  };

  const handleTaskToggle = async (taskId, currentStatus) => {
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    const res = await updateTaskStatus(taskId, newStatus);
    if (res.success) {
      setStudyPlan(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          tasks: prev.tasks.map(t => t.id === taskId ? res.data : t)
        };
      });
    } else {
      setErrorMsg(res.error);
    }
  };

  const loadHistory = async () => {
    setLoading(true);
    setErrorMsg('');
    const res = await getAssessmentHistory();
    setLoading(false);
    if (res.success) {
      setHistoryList(res.data);
      setViewState('history');
    } else {
      setErrorMsg(res.error);
    }
  };

  const viewPastResult = async (pastId) => {
    setLoading(true);
    setErrorMsg('');
    setAiData(null);
    const res = await getAssessmentResult(pastId);
    setLoading(false);
    if (res.success) {
      setResultData(res.data);
      setViewState('results');
    } else {
      setErrorMsg(res.error);
    }
  };

  const currentQ = questions[currentIndex];
  const answeredCount = Object.keys(userAnswers).length;
  const progressPercent = questions.length > 0 ? Math.round(((currentIndex + 1) / questions.length) * 100) : 0;

  return (
    <div style={{ maxWidth: '920px', margin: '1.5rem auto' }}>

      {/* Navigation Sub-header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Placement Diagnostic Assessment
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            Evaluate your readiness across Python, C, DSA, SQL, OOP, DBMS, and Aptitude.
          </p>
        </div>
        {viewState !== 'taking' && (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => setViewState('start')}
              className="btn"
              style={{ backgroundColor: viewState === 'start' ? '#334155' : 'transparent', color: '#fff' }}
            >
              Take Assessment
            </button>
            <button
              onClick={loadHistory}
              className="btn"
              style={{ backgroundColor: viewState === 'history' ? '#334155' : 'transparent', color: '#fff' }}
            >
              Assessment History
            </button>
          </div>
        )}
      </div>

      {errorMsg && (
        <div style={{
          backgroundColor: 'var(--status-error-bg)',
          border: '1px solid var(--status-error)',
          color: '#fca5a5',
          padding: '0.875rem 1rem',
          borderRadius: '8px',
          fontSize: '0.875rem',
          marginBottom: '1.5rem'
        }}>
          {errorMsg}
        </div>
      )}

      {/* VIEW 1: START SCREEN */}
      {viewState === 'start' && (
        <div className="card" style={{ padding: '2rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>
            Placement Readiness Diagnostic Test
          </h3>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '1.5rem' }}>
            This placement test evaluates your skills across 35 curated computer science and aptitude questions. 
            Once completed, your scores are calculated server-side and interpreted by SkillForge AI to map your skill gaps.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            {["Python", "C", "DSA", "SQL", "OOP", "DBMS", "Aptitude"].map(skill => (
              <div key={skill} style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <div style={{ fontWeight: 600, color: 'var(--accent-primary)', fontSize: '0.9375rem' }}>{skill}</div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>5 Diagnostic Questions</div>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #334155', paddingTop: '1.5rem' }}>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              Total Questions: <strong>35</strong> | Server-Side Evaluated
            </div>
            <button onClick={handleStartTest} disabled={loading} className="btn btn-primary" style={{ padding: '0.75rem 1.75rem', fontSize: '1rem' }}>
              {loading ? 'Initializing Assessment...' : 'Start Assessment Now'}
            </button>
          </div>
        </div>
      )}

      {/* VIEW 2: TAKING ASSESSMENT */}
      {viewState === 'taking' && currentQ && (
        <div className="card" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <span className="badge badge-warning" style={{ fontSize: '0.8125rem' }}>
              {currentQ.skill} • {currentQ.difficulty}
            </span>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)', fontWeight: 500 }}>
              Question {currentIndex + 1} of {questions.length} (Answered: {answeredCount}/{questions.length})
            </span>
          </div>

          <div style={{ width: '100%', height: '6px', backgroundColor: '#0f172a', borderRadius: '4px', overflow: 'hidden', marginBottom: '1.5rem' }}>
            <div style={{ width: `${progressPercent}%`, height: '100%', backgroundColor: 'var(--accent-primary)', transition: 'width 0.3s ease' }} />
          </div>

          <h3 style={{ fontSize: '1.1875rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1.5rem', lineHeight: '1.5' }}>
            {currentQ.question_text}
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem' }}>
            {[
              { key: 'A', text: currentQ.option_a },
              { key: 'B', text: currentQ.option_b },
              { key: 'C', text: currentQ.option_c },
              { key: 'D', text: currentQ.option_d },
            ].map(opt => {
              const isSelected = userAnswers[currentQ.id] === opt.key;
              return (
                <div
                  key={opt.key}
                  onClick={() => handleSelectOption(currentQ.id, opt.key)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '0.875rem 1.25rem',
                    borderRadius: '8px',
                    border: isSelected ? '2px solid var(--accent-primary)' : '1px solid #334155',
                    backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.15)' : '#0f172a',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    border: isSelected ? 'none' : '1px solid #475569',
                    backgroundColor: isSelected ? 'var(--accent-primary)' : 'transparent',
                    color: '#fff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 600,
                    fontSize: '0.875rem'
                  }}>
                    {opt.key}
                  </div>
                  <div style={{ fontSize: '0.9375rem', color: isSelected ? '#fff' : 'var(--text-main)' }}>
                    {opt.text}
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #334155' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Question Navigator</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
              {questions.map((q, idx) => {
                const isAns = Boolean(userAnswers[q.id]);
                const isCurr = idx === currentIndex;
                return (
                  <button
                    key={q.id}
                    onClick={() => setCurrentIndex(idx)}
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '6px',
                      border: isCurr ? '2px solid #38bdf8' : 'none',
                      backgroundColor: isAns ? 'var(--accent-primary)' : '#1e293b',
                      color: '#fff',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="btn"
              style={{ backgroundColor: '#334155', color: '#fff' }}
            >
              Previous Question
            </button>

            {currentIndex < questions.length - 1 ? (
              <button
                onClick={() => setCurrentIndex(prev => Math.min(questions.length - 1, prev + 1))}
                className="btn btn-primary"
              >
                Next Question
              </button>
            ) : (
              <button
                onClick={() => setShowConfirmModal(true)}
                className="btn"
                style={{ backgroundColor: 'var(--status-success)', color: '#fff', fontWeight: 600 }}
              >
                Submit Assessment
              </button>
            )}
          </div>
        </div>
      )}

      {/* CONFIRMATION MODAL */}
      {showConfirmModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.75)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', zIndex: 9999
        }}>
          <div className="card" style={{ maxWidth: '440px', width: '90%', padding: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.75rem' }}>
              Confirm Assessment Submission
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              You have answered <strong>{answeredCount}</strong> out of <strong>{questions.length}</strong> questions. 
              Once submitted, your answers will be evaluated server-side.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowConfirmModal(false)} className="btn" style={{ backgroundColor: '#334155', color: '#fff' }}>
                Continue Test
              </button>
              <button onClick={handleConfirmSubmit} disabled={loading} className="btn btn-primary">
                {loading ? 'Calculating Results...' : 'Confirm & Submit'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 3: RESULTS SCREEN & AI ANALYSIS */}
      {viewState === 'results' && resultData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Result Card */}
          <div className="card" style={{ padding: '2rem' }}>
            <div style={{ borderBottom: '1px solid #334155', paddingBottom: '1.5rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span className="badge badge-success" style={{ marginBottom: '0.5rem' }}>Assessment Completed</span>
                <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Diagnostic Results & Skill Performance
                </h3>
              </div>
              <button
                onClick={handleGenerateAI}
                disabled={aiLoading}
                className="btn btn-primary"
                style={{ background: 'linear-gradient(135deg, #6366f1, #a855f7)', padding: '0.75rem 1.25rem', fontWeight: 600 }}
              >
                {aiLoading ? 'AI is analyzing your placement readiness...' : 'Analyze My Skills with AI ✨'}
              </button>
            </div>

            {/* Score Summary Header */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1.25rem',
              marginBottom: '2rem'
            }}>
              <div style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '10px', border: '1px solid #334155', textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Overall Score</div>
                <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#38bdf8', marginTop: '0.25rem' }}>
                  {resultData.overall_score}%
                </div>
              </div>

              <div style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '10px', border: '1px solid #334155', textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Correct Answers</div>
                <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--status-success)', marginTop: '0.25rem' }}>
                  {resultData.total_correct} / {resultData.total_questions}
                </div>
              </div>
            </div>

            {/* Skill-wise Performance Breakdown */}
            <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>
              Skill-Wise Performance Breakdown
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {(resultData.skill_scores || []).map(sk => {
                const isHigh = sk.score >= 70;
                const isMed = sk.score >= 50 && sk.score < 70;
                const barColor = isHigh ? 'var(--status-success)' : isMed ? 'var(--status-warning)' : 'var(--status-error)';
                
                return (
                  <div key={sk.skill} style={{ backgroundColor: '#0f172a', padding: '1rem 1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{sk.skill}</span>
                      <span style={{ fontWeight: 700, color: barColor }}>
                        {sk.score}% ({sk.correct_answers}/{sk.total_questions})
                      </span>
                    </div>
                    <div style={{ width: '100%', height: '8px', backgroundColor: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${sk.score}%`, height: '100%', backgroundColor: barColor, transition: 'width 0.4s ease' }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI LOADING STATE */}
          {aiLoading && (
            <div className="card" style={{ padding: '2.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#a855f7', marginBottom: '0.5rem' }}>
                AI is analyzing your placement readiness...
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                Mapping your PostgreSQL assessment scores to placement skill gaps, strengths, and recommended focus areas.
              </p>
            </div>
          )}

          {/* PLAN LOADING STATE */}
          {planLoading && (
            <div className="card" style={{ padding: '2.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.5rem' }}>
                SkillForge AI is crafting your personalized study plan...
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                Building a 4-week placement preparation plan focused on your weakest skills.
              </p>
            </div>
          )}

          {/* AI ANALYSIS SECTION */}
          {aiData && (
            <div className="card" style={{ padding: '2rem', border: '1px solid #818cf8' }}>
              <div style={{ borderBottom: '1px solid #334155', paddingBottom: '1.25rem', marginBottom: '1.5rem' }}>
                <span className="badge" style={{ backgroundColor: 'rgba(168, 85, 247, 0.2)', color: '#c084fc', border: '1px solid #c084fc', marginBottom: '0.5rem' }}>
                  SkillForge AI Insight Engine
                </span>
                <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  AI Skill-Gap & Placement Analysis
                </h3>
              </div>

              {/* Summary */}
              <div style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155', marginBottom: '1.75rem' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.5rem' }}>
                  Overall Analysis Summary
                </h4>
                <p style={{ color: 'var(--text-main)', lineHeight: '1.6', fontSize: '0.9375rem' }}>
                  {aiData.summary}
                </p>
              </div>

              {/* Strengths & Weaknesses Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.75rem' }}>
                {/* Strengths */}
                <div style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--status-success)', marginBottom: '0.75rem' }}>
                    Your Identified Strengths
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {(aiData.strengths || []).map((st, i) => (
                      <div key={i} style={{ borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem' }}>
                        <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.875rem' }}>{st.skill}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginTop: '0.25rem' }}>{st.reason}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Weaknesses */}
                <div style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--status-error)', marginBottom: '0.75rem' }}>
                    Areas Needing Improvement
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {(aiData.weaknesses || []).map((wk, i) => (
                      <div key={i} style={{ borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem' }}>
                        <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.875rem' }}>{wk.skill}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginTop: '0.25rem' }}>{wk.reason}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Skill Gaps & Focus Topics */}
              <div style={{ marginBottom: '1.75rem' }}>
                <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>
                  Skill Gaps & Targeted Focus Topics
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {(aiData.skill_gaps || []).map((gapItem, idx) => (
                    <div key={idx} style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ fontWeight: 600, color: '#a855f7', fontSize: '1rem' }}>{gapItem.skill}</span>
                        <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Identified Gap</span>
                      </div>
                      <p style={{ color: 'var(--text-main)', fontSize: '0.875rem', marginBottom: '0.75rem', lineHeight: '1.5' }}>
                        {gapItem.gap}
                      </p>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
                        {(gapItem.focus_topics || []).map((topic, ti) => (
                          <span key={ti} style={{
                            fontSize: '0.75rem', padding: '0.25rem 0.625rem', borderRadius: '9999px',
                            backgroundColor: '#1e293b', color: '#38bdf8', border: '1px solid #334155'
                          }}>
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Priority Areas */}
              <div style={{ marginBottom: '1.75rem' }}>
                <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>
                  Priority Prep Areas
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
                  {(aiData.priorities || []).map((pri, pi) => {
                    const isHigh = pri.priority?.toLowerCase() === 'high';
                    const isMed = pri.priority?.toLowerCase() === 'medium';
                    const badgeClass = isHigh ? 'badge-error' : isMed ? 'badge-warning' : 'badge-success';

                    return (
                      <div key={pi} style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                          <span style={{ fontWeight: 600, color: '#fff' }}>{pri.skill}</span>
                          <span className={`badge ${badgeClass}`}>{pri.priority} Priority</span>
                        </div>
                        <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{pri.reason}</div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Recommended Actions */}
              <div>
                <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>
                  Actionable Preparation Recommendations
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {(aiData.recommendations || []).map((rec, ri) => (
                    <div key={ri} style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                      <div style={{ fontWeight: 600, color: 'var(--accent-primary)', fontSize: '0.9375rem', marginBottom: '0.75rem' }}>
                        {rec.skill} Action Plan
                      </div>
                      <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-main)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                        {(rec.actions || []).map((act, ai) => (
                          <li key={ai} style={{ marginBottom: '0.375rem' }}>{act}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Create Study Plan Button */}
              <div style={{ borderTop: '1px solid #334155', marginTop: '1.75rem', paddingTop: '1.5rem', textAlign: 'center' }}>
                <button
                  onClick={handleGenerateStudyPlan}
                  disabled={planLoading}
                  className="btn btn-primary"
                  style={{ background: 'linear-gradient(135deg, #38bdf8, #6366f1)', padding: '0.875rem 2rem', fontWeight: 600, fontSize: '1rem' }}
                >
                  {planLoading ? 'Creating your study plan...' : 'Create My Study Plan 📋'}
                </button>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginTop: '0.75rem' }}>
                  Generate a personalized 4-week placement preparation plan based on your skill-gap analysis.
                </p>
              </div>
            </div>
          )}

          {/* STUDY PLAN SECTION */}
          {studyPlan && (
            <div className="card" style={{ padding: '2rem', border: '1px solid #38bdf8' }}>
              <div style={{ borderBottom: '1px solid #334155', paddingBottom: '1.25rem', marginBottom: '1.5rem' }}>
                <span className="badge" style={{ backgroundColor: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8', border: '1px solid #38bdf8', marginBottom: '0.5rem' }}>
                  Personalized Study Plan
                </span>
                <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  {studyPlan.title}
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9375rem', marginTop: '0.5rem', lineHeight: '1.6' }}>
                  {studyPlan.goal}
                </p>
              </div>

              {/* Plan Overview */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', border: '1px solid #334155', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Duration</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{studyPlan.duration_weeks} weeks</div>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', border: '1px solid #334155', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Assessment</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>#{studyPlan.assessment_id}</div>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', border: '1px solid #334155', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Total Tasks</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{studyPlan.tasks?.length || 0}</div>
                </div>
              </div>

              {/* Progress Summary */}
              {(() => {
                const totalTasks = studyPlan.tasks?.length || 0;
                const completedTasks = (studyPlan.tasks || []).filter(t => t.status === 'completed').length;
                const remainingTasks = totalTasks - completedTasks;
                const pct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
                return (
                  <div style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155', marginBottom: '1.75rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                      <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>Progress Summary</h4>
                      <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#38bdf8' }}>{pct}%</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
                      <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Total: <strong style={{ color: '#fff' }}>{totalTasks}</strong></div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Completed: <strong style={{ color: 'var(--status-success)' }}>{completedTasks}</strong></div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Remaining: <strong style={{ color: 'var(--status-warning)' }}>{remainingTasks}</strong></div>
                    </div>
                    <div style={{ width: '100%', height: '8px', backgroundColor: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${pct}%`, height: '100%', backgroundColor: 'var(--status-success)', transition: 'width 0.3s ease' }} />
                    </div>
                  </div>
                );
              })()}

              {/* Weekly Plan */}
              {Array.from(new Set((studyPlan.tasks || []).map(t => t.week_number))).sort((a, b) => a - b).map(weekNum => (
                <div key={weekNum} style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#38bdf8', marginBottom: '0.875rem' }}>
                    WEEK {weekNum}
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {(studyPlan.tasks || []).filter(t => t.week_number === weekNum).map(task => (
                      <div key={task.id} style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.875rem',
                        padding: '1rem 1.25rem',
                        backgroundColor: '#0f172a',
                        borderRadius: '8px',
                        border: '1px solid #334155',
                        opacity: task.status === 'completed' ? 0.6 : 1
                      }}>
                        <input
                          type="checkbox"
                          checked={task.status === 'completed'}
                          onChange={() => handleTaskToggle(task.id, task.status)}
                          style={{ width: '18px', height: '18px', marginTop: '2px', cursor: 'pointer', accentColor: 'var(--accent-primary)' }}
                        />
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                            <span style={{ fontWeight: 600, color: 'var(--accent-primary)', fontSize: '0.875rem' }}>{task.skill}</span>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              {task.difficulty} • {task.estimated_minutes} min
                            </span>
                          </div>
                          <div style={{ color: 'var(--text-main)', fontSize: '0.875rem', lineHeight: '1.5', textDecoration: task.status === 'completed' ? 'line-through' : 'none' }}>
                            {task.task}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button onClick={loadHistory} className="btn" style={{ backgroundColor: '#334155', color: '#fff' }}>
              View Assessment History
            </button>
            <button onClick={handleStartTest} className="btn btn-primary">
              Take New Assessment
            </button>
          </div>
        </div>
      )}

      {/* VIEW 4: ASSESSMENT HISTORY */}
      {viewState === 'history' && (
        <div className="card" style={{ padding: '2rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1.25rem' }}>
            Assessment History
          </h3>

          {historyList.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No completed assessments found.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
              {historyList.map(item => (
                <div key={item.id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '1rem 1.25rem',
                  backgroundColor: '#0f172a',
                  borderRadius: '8px',
                  border: '1px solid #334155'
                }}>
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.9375rem' }}>
                      Placement Assessment #{item.id}
                    </div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                      Completed: {item.completed_at ? new Date(item.completed_at).toLocaleString() : 'N/A'}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#38bdf8' }}>
                        {item.overall_score}%
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {item.total_correct}/{item.total_questions} Correct
                      </div>
                    </div>
                    <button onClick={() => viewPastResult(item.id)} className="btn btn-primary" style={{ padding: '0.4rem 0.875rem', fontSize: '0.8125rem' }}>
                      View Breakdown & AI Analysis
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

    </div>
  );
}
