import React, { useEffect, useMemo, useState } from 'react';
import {
  askStudyCoach,
  getCurrentProgress,
  getCurrentStudyPlan,
  updateTaskStatus,
  adaptStudyPlan,
  getPlacementAlignment,
  getAchievements,
} from '../api/client';

const statusClass = (value = '') => {
  const text = String(value).toLowerCase();

  if (
    text.includes('critical') ||
    text.includes('priority gap') ||
    text.includes('declined')
  ) {
    return 'sf-status sf-status-danger';
  }

  if (
    text.includes('priority') ||
    text.includes('near') ||
    text.includes('improvement') ||
    text.includes('medium')
  ) {
    return 'sf-status sf-status-warning';
  }

  if (
    text.includes('strong') ||
    text.includes('ready') ||
    text.includes('improved') ||
    text.includes('good')
  ) {
    return 'sf-status sf-status-success';
  }

  return 'sf-status sf-status-neutral';
};

const formatNumber = (value) => Number(value || 0).toFixed(1);

export function Dashboard() {
  const [progress, setProgress] = useState(null);
  const [studyPlan, setStudyPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [adapting, setAdapting] = useState(false);
  const [error, setError] = useState('');

  const [coachQuestion, setCoachQuestion] = useState('');
  const [coachAnswer, setCoachAnswer] = useState('');
  const [coachLoading, setCoachLoading] = useState(false);

  const [adaptiveAnalysis, setAdaptiveAnalysis] = useState(null);
  const [whySkill, setWhySkill] = useState(null);
  const [whyLoading, setWhyLoading] = useState(false);

  const [placementAlignment, setPlacementAlignment] = useState(null);
  const [achievements, setAchievements] = useState([]);

  const getAdaptiveAnalysis = async () => {
    const token = localStorage.getItem('token');

    if (!token) {
      return {
        success: false,
        error: 'Authentication required.',
      };
    }

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/v1/adaptive/analysis',
        {
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: 'application/json',
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error:
            data.detail ||
            'Failed to load adaptive analysis.',
        };
      }

      return {
        success: true,
        data,
      };
    } catch {
      return {
        success: false,
        error:
          'Unable to connect to the adaptive analysis service.',
      };
    }
  };

  const getWhyExplanation = async (skill) => {
    setWhyLoading(true);
    setWhySkill(null);

    const token = localStorage.getItem('token');

    if (!token) {
      setError('Authentication required.');
      setWhyLoading(false);
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/adaptive/why/${encodeURIComponent(skill)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: 'application/json',
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            'Failed to load explanation.'
        );
      } else {
        setWhySkill(data);
      }
    } catch {
      setError(
        'Unable to load the skill explanation.'
      );
    } finally {
      setWhyLoading(false);
    }
  };

  const handleCoachAsk = async () => {
    const question = coachQuestion.trim();

    if (!question || coachLoading) {
      return;
    }

    setCoachLoading(true);
    setCoachAnswer('');

    const result = await askStudyCoach(question);

    if (result.success) {
      setCoachAnswer(result.data.answer);
    } else {
      setCoachAnswer(
        result.error ||
          'Unable to get a coach response.'
      );
    }

    setCoachLoading(false);
  };

  const loadDashboard = async () => {
    setLoading(true);
    setError('');

    const [
      progressResult,
      planResult,
      adaptiveResult,
      placementResult,
      achievementsResult,
    ] = await Promise.all([
      getCurrentProgress(),
      getCurrentStudyPlan(),
      getAdaptiveAnalysis(),
      getPlacementAlignment(),
      getAchievements(),
    ]);

    if (progressResult.success) {
      setProgress(progressResult.data);
    }

    if (planResult.success) {
      setStudyPlan(planResult.data);
    }

    if (adaptiveResult.success) {
      setAdaptiveAnalysis(
        adaptiveResult.data
      );
    }

    if (placementResult.success) {
      setPlacementAlignment(
        placementResult.data
      );
    }

    if (achievementsResult.success) {
      setAchievements(
        achievementsResult.data
      );
    }

    const firstError =
      !progressResult.success
        ? progressResult.error
        : !planResult.success
          ? planResult.error
          : '';

    if (firstError) {
      setError(firstError);
    }

    setLoading(false);
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleTaskToggle = async (task) => {
    const newStatus =
      task.status === 'completed'
        ? 'pending'
        : 'completed';

    const result = await updateTaskStatus(
      task.id,
      newStatus
    );

    if (result.success) {
      setStudyPlan((current) => ({
        ...current,
        tasks: current.tasks.map((item) =>
          item.id === task.id
            ? {
                ...item,
                status: newStatus,
                completed_at:
                  result.data?.completed_at ??
                  null,
              }
            : item
        ),
      }));
    } else {
      setError(
        result.error ||
          'Failed to update task.'
      );
    }
  };

  const handleAdaptPlan = async () => {
    setAdapting(true);
    setError('');

    const result = await adaptStudyPlan();

    if (result.success) {
      setStudyPlan(result.data);
    } else {
      setError(result.error);
    }

    setAdapting(false);
  };

  const currentScore =
    progress?.current_overall_score ?? 0;

  const scoreChange =
    progress?.overall_score_change ?? 0;

  const tasks = studyPlan?.tasks || [];

  const completedTasks = tasks.filter(
    (task) => task.status === 'completed'
  ).length;

  const taskProgress =
    tasks.length > 0
      ? Math.round(
          (completedTasks / tasks.length) * 100
        )
      : 0;

  const incompleteTasks = tasks.filter(
    (task) => task.status !== 'completed'
  );

  const currentMissionWeek =
    incompleteTasks.length > 0
      ? Math.min(
          ...incompleteTasks.map(
            (task) => task.week_number
          )
        )
      : null;

  const weekTasks =
    currentMissionWeek !== null
      ? tasks.filter(
          (task) =>
            task.week_number ===
            currentMissionWeek
        )
      : [];

  const currentMission =
    weekTasks.find(
      (task) => task.status !== 'completed'
    ) ||
    weekTasks[0] ||
    null;

  const completedWeekTasks =
    weekTasks.filter(
      (task) => task.status === 'completed'
    ).length;

  const weekProgress =
    weekTasks.length > 0
      ? Math.round(
          (completedWeekTasks /
            weekTasks.length) *
            100
        )
      : 100;

  const prioritySkills = useMemo(() => {
    if (!adaptiveAnalysis?.skills) {
      return [];
    }

    return [...adaptiveAnalysis.skills]
      .sort((a, b) => {
        const priorityValue = {
          High: 0,
          Medium: 1,
          Low: 2,
        };

        const aPriority =
          priorityValue[a.priority] ?? 3;
        const bPriority =
          priorityValue[b.priority] ?? 3;

        if (aPriority !== bPriority) {
          return aPriority - bPriority;
        }

        return (
          Number(a.current_score || 0) -
          Number(b.current_score || 0)
        );
      })
      .slice(0, 5);
  }, [adaptiveAnalysis]);

  const topPrioritySkill =
    prioritySkills[0] || null;

  const targetRole =
    placementAlignment?.target_role ||
    'Software Engineer';

  if (loading) {
    return (
      <main className="sf-page">
        <div className="sf-shell">
          <div className="sf-loading">
            <div className="sf-loading-mark">
              SF
            </div>

            <div>
              <strong>
                Building your intelligence dashboard
              </strong>

              <span>
                Reading your latest assessment,
                learning plan and placement data...
              </span>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="sf-page">
      <div className="sf-shell">

        {/* =========================
            HERO
        ========================== */}

        <section className="sf-hero">
          <div className="sf-hero-main">
            <div className="sf-eyebrow">
              <span className="sf-eyebrow-dot" />
              AI CAREER INTELLIGENCE
            </div>

            <h1>
              Your placement journey,
              <br />
              <span>intelligently guided.</span>
            </h1>

            <p className="sf-hero-description">
              SkillForge continuously turns your
              assessment performance into your
              next learning decision.
            </p>

            <div className="sf-role-row">
              <span className="sf-role-label">
                TARGET ROLE
              </span>

              <span className="sf-role-value">
                {targetRole}
              </span>
            </div>
          </div>

          <div className="sf-readiness">
            <div className="sf-readiness-top">
              <span>PLACEMENT READINESS</span>

              <span
                className={
                  scoreChange > 0
                    ? 'sf-trend sf-trend-up'
                    : scoreChange < 0
                      ? 'sf-trend sf-trend-down'
                      : 'sf-trend'
                }
              >
                {scoreChange > 0 ? '↑' : ''}
                {scoreChange > 0
                  ? ` ${formatNumber(scoreChange)}`
                  : scoreChange < 0
                    ? ` ${formatNumber(scoreChange)}`
                    : ' —'}
              </span>
            </div>

            <div className="sf-score-row">
              <strong>
                {formatNumber(currentScore)}
                <small>%</small>
              </strong>

              <div className="sf-score-ring">
                <svg
                  viewBox="0 0 100 100"
                  aria-hidden="true"
                >
                  <circle
                    cx="50"
                    cy="50"
                    r="42"
                    className="sf-ring-track"
                  />

                  <circle
                    cx="50"
                    cy="50"
                    r="42"
                    className="sf-ring-value"
                    strokeDasharray="264"
                    strokeDashoffset={
                      264 -
                      (Math.min(
                        currentScore,
                        100
                      ) /
                        100) *
                        264
                    }
                  />
                </svg>

                <span>
                  LIVE
                </span>
              </div>
            </div>

            <div className="sf-readiness-footer">
              <span>
                Based on your latest assessment
              </span>

              {currentMission && (
                <button
                  className="sf-button sf-button-primary"
                  onClick={() =>
                    document
                      .getElementById(
                        'sf-mission'
                      )
                      ?.scrollIntoView({
                        behavior: 'smooth',
                      })
                  }
                >
                  Continue Mission
                  <span>→</span>
                </button>
              )}
            </div>
          </div>
        </section>

        {/* =========================
            AI INSIGHT
        ========================== */}

        <section className="sf-ai-insight">
          <div className="sf-ai-symbol">
            ✦
          </div>

          <div className="sf-ai-content">
            <div className="sf-ai-label">
              AI INSIGHT
            </div>

            <h2>
              {topPrioritySkill
                ? `${topPrioritySkill.skill} is your highest-priority gap.`
                : 'Your next learning decision is ready.'}
            </h2>

            <p>
              {topPrioritySkill
                ? `Your latest assessment recorded ${formatNumber(
                    topPrioritySkill.current_score
                  )}% in ${
                    topPrioritySkill.skill
                  }. SkillForge recommends focusing here before moving to lower-priority areas.`
                : 'Complete an assessment to let SkillForge identify your highest-impact learning priorities.'}
            </p>
          </div>

          {topPrioritySkill && (
            <button
              className="sf-button sf-button-dark"
              onClick={() =>
                getWhyExplanation(
                  topPrioritySkill.skill
                )
              }
              disabled={whyLoading}
            >
              {whyLoading
                ? 'Analyzing...'
                : `Why ${topPrioritySkill.skill}?`}
              <span>→</span>
            </button>
          )}
        </section>

        {/* =========================
            TOP GRID
        ========================== */}

        <div className="sf-two-column">

          {/* Skill intelligence */}

          {adaptiveAnalysis && (
            <section className="sf-panel">
              <div className="sf-panel-header">
                <div>
                  <div className="sf-kicker">
                    SKILL INTELLIGENCE
                  </div>

                  <h2>
                    Where you stand
                  </h2>

                  <p>
                    Actual performance,
                    interpreted by AI.
                  </p>
                </div>

                <div className="sf-panel-icon">
                  ✦
                </div>
              </div>

              <div className="sf-skill-list">
                {prioritySkills.map(
                  (skill) => (
                    <div
                      className="sf-skill-row"
                      key={skill.skill}
                    >
                      <div className="sf-skill-name">
                        <strong>
                          {skill.skill}
                        </strong>

                        <span>
                          {skill.classification}
                        </span>
                      </div>

                      <div className="sf-skill-meter">
                        <div className="sf-meter-track">
                          <div
                            className="sf-meter-fill"
                            style={{
                              width: `${Math.min(
                                Math.max(
                                  Number(
                                    skill.current_score ||
                                      0
                                  ),
                                  0
                                ),
                                100
                              )}%`,
                            }}
                          />
                        </div>
                      </div>

                      <strong className="sf-skill-score">
                        {formatNumber(
                          skill.current_score
                        )}%
                      </strong>

                      <span
                        className={statusClass(
                          skill.priority
                        )}
                      >
                        {skill.priority}
                      </span>
                    </div>
                  )
                )}
              </div>

              <div className="sf-panel-footer">
                <span>
                  Showing your highest-impact
                  skills
                </span>

                <span>
                  {adaptiveAnalysis.skills
                    ?.length || 0}{' '}
                  skills analyzed
                </span>
              </div>
            </section>
          )}

          {/* Mission */}

          {studyPlan && currentMission && (
            <section
              className="sf-panel sf-mission-panel"
              id="sf-mission"
            >
              <div className="sf-mission-topline">
                <div className="sf-kicker">
                  WEEK {currentMissionWeek}
                </div>

                <span className="sf-mission-progress">
                  {weekProgress}%
                </span>
              </div>

              <div className="sf-mission-number">
                0{currentMissionWeek}
              </div>

              <h2>
                Strengthen{' '}
                {currentMission.skill}
              </h2>

              <p className="sf-mission-subtitle">
                Your current mission was selected
                from your personalized placement
                plan.
              </p>

              <div className="sf-mission-task">
                <span>
                  NEXT ACTION
                </span>

                <strong>
                  {currentMission.task}
                </strong>

                <div className="sf-task-meta">
                  <span>
                    {currentMission.skill}
                  </span>

                  <span>
                    {currentMission.difficulty}
                  </span>

                  <span>
                    {currentMission.estimated_minutes}{' '}
                    min
                  </span>
                </div>
              </div>

              <div className="sf-mission-actions">
                {currentMission.resource_url && (
                  <a
                    href={
                      currentMission.resource_url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="sf-button sf-button-primary"
                  >
                    Start Mission
                    <span>↗</span>
                  </a>
                )}

                <button
                  className="sf-button sf-button-outline"
                  onClick={() =>
                    handleTaskToggle(
                      currentMission
                    )
                  }
                >
                  Mark Complete
                </button>
              </div>

              <div className="sf-week-progress">
                <div className="sf-progress-head">
                  <span>
                    Week {currentMissionWeek}
                  </span>

                  <strong>
                    {completedWeekTasks} /{' '}
                    {weekTasks.length}
                  </strong>
                </div>

                <div className="sf-progress-track">
                  <div
                    className="sf-progress-value"
                    style={{
                      width: `${weekProgress}%`,
                    }}
                  />
                </div>
              </div>
            </section>
          )}
        </div>

        {/* =========================
            WHY EXPLANATION
        ========================== */}

        {whySkill && (
          <section className="sf-explanation">
            <div className="sf-explanation-mark">
              ?
            </div>

            <div className="sf-explanation-content">
              <div className="sf-kicker">
                AI EVIDENCE
              </div>

              <h2>
                Why {whySkill.skill}?
              </h2>

              <p>
                {whySkill.explanation}
              </p>

              {Array.isArray(
                whySkill.evidence
              ) &&
                whySkill.evidence.length >
                  0 && (
                  <div className="sf-evidence-list">
                    {whySkill.evidence.map(
                      (item, index) => (
                        <div
                          key={index}
                          className="sf-evidence-item"
                        >
                          <span>✓</span>
                          {item}
                        </div>
                      )
                    )}
                  </div>
                )}
            </div>

            <button
              className="sf-icon-button"
              onClick={() =>
                setWhySkill(null)
              }
              aria-label="Close explanation"
            >
              ×
            </button>
          </section>
        )}

        {/* =========================
            PLACEMENT ALIGNMENT
        ========================== */}

        {placementAlignment && (
          <section className="sf-panel sf-placement">
            <div className="sf-panel-header">
              <div>
                <div className="sf-kicker">
                  PLACEMENT ALIGNMENT
                </div>

                <h2>
                  Your skills vs the role
                </h2>

                <p>
                  See exactly where your current
                  performance sits against the
                  requirements for{' '}
                  <strong>
                    {targetRole}
                  </strong>
                  .
                </p>
              </div>

              <div className="sf-alignment-score">
                <span>
                  ALIGNMENT
                </span>

                <strong>
                  {formatNumber(
                    placementAlignment.alignment_score
                  )}
                  %
                </strong>
              </div>
            </div>

            <div className="sf-alignment-summary">
              <div>
                <span>Target Role</span>
                <strong>
                  {targetRole}
                </strong>
              </div>

              <div>
                <span>Ready</span>
                <strong>
                  {placementAlignment.ready_count ||
                    0}
                </strong>
              </div>

              <div>
                <span>Near Ready</span>
                <strong>
                  {placementAlignment.near_ready_count ||
                    0}
                </strong>
              </div>

              <div>
                <span>Priority Gaps</span>
                <strong>
                  {placementAlignment.needs_improvement_count ||
                    0}
                </strong>
              </div>
            </div>

            {Array.isArray(
              placementAlignment.skills
            ) &&
              placementAlignment.skills.length >
                0 && (
                <div className="sf-gap-table">
                  <div className="sf-gap-header">
                    <span>SKILL</span>
                    <span>YOU</span>
                    <span>TARGET</span>
                    <span>GAP</span>
                    <span>STATUS</span>
                  </div>

                  {placementAlignment.skills.map(
                    (item) => {
                      const score = Number(
                        item.current_score || 0
                      );

                      const required =
                        Number(
                          item.required_score ||
                            0
                        );

                      const gap = Number(
                        item.gap || 0
                      );

                      return (
                        <div
                          className="sf-gap-row"
                          key={item.skill}
                        >
                          <div>
                            <strong>
                              {item.skill}
                            </strong>

                            <div className="sf-gap-mini-track">
                              <span
                                style={{
                                  width: `${Math.min(
                                    score,
                                    100
                                  )}%`,
                                }}
                              />
                            </div>
                          </div>

                          <strong>
                            {formatNumber(
                              score
                            )}
                            %
                          </strong>

                          <span>
                            {formatNumber(
                              required
                            )}
                            %
                          </span>

                          <span
                            className={
                              gap >= 0
                                ? 'sf-gap-positive'
                                : 'sf-gap-negative'
                            }
                          >
                            {gap >= 0
                              ? `+${formatNumber(
                                  gap
                                )}`
                              : `-${formatNumber(
                                  Math.abs(gap)
                                )}`}
                          </span>

                          <span
                            className={statusClass(
                              item.status
                            )}
                          >
                            {item.status}
                          </span>
                        </div>
                      );
                    }
                  )}
                </div>
              )}

            {Array.isArray(
              placementAlignment.priority_gaps
            ) &&
              placementAlignment.priority_gaps
                .length > 0 && (
                <div className="sf-priority-strip">
                  <div>
                    <span className="sf-priority-icon">
                      !
                    </span>

                    <div>
                      <strong>
                        Highest-impact gaps
                      </strong>

                      <span>
                        Focus here to move your
                        placement alignment fastest.
                      </span>
                    </div>
                  </div>

                  <div className="sf-priority-skills">
                    {placementAlignment.priority_gaps
                      .slice(0, 4)
                      .map((item) => (
                        <span key={item.skill}>
                          {item.skill}{' '}
                          <small>
                            {Math.abs(
                              Number(
                                item.gap || 0
                              )
                            ).toFixed(0)}
                          </small>
                        </span>
                      ))}
                  </div>
                </div>
              )}
          </section>
        )}

        {/* =========================
            PERFORMANCE JOURNEY
        ========================== */}

        {progress && (
          <section className="sf-panel">
            <div className="sf-panel-header">
              <div>
                <div className="sf-kicker">
                  PERFORMANCE JOURNEY
                </div>

                <h2>
                  Before → After
                </h2>

                <p>
                  Your latest change is measured
                  against your previous completed
                  assessment.
                </p>
              </div>

              <div
                className={
                  scoreChange > 0
                    ? 'sf-change sf-change-positive'
                    : scoreChange < 0
                      ? 'sf-change sf-change-negative'
                      : 'sf-change'
                }
              >
                {scoreChange > 0
                  ? '+'
                  : ''}
                {formatNumber(
                  scoreChange
                )}
                %
              </div>
            </div>

            <div className="sf-journey">
              <div className="sf-journey-step">
                <span>
                  PREVIOUS
                </span>

                <strong>
                  {formatNumber(
                    progress.previous_overall_score
                  )}
                  %
                </strong>
              </div>

              <div className="sf-journey-line">
                <span />
              </div>

              <div className="sf-journey-step sf-journey-current">
                <span>
                  CURRENT
                </span>

                <strong>
                  {formatNumber(
                    progress.current_overall_score
                  )}
                  %
                </strong>
              </div>

              <div className="sf-journey-line">
                <span />
              </div>

              <div className="sf-journey-step sf-journey-next">
                <span>
                  NEXT ASSESSMENT
                </span>

                <strong>
                  ?
                </strong>
              </div>
            </div>

            <div className="sf-progress-summary">
              <div>
                <span className="sf-dot sf-dot-success" />
                Improved
                <strong>
                  {progress.improved_skills}
                </strong>
              </div>

              <div>
                <span className="sf-dot sf-dot-neutral" />
                Unchanged
                <strong>
                  {progress.unchanged_skills}
                </strong>
              </div>

              <div>
                <span className="sf-dot sf-dot-danger" />
                Declined
                <strong>
                  {progress.declined_skills}
                </strong>
              </div>
            </div>

            <div className="sf-before-after">
              {progress.skill_progress.map(
                (skill) => (
                  <div
                    key={skill.skill}
                    className="sf-comparison-row"
                  >
                    <div className="sf-comparison-name">
                      <strong>
                        {skill.skill}
                      </strong>

                      <span
                        className={statusClass(
                          skill.status
                        )}
                      >
                        {skill.status}
                      </span>
                    </div>

                    <div className="sf-comparison-bars">
                      <div>
                        <span>
                          Before
                        </span>

                        <div className="sf-progress-track sf-track-small">
                          <div
                            className="sf-before-bar"
                            style={{
                              width: `${Math.min(
                                Math.max(
                                  Number(
                                    skill.previous_score ||
                                      0
                                  ),
                                  0
                                ),
                                100
                              )}%`,
                            }}
                          />
                        </div>
                      </div>

                      <div>
                        <span>
                          After
                        </span>

                        <div className="sf-progress-track sf-track-small">
                          <div
                            className="sf-progress-value"
                            style={{
                              width: `${Math.min(
                                Math.max(
                                  Number(
                                    skill.current_score ||
                                      0
                                  ),
                                  0
                                ),
                                100
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>

                    <strong
                      className={
                        skill.score_change > 0
                          ? 'sf-delta-positive'
                          : skill.score_change < 0
                            ? 'sf-delta-negative'
                            : ''
                      }
                    >
                      {skill.score_change > 0
                        ? '+'
                        : ''}
                      {formatNumber(
                        skill.score_change
                      )}
                    </strong>
                  </div>
                )
              )}
            </div>
          </section>
        )}

        {/* =========================
            FULL STUDY PLAN
        ========================== */}

        {studyPlan && (
          <section className="sf-panel sf-study-plan">
            <div className="sf-panel-header">
              <div>
                <div className="sf-kicker">
                  PERSONALIZED PLAN
                </div>

                <h2>
                  {studyPlan.title}
                </h2>

                <p>
                  {studyPlan.goal}
                </p>
              </div>

              <button
                className="sf-button sf-button-outline"
                onClick={handleAdaptPlan}
                disabled={adapting}
              >
                {adapting
                  ? 'Adapting...'
                  : 'Adapt My Plan'}
                <span>↗</span>
              </button>
            </div>

            <div className="sf-plan-progress">
              <div>
                <strong>
                  {taskProgress}%
                </strong>

                <span>
                  {completedTasks} of{' '}
                  {tasks.length} tasks
                  completed
                </span>
              </div>

              <div className="sf-progress-track">
                <div
                  className="sf-progress-value"
                  style={{
                    width: `${taskProgress}%`,
                  }}
                />
              </div>
            </div>

            <div className="sf-task-list">
              {tasks.map((task) => {
                const completed =
                  task.status ===
                  'completed';

                return (
                  <div
                    key={task.id}
                    className={
                      completed
                        ? 'sf-task-card sf-task-completed'
                        : 'sf-task-card'
                    }
                  >
                    <button
                      className={
                        completed
                          ? 'sf-task-check sf-task-check-done'
                          : 'sf-task-check'
                      }
                      onClick={() =>
                        handleTaskToggle(
                          task
                        )
                      }
                      aria-label={
                        completed
                          ? 'Mark task pending'
                          : 'Mark task complete'
                      }
                    >
                      {completed
                        ? '✓'
                        : ''}
                    </button>

                    <div className="sf-task-body">
                      <div className="sf-task-title-row">
                        <strong>
                          {task.task}
                        </strong>

                        <span>
                          Week{' '}
                          {
                            task.week_number
                          }
                        </span>
                      </div>

                      <div className="sf-task-details">
                        <span>
                          {task.skill}
                        </span>

                        <span>
                          {task.difficulty}
                        </span>

                        <span>
                          {
                            task.estimated_minutes
                          }{' '}
                          min
                        </span>
                      </div>

                      {task.resource_url && (
                        <a
                          href={
                            task.resource_url
                          }
                          target="_blank"
                          rel="noopener noreferrer"
                          className="sf-resource-link"
                        >
                          {task.resource_title ||
                            'Open study resource'}
                          {' →'}
                        </a>
                      )}
                    </div>

                    <span
                      className={
                        completed
                          ? 'sf-task-status sf-task-status-done'
                          : 'sf-task-status'
                      }
                    >
                      {completed
                        ? 'Completed'
                        : 'Pending'}
                    </span>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* =========================
            ACHIEVEMENTS + COACH
        ========================== */}

        <div className="sf-two-column sf-bottom-grid">

          <section className="sf-panel">
            <div className="sf-panel-header">
              <div>
                <div className="sf-kicker">
                  EVIDENCE-BASED PROGRESS
                </div>

                <h2>
                  Achievements
                </h2>

                <p>
                  Earned from what you actually
                  accomplish.
                </p>
              </div>

              <div className="sf-panel-icon">
                ◆
              </div>
            </div>

            {achievements.length === 0 ? (
              <div className="sf-empty">
                <span>
                  ◆
                </span>

                <strong>
                  Your first achievement is
                  waiting.
                </strong>

                <p>
                  Complete assessments and
                  personalized study tasks to
                  build your record.
                </p>
              </div>
            ) : (
              <div className="sf-achievement-grid">
                {achievements.map(
                  (achievement) => (
                    <div
                      className="sf-achievement"
                      key={achievement.key}
                    >
                      <div className="sf-achievement-icon">
                        ✓
                      </div>

                      <div>
                        <strong>
                          {
                            achievement.title
                          }
                        </strong>

                        <p>
                          {
                            achievement.description
                          }
                        </p>

                        <small>
                          Evidence:{" "}
                          {
                            achievement.evidence
                          }
                        </small>
                      </div>
                    </div>
                  )
                )}
              </div>
            )}
          </section>

          <section className="sf-coach">
            <div className="sf-coach-header">
              <div className="sf-coach-orb">
                ✦
              </div>

              <div>
                <div className="sf-kicker">
                  SKILLFORGE AI
                </div>

                <h2>
                  Study Coach
                </h2>
              </div>
            </div>

            <p className="sf-coach-description">
              Ask anything about your next
              learning step. The coach uses your
              actual assessment, placement gaps
              and study plan.
            </p>

            <div className="sf-coach-input">
              <input
                type="text"
                value={coachQuestion}
                onChange={(event) =>
                  setCoachQuestion(
                    event.target.value
                  )
                }
                onKeyDown={(event) => {
                  if (
                    event.key === 'Enter' &&
                    !coachLoading
                  ) {
                    handleCoachAsk();
                  }
                }}
                placeholder="What should I study next?"
                maxLength={1000}
                disabled={coachLoading}
              />

              <button
                onClick={handleCoachAsk}
                disabled={
                  !coachQuestion.trim() ||
                  coachLoading
                }
              >
                {coachLoading
                  ? '...'
                  : '→'}
              </button>
            </div>

            {coachAnswer && (
              <div className="sf-coach-answer">
                <span>
                  AI RESPONSE
                </span>

                <p>
                  {coachAnswer}
                </p>
              </div>
            )}

            {!coachAnswer &&
              !coachLoading && (
                <div className="sf-coach-suggestions">
                  <button
                    onClick={() =>
                      setCoachQuestion(
                        'What should I study next?'
                      )
                    }
                  >
                    What should I study next?
                  </button>

                  <button
                    onClick={() =>
                      setCoachQuestion(
                        'Why is my weakest skill important for my target role?'
                      )
                    }
                  >
                    Why is my weakest skill important?
                  </button>
                </div>
              )}
          </section>
        </div>

        {/* =========================
            PLAN COMPLETE
        ========================== */}

        {studyPlan &&
          !currentMission && (
            <section className="sf-complete">
              <div>
                <span>
                  ✓
                </span>

                <div>
                  <div className="sf-kicker">
                    MISSION COMPLETE
                  </div>

                  <h2>
                    You've completed your
                    current learning cycle.
                  </h2>

                  <p>
                    Take another assessment to
                    measure improvement and
                    generate your next adaptive
                    mission.
                  </p>
                </div>
              </div>
            </section>
          )}

        {/* =========================
            ERROR
        ========================== */}

        {error && (
          <section className="sf-error">
            <span>!</span>
            <p>{error}</p>
            <button
              onClick={() => setError('')}
              aria-label="Dismiss error"
            >
              ×
            </button>
          </section>
        )}

      </div>
    </main>
  );
}
