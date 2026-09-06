import React, { useEffect, useState } from 'react';
import { getHealthStatus } from '../api/client';

export function BackendStartup({ onReady }) {
  const [elapsed, setElapsed] = useState(0);
  const [status, setStatus] = useState('Connecting to SkillForge AI...');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const startedAt = Date.now();
    let cancelled = false;
    let retryTimer;

    const timer = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);

    const checkBackend = async () => {
      if (cancelled) return;

      const currentElapsed = Math.floor((Date.now() - startedAt) / 1000);

      setAttempt((value) => value + 1);

      if (currentElapsed < 5) {
        setStatus('Connecting to SkillForge AI...');
      } else if (currentElapsed < 30) {
        setStatus('Waking up the SkillForge AI engine...');
      } else if (currentElapsed < 60) {
        setStatus('Still preparing your learning environment...');
      } else {
        setStatus('Taking a little longer than usual. Still connecting...');
      }

      const result = await getHealthStatus();

      if (cancelled) return;

      if (result.success) {
        setStatus('SkillForge AI is ready.');
        clearInterval(timer);

        setTimeout(() => {
          if (!cancelled) {
            onReady();
          }
        }, 600);

        return;
      }

      retryTimer = setTimeout(checkBackend, 3000);
    };

    checkBackend();

    return () => {
      cancelled = true;
      clearInterval(timer);
      clearTimeout(retryTimer);
    };
  }, [onReady]);

  return (
    <div className="sf-startup">
      <div className="sf-startup-card">
        <div className="sf-startup-logo">SF</div>

        <div className="sf-startup-eyebrow">
          AI CAREER INTELLIGENCE
        </div>

        <h1>Preparing SkillForge AI</h1>

        <p className="sf-startup-description">
          We're connecting to your personalized learning engine.
          This happens automatically.
        </p>

        <div className="sf-startup-status">
          <span className="sf-startup-dot" />
          <span>{status}</span>
        </div>

        <div className="sf-startup-time">
          <strong>{elapsed}s</strong>
          <span>elapsed</span>
        </div>

        <div className="sf-startup-progress">
          <span />
        </div>

        <p className="sf-startup-note">
          The first visit may take a little longer while the backend
          wakes up. Please wait — SkillForge will continue automatically.
        </p>

        {attempt > 1 && (
          <p className="sf-startup-attempt">
            Connection attempt {attempt}
          </p>
        )}
      </div>
    </div>
  );
}
