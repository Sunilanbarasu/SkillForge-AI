import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { Profile } from './components/Profile';
import { Assessment } from './components/Assessment';
import { HealthStatus } from './components/HealthStatus';
import { Dashboard } from './components/Dashboard';

function MainApp() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState(user ? 'dashboard' : 'login');

  return (
    <div className="container">
      {/* Navigation Header */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem',
        borderBottom: '1px solid #334155',
        paddingBottom: '1.25rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            backgroundColor: 'var(--accent-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            fontSize: '1.25rem',
            color: '#fff'
          }}>
            SF
          </div>

          <div>
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              background: 'linear-gradient(to right, #818cf8, #c084fc)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              SkillForge AI
            </h1>

            <p style={{
              fontSize: '0.8125rem',
              color: 'var(--text-muted)'
            }}>
              Adaptive Placement Preparation Platform
            </p>
          </div>
        </div>

        <nav style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          flexWrap: 'wrap'
        }}>
          {user ? (
            <>
              {/* Dashboard */}
              <button
                onClick={() => setActiveTab('dashboard')}
                className="btn"
                style={{
                  backgroundColor:
                    activeTab === 'dashboard'
                      ? '#334155'
                      : 'transparent',
                  color: 'var(--text-main)'
                }}
              >
                Dashboard
              </button>

              {/* Assessment */}
              <button
                onClick={() => setActiveTab('assessment')}
                className="btn"
                style={{
                  backgroundColor:
                    activeTab === 'assessment'
                      ? '#334155'
                      : 'transparent',
                  color: 'var(--text-main)'
                }}
              >
                Assessment Engine
              </button>

              {/* Profile */}
              <button
                onClick={() => setActiveTab('profile')}
                className="btn"
                style={{
                  backgroundColor:
                    activeTab === 'profile'
                      ? '#334155'
                      : 'transparent',
                  color: 'var(--text-main)'
                }}
              >
                Profile Setup
              </button>

              {/* Diagnostics */}
              <button
                onClick={() => setActiveTab('health')}
                className="btn"
                style={{
                  backgroundColor:
                    activeTab === 'health'
                      ? '#334155'
                      : 'transparent',
                  color: 'var(--text-muted)'
                }}
              >
                Diagnostics
              </button>

              {/* Logout */}
              <button
                onClick={logout}
                className="btn"
                style={{
                  backgroundColor: 'rgba(239, 68, 68, 0.2)',
                  color: '#fca5a5',
                  border: '1px solid rgba(239, 68, 68, 0.4)'
                }}
              >
                Logout ({user.name.split(' ')[0]})
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setActiveTab('login')}
                className="btn"
                style={{
                  backgroundColor:
                    activeTab === 'login'
                      ? '#334155'
                      : 'transparent',
                  color: 'var(--text-main)'
                }}
              >
                Login
              </button>

              <button
                onClick={() => setActiveTab('register')}
                className="btn btn-primary"
              >
                Register
              </button>

              <button
                onClick={() => setActiveTab('health')}
                className="btn"
                style={{
                  backgroundColor:
                    activeTab === 'health'
                      ? '#334155'
                      : 'transparent',
                  color: 'var(--text-muted)'
                }}
              >
                Diagnostics
              </button>
            </>
          )}
        </nav>
      </header>

      {/* Main View Area */}
      <main>
        {!user && activeTab === 'login' && (
          <Login
            onSwitchToRegister={() => setActiveTab('register')}
            onSuccess={() => setActiveTab('dashboard')}
          />
        )}

        {!user && activeTab === 'register' && (
          <Register
            onSwitchToLogin={() => setActiveTab('login')}
            onSuccess={() => setActiveTab('dashboard')}
          />
        )}

        {user && activeTab === 'dashboard' && (
          <Dashboard />
        )}

        {user && activeTab === 'assessment' && (
          <Assessment />
        )}

        {user && activeTab === 'profile' && (
          <Profile />
        )}

        {activeTab === 'health' && (
          <HealthStatus />
        )}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}