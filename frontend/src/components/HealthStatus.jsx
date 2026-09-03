import React, { useState, useEffect } from 'react';
import { getHealthStatus } from '../api/client';

export function HealthStatus() {
  const [loading, setLoading] = useState(true);
  const [healthData, setHealthData] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  const fetchHealth = async () => {
    setLoading(true);
    setErrorMsg(null);
    const result = await getHealthStatus();
    setLastChecked(new Date().toLocaleTimeString());

    if (result.success || result.data) {
      setHealthData(result.data);
      if (!result.success && result.data?.database?.error) {
        setErrorMsg(`PostgreSQL Connection Warning: ${result.data.database.error}`);
      }
    } else {
      setHealthData(null);
      setErrorMsg(result.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const isBackendOnline = Boolean(healthData);
  const isDbConnected = healthData?.database?.status === 'connected';

  return (
    <div className="card" style={{ marginTop: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)' }}>System Diagnostics</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Phase 1 Foundation - Health Endpoint Verification
          </p>
        </div>
        <button onClick={fetchHealth} disabled={loading} className="btn btn-primary">
          {loading ? 'Testing Connection...' : 'Re-test Connection'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        {/* Backend API Status */}
        <div style={{ padding: '1rem', backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #334155' }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>FastAPI Backend</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className={`badge ${isBackendOnline ? 'badge-success' : 'badge-error'}`}>
              {isBackendOnline ? 'ONLINE' : 'OFFLINE'}
            </span>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-main)' }}>
              {isBackendOnline ? 'http://localhost:8000' : 'Unreachable'}
            </span>
          </div>
        </div>

        {/* PostgreSQL Status */}
        <div style={{ padding: '1rem', backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #334155' }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>PostgreSQL Database</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className={`badge ${isDbConnected ? 'badge-success' : 'badge-error'}`}>
              {isDbConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-main)' }}>
              {healthData?.database?.type || 'PostgreSQL'}
            </span>
          </div>
        </div>
      </div>

      {/* Raw Response Output */}
      {healthData && (
        <div style={{ marginTop: '1rem' }}>
          <h3 style={{ fontSize: '0.9375rem', fontWeight: 500, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Backend API Response (/api/v1/health)
          </h3>
          <pre style={{
            backgroundColor: '#090d16',
            padding: '1rem',
            borderRadius: '8px',
            border: '1px solid #1e293b',
            overflowX: 'auto',
            fontSize: '0.875rem',
            color: '#38bdf8'
          }}>
            {JSON.stringify(healthData, null, 2)}
          </pre>
        </div>
      )}

      {/* Error / Diagnostic Warning */}
      {errorMsg && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: 'var(--status-error-bg)',
          border: '1px solid var(--status-error)',
          borderRadius: '8px',
          color: '#fca5a5',
          fontSize: '0.875rem'
        }}>
          <strong>Connection Details:</strong> {errorMsg}
        </div>
      )}

      {lastChecked && (
        <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'right' }}>
          Last checked at: {lastChecked}
        </div>
      )}
    </div>
  );
}
