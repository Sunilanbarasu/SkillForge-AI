import React, { useEffect, useState } from 'react';
import {
  getCurrentProgress,
  getCurrentStudyPlan,
  updateTaskStatus,
  adaptStudyPlan,
} from '../api/client';

export function Dashboard() {
  const [progress, setProgress] = useState(null);
  const [studyPlan, setStudyPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [adapting, setAdapting] = useState(false);
  const [error, setError] = useState('');

  const loadDashboard = async () => {
    setLoading(true);
    setError('');

    const [progressResult, planResult] = await Promise.all([
      getCurrentProgress(),
      getCurrentStudyPlan(),
    ]);

    if (progressResult.success) {
      setProgress(progressResult.data);
    }

    if (planResult.success) {
      setStudyPlan(planResult.data);
    }

    if (!progressResult.success && progressResult.error) {
      setError(progressResult.error);
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
                  result.data?.completed_at ?? null,
              }
            : item
        ),
      }));
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

  if (loading) {
    return (
      <section className="card">
        <h2>Placement Dashboard</h2>
        <p style={{ color: 'var(--text-muted)' }}>
          Loading your progress...
        </p>
      </section>
    );
  }

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

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>

      {/* Header */}
      <section className="card">
        <h2 style={{ marginBottom: '0.5rem' }}>
          Placement Dashboard
        </h2>

        <p style={{ color: 'var(--text-muted)' }}>
          Track your actual assessment performance and
          adaptive preparation progress.
        </p>
      </section>

      {/* Overall Progress */}
      <section className="card">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '0.75rem',
          }}
        >
          <h3>Overall Placement Progress</h3>

          <strong>
            {currentScore.toFixed(1)}%
          </strong>
        </div>

        <div
          style={{
            width: '100%',
            height: '12px',
            background: '#1e293b',
            borderRadius: '999px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${Math.min(
                currentScore,
                100
              )}%`,
              height: '100%',
              background:
                'var(--accent-primary)',
              borderRadius: '999px',
              transition:
                'width 0.4s ease',
            }}
          />
        </div>

        <p
          style={{
            marginTop: '0.75rem',
            color:
              scoreChange > 0
                ? '#86efac'
                : scoreChange < 0
                  ? '#fca5a5'
                  : 'var(--text-muted)',
          }}
        >
          {scoreChange > 0 ? '+' : ''}
          {scoreChange.toFixed(1)}% since your
          previous assessment
        </p>
      </section>

      {/* Skill Progress */}
      {progress && (
        <section className="card">
          <h3
            style={{
              marginBottom: '1.25rem',
            }}
          >
            Skill Progress
          </h3>

          <div
            style={{
              display: 'grid',
              gap: '1rem',
            }}
          >
            {progress.skill_progress.map(
              (skill) => (
                <div key={skill.skill}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent:
                        'space-between',
                      marginBottom:
                        '0.35rem',
                    }}
                  >
                    <span>
                      {skill.skill}
                    </span>

                    <span
                      style={{
                        color:
                          skill.status ===
                          'Improved'
                            ? '#86efac'
                            : skill.status ===
                              'Declined'
                              ? '#fca5a5'
                              : 'var(--text-muted)',
                      }}
                    >
                      {skill.current_score.toFixed(
                        1
                      )}
                      % (
                      {skill.score_change > 0
                        ? '+'
                        : ''}
                      {skill.score_change.toFixed(
                        1
                      )}
                      )
                    </span>
                  </div>

                  <div
                    style={{
                      width: '100%',
                      height: '8px',
                      background:
                        '#1e293b',
                      borderRadius:
                        '999px',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        width: `${Math.min(
                          skill.current_score,
                          100
                        )}%`,
                        height: '100%',
                        background:
                          'var(--accent-primary)',
                        borderRadius:
                          '999px',
                      }}
                    />
                  </div>
                </div>
              )
            )}
          </div>

          <div
            style={{
              display: 'flex',
              gap: '1.5rem',
              marginTop: '1.5rem',
              color:
                'var(--text-muted)',
            }}
          >
            <span>
              Improved:{' '}
              {progress.improved_skills}
            </span>

            <span>
              Unchanged:{' '}
              {progress.unchanged_skills}
            </span>

            <span>
              Declined:{' '}
              {progress.declined_skills}
            </span>
          </div>
        </section>
      )}

      {/* Study Plan */}
      {studyPlan && (
        <section className="card">

          {/* Plan Header */}
          <div
            style={{
              display: 'flex',
              justifyContent:
                'space-between',
              alignItems: 'center',
              gap: '1rem',
              marginBottom: '1rem',
            }}
          >
            <div>
              <h3>
                {studyPlan.title}
              </h3>

              <p
                style={{
                  color:
                    'var(--text-muted)',
                }}
              >
                {studyPlan.goal}
              </p>
            </div>

            <button
              className="btn btn-primary"
              onClick={
                handleAdaptPlan
              }
              disabled={adapting}
            >
              {adapting
                ? 'Adapting...'
                : 'Adapt My Plan'}
            </button>
          </div>

          {/* Plan Progress */}
          <div
            style={{
              marginBottom: '1.5rem',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent:
                  'space-between',
                marginBottom: '0.4rem',
              }}
            >
              <span>
                Plan Progress
              </span>

              <strong>
                {taskProgress}%
              </strong>
            </div>

            <div
              style={{
                width: '100%',
                height: '10px',
                background:
                  '#1e293b',
                borderRadius:
                  '999px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${taskProgress}%`,
                  height: '100%',
                  background:
                    'var(--accent-primary)',
                  borderRadius:
                    '999px',
                }}
              />
            </div>

            <p
              style={{
                marginTop: '0.5rem',
                color:
                  'var(--text-muted)',
              }}
            >
              {completedTasks} of{' '}
              {tasks.length} tasks
              completed
            </p>
          </div>

          {/* Tasks */}
          <div
            style={{
              display: 'grid',
              gap: '0.75rem',
            }}
          >
            {tasks.map((task) => (
              <div
                key={task.id}
                style={{
                  display: 'flex',
                  alignItems:
                    'flex-start',
                  gap: '0.75rem',
                  padding: '1rem',
                  border:
                    '1px solid #334155',
                  borderRadius:
                    '10px',
                }}
              >
                {/* Completion checkbox */}
                <input
                  type="checkbox"
                  checked={
                    task.status ===
                    'completed'
                  }
                  onChange={() =>
                    handleTaskToggle(
                      task
                    )
                  }
                  style={{
                    marginTop:
                      '0.25rem',
                  }}
                />

                {/* Task Content */}
                <div
                  style={{
                    flex: 1,
                  }}
                >
                  <strong>
                    {task.task}
                  </strong>

                  <div
                    style={{
                      fontSize:
                        '0.8rem',
                      color:
                        'var(--text-muted)',
                      marginTop:
                        '0.35rem',
                    }}
                  >
                    {task.skill} · Week{' '}
                    {task.week_number} ·{' '}
                    {task.estimated_minutes}{' '}
                    min ·{' '}
                    {task.difficulty}
                  </div>

                  {/* Study Resource */}
                  {task.resource_url && (
                    <div
                      style={{
                        marginTop:
                          '0.75rem',
                        paddingTop:
                          '0.65rem',
                        borderTop:
                          '1px solid #334155',
                      }}
                    >
                      <div
                        style={{
                          fontSize:
                            '0.8rem',
                          color:
                            'var(--text-muted)',
                          marginBottom:
                            '0.35rem',
                        }}
                      >
                        📚 Study Resource
                      </div>

                      <a
                        href={
                          task.resource_url
                        }
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          color:
                            'var(--accent-primary)',
                          fontWeight:
                            '600',
                          textDecoration:
                            'none',
                        }}
                      >
                        {task.resource_title ||
                          'Open Study Resource'}{' '}
                        →
                      </a>
                    </div>
                  )}
                </div>

                {/* Status */}
                <span
                  style={{
                    fontSize:
                      '0.8rem',
                    color:
                      task.status ===
                      'completed'
                        ? '#86efac'
                        : 'var(--text-muted)',
                  }}
                >
                  {task.status}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Error */}
      {error && (
        <section className="card">
          <p
            style={{
              color: '#fca5a5',
            }}
          >
            {error}
          </p>
        </section>
      )}
    </div>
  );
}