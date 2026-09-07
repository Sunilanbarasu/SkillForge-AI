import React, { useEffect, useState } from 'react';
import {
  getDailyChallenge,
  getCodingStreak,
  submitDailyChallenge,
} from '../api/client';

const DailyChallenge = () => {
  const [challenge, setChallenge] = useState(null);
  const [streak, setStreak] = useState({
    current_streak: 0,
    best_streak: 0,
    total_completed: 0,
  });
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [showHints, setShowHints] = useState(false);

  const loadChallenge = async () => {
    setLoading(true);
    setError('');

    const [challengeRes, streakRes] = await Promise.all([
      getDailyChallenge(),
      getCodingStreak(),
    ]);

    if (challengeRes.success) {
      const dailyChallenge = challengeRes.data;
      setChallenge(dailyChallenge);

      const storageKey =
        `skillforge_daily_code_${dailyChallenge.challenge_id}_${dailyChallenge.challenge_date}`;

      const savedCode = localStorage.getItem(storageKey);

      setCode(
        savedCode !== null
          ? savedCode
          : (dailyChallenge.starter_code || '')
      );
    } else {
      setError(challengeRes.error);
    }

    if (streakRes.success) {
      setStreak(streakRes.data);
    }

    setLoading(false);
  };

  useEffect(() => {
    loadChallenge();
  }, []);

  const handleSubmit = async () => {
    if (!challenge || !code.trim() || submitting) return;

    setSubmitting(true);
    setResult(null);
    setError('');

    const response = await submitDailyChallenge(
      challenge.challenge_id,
      code
    );

    if (response.success) {
      setResult(response.data);

      if (response.data.completed) {
        setChallenge((prev) => ({
          ...prev,
          completed: true,
          completed_at: new Date().toISOString(),
        }));

        if (response.data.streak) {
          setStreak(response.data.streak);
        }
      }
    } else {
      setError(response.error);
    }

    setSubmitting(false);
  };

  if (loading) {
    return (
      <section className="daily-challenge-card">
        <div className="daily-loading">
          <div className="daily-spinner" />
          <p>Preparing your AI coding mission...</p>
        </div>
      </section>
    );
  }

  if (error && !challenge) {
    return (
      <section className="daily-challenge-card">
        <div className="daily-error">
          <strong>Unable to load today's challenge</strong>
          <p>{error}</p>
          <button onClick={loadChallenge}>Try Again</button>
        </div>
      </section>
    );
  }

  if (!challenge) return null;

  return (
    <section className="daily-challenge-card">
      <div className="daily-header">
        <div>
          <div className="daily-eyebrow">
            <span className="daily-spark">✦</span>
            AI DAILY MISSION
          </div>
          <h2>{challenge.title}</h2>
          <p className="daily-subtitle">
            A personalized coding challenge selected from your current
            SkillForge learning profile.
          </p>
        </div>

        <div className="daily-completion-badge">
          {challenge.completed ? '✓ Completed' : '● Today'}
        </div>
      </div>

      <div className="daily-meta">
        <span>{challenge.skill}</span>
        <span>{challenge.difficulty}</span>
        <span>{challenge.language}</span>
      </div>

      <div className="daily-grid">
        <div className="daily-main">
          <div className="daily-panel">
            <h3>Challenge</h3>
            <p className="daily-description">
              {challenge.description}
            </p>
          </div>

          <div className="daily-editor-panel">
            <div className="daily-editor-header">
              <div>
                <h3>Your Solution</h3>
                <span>Complete the <code>solution()</code> function.</span>
              </div>
              <span className="daily-language">Python</span>
            </div>

            <textarea
              value={code}
              onChange={(event) => {
                const value = event.target.value;
                setCode(value);

                if (challenge) {
                  const storageKey =
                    `skillforge_daily_code_${challenge.challenge_id}_${challenge.challenge_date}`;

                  localStorage.setItem(storageKey, value);
                }
              }}
              onKeyDown={(event) => {
                if (event.key !== "Tab") return;

                event.preventDefault();

                const textarea = event.currentTarget;
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                const value = textarea.value;

                const updatedValue =
                  value.substring(0, start) +
                  "    " +
                  value.substring(end);

                setCode(updatedValue);

                if (challenge) {
                  const storageKey =
                    `skillforge_daily_code_${challenge.challenge_id}_${challenge.challenge_date}`;

                  localStorage.setItem(storageKey, updatedValue);
                }

                requestAnimationFrame(() => {
                  textarea.selectionStart = start + 4;
                  textarea.selectionEnd = start + 4;
                });
              }}
              className="daily-code-editor"
              spellCheck="false"
              disabled={challenge.completed || submitting}
              aria-label="Python solution editor"
            />

            <div className="daily-editor-actions">
              <button
                className="daily-submit-button"
                onClick={handleSubmit}
                disabled={
                  challenge.completed ||
                  submitting ||
                  !code.trim()
                }
              >
                {submitting ? 'Running Tests...' : '▶ Submit Solution'}
              </button>

              {challenge.completed && (
                <span className="daily-success-text">
                  ✓ Challenge completed
                </span>
              )}
            </div>
          </div>

          {result && (() => {
            const feedback = result.feedback || '';

            let resultType = 'Wrong Answer';
            let resultIcon = '⚠️';
            let resultTitle = 'Some tests failed';
            let resultClass = 'daily-result-failed';

            if (result.passed) {
              resultType = 'Success';
              resultIcon = '🎉';
              resultTitle = 'All tests passed!';
              resultClass = 'daily-result-success';
            } else if (/SyntaxError/i.test(feedback)) {
              resultType = 'Syntax Error';
              resultIcon = '🔴';
              resultTitle = 'Syntax error in your code';
            } else if (/Runtime Error|NameError|TypeError|ValueError|IndexError|KeyError|AttributeError/i.test(feedback)) {
              resultType = 'Runtime Error';
              resultIcon = '🔴';
              resultTitle = 'Your code caused a runtime error';
            } else if (/Timeout|timed out/i.test(feedback)) {
              resultType = 'Timeout';
              resultIcon = '⏱️';
              resultTitle = 'Your code took too long';
            } else if (/restricted|not allowed|blocked/i.test(feedback)) {
              resultType = 'Restricted Operation';
              resultIcon = '🚫';
              resultTitle = 'Restricted operation detected';
            }

            return (
              <div className={`daily-result ${resultClass}`}>
                <div className="daily-result-top">
                  <div>
                    <div className="daily-result-type">
                      <span>{resultIcon}</span>
                      <strong>{resultType}</strong>
                    </div>

                    <h3>{resultTitle}</h3>

                    <p className="daily-result-feedback">
                      {feedback}
                    </p>
                  </div>

                  <div className="daily-score">
                    <strong>{result.score ?? 0}%</strong>
                    <span>Score</span>
                  </div>
                </div>

                {result.passed_tests !== undefined && (
                  <div className="daily-test-count">
                    <span>
                      Tests passed
                    </span>
                    <strong>
                      {result.passed_tests} / {result.total_tests}
                    </strong>
                  </div>
                )}
              </div>
            );
          })()}

          {challenge.explanation && challenge.completed && (
            <div className="daily-panel daily-explanation">
              <h3>💡 AI Explanation</h3>
              <p>{challenge.explanation}</p>
            </div>
          )}

          {challenge.hints?.length > 0 && (
            <div className="daily-hints">
              <button
                className="daily-hints-toggle"
                onClick={() => setShowHints((value) => !value)}
              >
                <span>💡 Need a hint?</span>
                <span>{showHints ? '▲' : '▼'}</span>
              </button>

              {showHints && (
                <div className="daily-hints-content">
                  {challenge.hints.map((hint, index) => (
                    <div key={index} className="daily-hint">
                      <strong>Hint {index + 1}</strong>
                      <p>{hint}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <aside className="daily-sidebar">
          <div className="streak-card streak-primary">
            <span className="streak-icon">🔥</span>
            <span className="streak-label">Current Streak</span>
            <strong>{streak.current_streak}</strong>
            <small>
              {streak.current_streak === 1 ? 'day' : 'days'}
            </small>
          </div>

          <div className="streak-card">
            <span className="streak-icon">🏆</span>
            <span className="streak-label">Best Streak</span>
            <strong>{streak.best_streak}</strong>
            <small>
              {streak.best_streak === 1 ? 'day' : 'days'}
            </small>
          </div>

          <div className="streak-card">
            <span className="streak-icon">✓</span>
            <span className="streak-label">Completed</span>
            <strong>{streak.total_completed}</strong>
            <small>challenges</small>
          </div>

          <div className="daily-ai-note">
            <span>✦</span>
            <div>
              <strong>Why this challenge?</strong>
              <p>
                SkillForge AI uses your target role, assessment performance,
                priority skills and learning level to personalize today's
                mission.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
};

export default DailyChallenge;
