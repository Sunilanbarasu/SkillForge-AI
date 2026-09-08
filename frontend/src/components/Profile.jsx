import React, { useState, useEffect } from 'react';
import { getStudentProfile, updateStudentProfile } from '../api/client';
import { useAuth } from '../context/AuthContext';

const ROLE_PROFILES = {
  "Software Engineer": ["DSA", "Python", "OOP", "SQL", "DBMS", "C", "Aptitude"],
  "Software Developer": ["DSA", "Python", "OOP", "SQL", "DBMS", "C", "Aptitude"],
  "Full Stack Developer": ["JavaScript", "React", "APIs", "Python", "SQL", "DBMS", "DSA"],
  "Frontend Developer": ["JavaScript", "HTML/CSS", "React", "Web", "DSA", "Aptitude"],
  "Backend Developer": ["APIs", "Python", "SQL", "DBMS", "OOP", "DSA", "Git"],
  "Data Analyst": ["SQL", "Python", "Statistics", "Data Visualization", "DBMS", "Excel", "Aptitude"],
  "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Data Visualization", "DSA"],
  "AI/ML Engineer": ["Python", "Machine Learning", "Statistics", "DSA", "OOP", "SQL", "APIs"],
  "DevOps Engineer": ["Linux", "Cloud", "CI/CD", "Networking", "Git", "Python", "Security"],
  "Cybersecurity Engineer": ["Cybersecurity", "Networking", "Security", "Linux", "Python", "SQL", "C"]
};

const AVAILABLE_ROLES = Object.keys(ROLE_PROFILES);
const EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"];

const CAREER_CATALOG = {
  "Technology": [
    "Software Engineer",
    "Software Developer",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Mobile App Developer",
    "Web Developer",
    "Cloud Engineer",
    "DevOps Engineer",
    "Site Reliability Engineer",
    "Data Engineer",
    "Data Analyst",
    "Data Scientist",
    "AI/ML Engineer",
    "Machine Learning Engineer",
    "Computer Vision Engineer",
    "NLP Engineer",
    "Cybersecurity Engineer",
    "Security Engineer",
    "Network Engineer",
    "Database Administrator",
    "Solutions Architect",
    "System Administrator",
    "QA Engineer",
    "Automation Test Engineer",
    "Embedded Systems Engineer",
    "IoT Engineer",
    "Robotics Engineer",
    "Blockchain Developer",
    "Game Developer",
  ],
  "Design": [
    "UI/UX Designer",
    "Product Designer",
    "UX Researcher",
    "Visual Designer",
    "Graphic Designer",
    "Interaction Designer",
    "Motion Designer",
  ],
  "Product & Management": [
    "Product Manager",
    "Technical Product Manager",
    "Project Manager",
    "Program Manager",
    "Scrum Master",
    "Product Owner",
    "Engineering Manager",
  ],
  "Business & Analytics": [
    "Business Analyst",
    "Business Intelligence Analyst",
    "Financial Analyst",
    "Operations Analyst",
    "Marketing Analyst",
    "Management Consultant",
    "Risk Analyst",
  ],
  "Finance": [
    "Financial Planner",
    "Investment Analyst",
    "Credit Analyst",
    "Accountant",
    "Auditor",
    "FinTech Analyst",
  ],
  "Marketing & Sales": [
    "Digital Marketing Specialist",
    "SEO Specialist",
    "Content Strategist",
    "Social Media Manager",
    "Growth Marketer",
    "Sales Engineer",
    "Business Development Executive",
    "Account Executive",
  ],
  "Human Resources": [
    "HR Analyst",
    "HR Generalist",
    "Talent Acquisition Specialist",
    "Recruiter",
    "People Operations Specialist",
    "Learning & Development Specialist",
  ],
  "Engineering": [
    "Mechanical Engineer",
    "Electrical Engineer",
    "Electronics Engineer",
    "Civil Engineer",
    "Chemical Engineer",
    "Aerospace Engineer",
    "Automotive Engineer",
    "Biomedical Engineer",
    "Industrial Engineer",
    "Manufacturing Engineer",
    "Control Systems Engineer",
    "Mechatronics Engineer",
  ],
  "Media & Creative": [
    "Technical Writer",
    "Content Writer",
    "Copywriter",
    "Video Editor",
    "Content Creator",
    "Photographer",
    "Animator",
    "3D Artist",
  ],
};

const CAREER_CATEGORIES = Object.keys(CAREER_CATALOG);


export function Profile() {
  const { user, profile: authProfile, refreshProfile } = useAuth();
  const [targetRole, setTargetRole] = useState('Software Engineer');
  const [careerCategory, setCareerCategory] = useState('Technology');
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
        const savedRole = res.data.target_role || 'Software Engineer';
        const normalizedRole = CAREER_CATEGORIES
          .flatMap(category => CAREER_CATALOG[category])
          .includes(savedRole)
          ? savedRole
          : 'Software Engineer';

        setTargetRole(normalizedRole);

        const savedCategory = CAREER_CATEGORIES.find(category =>
          CAREER_CATALOG[category].includes(normalizedRole)
        );

        setCareerCategory(savedCategory || 'Technology');
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
      <div style={{ borderBottom: '1px solid var(--profile-info-muted)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
          Student Profile Setup
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Configure your target career for placement readiness assessments.
        </p>
      </div>

      {user && (
        <div style={{ backgroundColor: 'var(--profile-info-bg)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', border: '1px solid var(--profile-info-muted)' }}>
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
        {/* Career Category + Target Role */}
        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: 600,
            color: 'var(--text)',
            marginBottom: '0.5rem'
          }}>
            Career Category
          </label>

          <select
            value={careerCategory}
            onChange={(e) => {
              const newCategory = e.target.value;
              setCareerCategory(newCategory);

              const careers = CAREER_CATALOG[newCategory] || [];

              if (careers.length > 0) {
                const firstRole = careers[0];
                setTargetRole(firstRole);
                if (ROLE_PROFILES[firstRole]) {
                  setSelectedSkills(ROLE_PROFILES[firstRole]);
                }
              }
            }}
            style={{
              width: '100%',
              padding: '0.75rem 0.875rem',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              backgroundColor: 'var(--surface)',
              color: 'var(--text)',
              fontSize: '0.9375rem',
              cursor: 'pointer',
              marginBottom: '1rem'
            }}
          >
            {CAREER_CATEGORIES.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>

          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: 600,
            color: 'var(--text)',
            marginBottom: '0.5rem'
          }}>
            Target Role
          </label>

          <select
            value={targetRole}
            onChange={(e) => {
              const newRole = e.target.value;
              setTargetRole(newRole);
              if (ROLE_PROFILES[newRole]) {
                setSelectedSkills(ROLE_PROFILES[newRole]);
              }
            }}
            style={{
              width: '100%',
              padding: '0.75rem 0.875rem',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              backgroundColor: 'var(--surface)',
              color: 'var(--text)',
              fontSize: '0.9375rem',
              cursor: 'pointer'
            }}
          >
            {(CAREER_CATALOG[careerCategory] || []).map(role => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>

          <div style={{
            marginTop: '0.4rem',
            fontSize: '0.75rem',
            color: 'var(--text-secondary)'
          }}>
            Your assessments, AI analysis and placement readiness will follow this role.
          </div>
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
              border: '1px solid var(--profile-info-muted)',
              backgroundColor: 'var(--profile-info-bg)',
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
            {(ROLE_PROFILES[targetRole] || []).map(skill => {
              const isSelected = selectedSkills.includes(skill);
              return (
                <button
                  type="button"
                  key={skill}
                  onClick={() => handleSkillToggle(skill)}
                  style={{
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--profile-info-muted)',
                    backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.2)' : 'var(--profile-info-bg)',
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
              border: '1px solid var(--profile-info-muted)',
              backgroundColor: 'var(--profile-info-bg)',
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
