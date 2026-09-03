import React, { useState, useEffect } from 'react';
import { getStudentProfile, updateStudentProfile } from '../api/client';
import { useAuth } from '../context/AuthContext';

const AVAILABLE_SKILLS = ["Python", "C", "DSA", "SQL", "OOP", "DBMS", "Aptitude"];
const EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"];

export function Profile() {
  const { user, profile: authProfile, refreshProfile } = useAuth();
  const [targetRole, setTargetRole] = useState('Software Engineer');
  const [experienceLevel, setExperienceLevel] = useState('Beginner');
  const [selectedSkills, setSelectedSkills] = useState(['Python', 'DSA', 'SQL']);
  const [interests, setInterests] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [msg, setMsg] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchProf = async () => {
      setFetching(true);
      const res = await getStudentProfile();
      if (res.success && res.data) {
        setTargetRole(res.data.target_role || 'Software Engineer');
        setExperienceLevel(res.data.experience_level || 'Beginner');
        setSelectedSkills(res.data.selected_skills || []);
        setInterests((res.data.interests || []).join(', '));
      }
      setFetching(false);
    };
    fetchProf();
  }, []);

  const handleSkillToggle = (skill) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg({ type: '', text: '' });
    setLoading(true);

    const parsedInterests = interests
      ? interests.split(',').map(i => i.strip ? i.strip() : i.trim()).filter(Boolean)
      : [];

    const payload = {
      target_role: targetRole,
      experience_level: experienceLevel,
      interests: parsedInterests,
      selected_skills: selectedSkills,
    };

    const res = await updateStudentProfile(payload);
    setLoading(false);

    if (res.success) {
      setMsg({ type: 'success', text: 'Student profile updated successfully!' });
      refreshProfile();
    } else {
      setMsg({ type: 'error', text: res.error });
    }
  };

  if (fetching) {
    return (
      <div className="card" style={{ maxWidth: '640px', margin: '2rem auto', textAlign: 'center' }}>
        Loading student profile...
      </div>
    );
  }

  return (
    <div className="card" style={{ maxWidth: '680px', margin: '2rem auto' }}>
      <div style={{ borderBottom: '1px solid #334155', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
          Student Profile Setup
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Configure your target role and preparation skill selection for adaptive assessments.
        </p>
      </div>

      {user && (
        <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', border: '1px solid #334155' }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Student Info</div>
          <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-main)', marginTop: '0.25rem' }}>
            {user.name} ({user.email})
          </div>
        </div>
      )}

      {msg.text && (
        <div style={{
          backgroundColor: msg.type === 'success' ? 'var(--status-success-bg)' : 'var(--status-error-bg)',
          border: `1px solid ${msg.type === 'success' ? 'var(--status-success)' : 'var(--status-error)'}`,
          color: msg.type === 'success' ? '#6ee7b7' : '#fca5a5',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          fontSize: '0.875rem',
          marginBottom: '1.5rem'
        }}>
          {msg.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Target Role */}
        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Target Role
          </label>
          <input
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Software Engineer, Fullstack Developer"
            style={{
              width: '100%',
              padding: '0.625rem 0.875rem',
              borderRadius: '8px',
              border: '1px solid #334155',
              backgroundColor: '#0f172a',
              color: '#fff',
              fontSize: '0.9375rem'
            }}
          />
        </div>

        {/* Experience Level */}
        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Experience Level
          </label>
          <select
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
            style={{
              width: '100%',
              padding: '0.625rem 0.875rem',
              borderRadius: '8px',
              border: '1px solid #334155',
              backgroundColor: '#0f172a',
              color: '#fff',
              fontSize: '0.9375rem'
            }}
          >
            {EXPERIENCE_LEVELS.map(lvl => (
              <option key={lvl} value={lvl}>{lvl}</option>
            ))}
          </select>
        </div>

        {/* Selected Skills */}
        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Select Placement Skills
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {AVAILABLE_SKILLS.map(skill => {
              const isSelected = selectedSkills.includes(skill);
              return (
                <button
                  type="button"
                  key={skill}
                  onClick={() => handleSkillToggle(skill)}
                  style={{
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    border: isSelected ? '1px solid var(--accent-primary)' : '1px solid #334155',
                    backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.2)' : '#0f172a',
                    color: isSelected ? '#a5b4fc' : 'var(--text-muted)',
                    cursor: 'pointer',
                    fontWeight: isSelected ? 600 : 400,
                    fontSize: '0.875rem',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {isSelected ? `✓ ${skill}` : `+ ${skill}`}
                </button>
              );
            })}
          </div>
        </div>

        {/* Interests */}
        <div style={{ marginBottom: '1.75rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Interests / Domain Focus (comma separated)
          </label>
          <input
            type="text"
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
            placeholder="System Design, Algorithms, Web Development"
            style={{
              width: '100%',
              padding: '0.625rem 0.875rem',
              borderRadius: '8px',
              border: '1px solid #334155',
              backgroundColor: '#0f172a',
              color: '#fff',
              fontSize: '0.9375rem'
            }}
          />
        </div>

        <button type="submit" disabled={loading} className="btn btn-primary" style={{ padding: '0.75rem 1.5rem' }}>
          {loading ? 'Saving Profile...' : 'Save Profile Setup'}
        </button>
      </form>
    </div>
  );
}
