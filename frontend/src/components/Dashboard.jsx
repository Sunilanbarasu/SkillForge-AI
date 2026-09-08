import React, { useEffect, useState } from 'react';
import {
  getCurrentProgress,
  getPlacementAlignment,
  getStudentProfile,
} from '../api/client';

const formatNumber = (value) => {
  const n = Number(value);
  return Number.isFinite(n) ? Math.round(n) : 0;
};

const getStatus = (score) => {
  if (score >= 80) return 'Strong';
  if (score >= 65) return 'Good';
  if (score >= 50) return 'Developing';
  return 'Critical Gap';
};

export function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [progress, setProgress] = useState(null);
  const [alignment, setAlignment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadReadiness = async () => {
      setLoading(true);
      setError('');

      try {
        const [profileResult, progressResult, alignmentResult] =
          await Promise.all([
            getStudentProfile(),
            getCurrentProgress(),
            getPlacementAlignment(),
          ]);

        if (profileResult.success) setProfile(profileResult.data);
        if (progressResult.success) setProgress(progressResult.data);
        if (alignmentResult.success) setAlignment(alignmentResult.data);

        if (
          !profileResult.success &&
          !progressResult.success &&
          !alignmentResult.success
        ) {
          setError('Unable to load placement readiness data.');
        }
      } catch {
        setError('Unable to load placement readiness data.');
      } finally {
        setLoading(false);
      }
    };

    loadReadiness();
  }, []);

  // Profile is the source of truth for the student's current target career.
  // Alignment data may belong to an older assessment/career.
  const targetRole =
    profile?.target_role ||
    alignment?.target_role ||
    'Software Engineer';

  const readiness = formatNumber(
    alignment?.alignment_score ??
      progress?.current_overall_score ??
      0
  );

  const previousScore = formatNumber(
    progress?.previous_overall_score ?? 0
  );

  const scoreChange = formatNumber(
    progress?.overall_score_change ?? readiness - previousScore
  );

  const skills = Array.isArray(alignment?.skills)
    ? alignment.skills
    : Array.isArray(progress?.skill_progress)
      ? progress.skill_progress.map((item) => ({
          skill: item.skill,
          current_score: item.current_score,
          score: item.current_score,
          status: item.status,
        }))
      : [];

  const priorityGaps = Array.isArray(alignment?.priority_gaps)
    ? alignment.priority_gaps
    : skills
        .filter((item) => Number(item.current_score ?? item.score ?? 0) < 65)
        .sort(
          (a, b) =>
            Number(a.current_score ?? a.score ?? 0) -
            Number(b.current_score ?? b.score ?? 0)
        )
        .slice(0, 4);

  if (loading) {
    return (
      <main className="sf-dashboard">
        <div className="sf-loading">
          <div className="sf-spinner" />
          <p>Analyzing your placement readiness...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="sf-dashboard">
      <div className="sf-container">

        <header className="sf-hero">
          <div>
            <div className="sf-kicker">SKILLFORGE AI</div>
            <h1>
              Know your placement
              <br />
              <span>readiness.</span>
            </h1>
            <p>
              Evidence-based analysis of how prepared you are
              for your target career.
            </p>
          </div>

          <div className="sf-readiness">
            <div className="sf-readiness-top">
              <span>PLACEMENT READINESS</span>
              <strong>{readiness}%</strong>
            </div>

            <div className="sf-progress-track">
              <div
                className="sf-progress-fill"
                style={{ width: `${Math.min(readiness, 100)}%` }}
              />
            </div>

            <div className="sf-readiness-meta">
              <span>{targetRole}</span>
              <span>{getStatus(readiness)}</span>
            </div>
          </div>
        </header>

        {error && (
          <div className="sf-error">
            {error}
          </div>
        )}

        <section className="sf-panel">
          <div className="sf-panel-header">
            <div>
              <div className="sf-kicker">TARGET CAREER</div>
              <h2>{targetRole}</h2>
            </div>
            <span className="sf-badge">AI ANALYZED</span>
          </div>

          <p className="sf-muted">
            Your readiness is evaluated against the skills required
            for this career.
          </p>
        </section>

        <section className="sf-panel">
          <div className="sf-panel-header">
            <div>
              <div className="sf-kicker">SKILL INTELLIGENCE</div>
              <h2>Where you stand</h2>
            </div>
          </div>

          {skills.length === 0 ? (
            <div className="sf-empty">
              <h3>Complete an assessment</h3>
              <p>
                Take your first career-specific assessment to
                generate your skill intelligence.
              </p>
            </div>
          ) : (
            <div className="sf-skill-grid">
              {skills.map((item, index) => {
                const score = formatNumber(
                  item.current_score ?? item.score ?? item.readiness_score
                );

                return (
                  <div className="sf-skill-card" key={`${item.skill}-${index}`}>
                    <div className="sf-skill-card-top">
                      <strong>{item.skill}</strong>
                      <span>{score}%</span>
                    </div>

                    <div className="sf-progress-track">
                      <div
                        className="sf-progress-fill"
                        style={{ width: `${Math.min(score, 100)}%` }}
                      />
                    </div>

                    <span className="sf-skill-status">
                      {item.status || getStatus(score)}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        <section className="sf-two-column">

          <div className="sf-panel">
            <div className="sf-kicker">AI READINESS ANALYSIS</div>
            <h2>What is holding you back?</h2>

            {priorityGaps.length === 0 ? (
              <p className="sf-muted">
                No major skill gaps were identified from your
                available assessment data.
              </p>
            ) : (
              <>
                <p className="sf-muted">
                  These are currently the largest gaps affecting
                  your readiness for {targetRole}.
                </p>

                <div className="sf-gap-list">
                  {priorityGaps.map((item, index) => {
                    const score = formatNumber(
                      item.current_score ??
                        item.score ??
                        item.readiness_score
                    );

                    return (
                      <div className="sf-gap-item" key={`${item.skill}-${index}`}>
                        <span>{item.skill}</span>
                        <strong>{score}%</strong>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </div>

          <div className="sf-panel">
            <div className="sf-kicker">ASSESSMENT PROGRESS</div>
            <h2>Readiness over time</h2>

            {progress ? (
              <>
                <div className="sf-score-comparison">
                  <div>
                    <span>Previous</span>
                    <strong>{previousScore}%</strong>
                  </div>

                  <div className="sf-arrow">→</div>

                  <div>
                    <span>Current</span>
                    <strong>{readiness}%</strong>
                  </div>
                </div>

                <div className="sf-change">
                  {scoreChange >= 0 ? '+' : ''}
                  {scoreChange}% change
                </div>
              </>
            ) : (
              <p className="sf-muted">
                Complete another assessment to measure readiness
                improvement.
              </p>
            )}
          </div>

        </section>

        {alignment && (
          <section className="sf-panel">
            <div className="sf-panel-header">
              <div>
                <div className="sf-kicker">PLACEMENT ALIGNMENT</div>
                <h2>Career fit by measured skill</h2>
              </div>

              <strong className="sf-large-score">
                {formatNumber(alignment.alignment_score)}%
              </strong>
            </div>

            <div className="sf-alignment-stats">
              <div>
                <span>Ready</span>
                <strong>{alignment.ready_count || 0}</strong>
              </div>

              <div>
                <span>Near Ready</span>
                <strong>{alignment.near_ready_count || 0}</strong>
              </div>

              <div>
                <span>Priority Gaps</span>
                <strong>
                  {alignment.needs_improvement_count || 0}
                </strong>
              </div>
            </div>
          </section>
        )}

        <section className="sf-panel sf-next-assessment">
          <div>
            <div className="sf-kicker">NEXT STEP</div>
            <h2>Retest to measure your readiness.</h2>
            <p>
              SkillForge compares assessment evidence over time
              so you can see whether your placement readiness is
              actually changing.
            </p>
          </div>
        </section>

      </div>
    </main>
  );
}
