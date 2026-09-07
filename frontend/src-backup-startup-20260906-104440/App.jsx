import React, { useEffect, useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { Profile } from './components/Profile';
import { Assessment } from './components/Assessment';
import { HealthStatus } from './components/HealthStatus';
import { Dashboard } from './components/Dashboard';

function MainApp() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState(
    user ? 'dashboard' : 'login'
  );
  const [mobileMenuOpen, setMobileMenuOpen] =
    useState(false);

  useEffect(() => {
    if (user && activeTab === 'login') {
      setActiveTab('dashboard');
    }

    if (!user && !['login', 'register', 'health'].includes(activeTab)) {
      setActiveTab('login');
    }
  }, [user, activeTab]);

  const navigate = (tab) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  const firstName =
    user?.name?.split(' ')[0] || 'Student';

  return (
    <div className="sf-app">
      <header className="sf-header">
        <div className="sf-header-inner">

          {/* Brand */}

          <button
            className="sf-brand"
            onClick={() =>
              navigate(
                user ? 'dashboard' : 'login'
              )
            }
            aria-label="Go to SkillForge home"
          >
            <span className="sf-brand-mark">
              SF
            </span>

            <span className="sf-brand-copy">
              <strong>
                SkillForge
              </strong>

              <small>
                AI CAREER INTELLIGENCE
              </small>
            </span>
          </button>

          {/* Desktop navigation */}

          <nav className="sf-nav">
            {user ? (
              <>
                <button
                  className={
                    activeTab === 'dashboard'
                      ? 'sf-nav-item sf-nav-active'
                      : 'sf-nav-item'
                  }
                  onClick={() =>
                    navigate('dashboard')
                  }
                >
                  <span>Overview</span>
                </button>

                <button
                  className={
                    activeTab === 'assessment'
                      ? 'sf-nav-item sf-nav-active'
                      : 'sf-nav-item'
                  }
                  onClick={() =>
                    navigate('assessment')
                  }
                >
                  <span>Assessment</span>
                </button>

                <button
                  className={
                    activeTab === 'profile'
                      ? 'sf-nav-item sf-nav-active'
                      : 'sf-nav-item'
                  }
                  onClick={() =>
                    navigate('profile')
                  }
                >
                  <span>Profile</span>
                </button>

                <button
                  className={
                    activeTab === 'health'
                      ? 'sf-nav-item sf-nav-active'
                      : 'sf-nav-item'
                  }
                  onClick={() =>
                    navigate('health')
                  }
                >
                  <span>System</span>
                </button>
              </>
            ) : (
              <>
                <button
                  className={
                    activeTab === 'login'
                      ? 'sf-nav-item sf-nav-active'
                      : 'sf-nav-item'
                  }
                  onClick={() =>
                    navigate('login')
                  }
                >
                  Sign in
                </button>

                <button
                  className={
                    activeTab === 'health'
                      ? 'sf-nav-item sf-nav-active'
                      : 'sf-nav-item'
                  }
                  onClick={() =>
                    navigate('health')
                  }
                >
                  System
                </button>
              </>
            )}
          </nav>

          {/* Account */}

          <div className="sf-header-account">
            {user ? (
              <>
                <div className="sf-user">
                  <span className="sf-user-avatar">
                    {firstName.charAt(0).toUpperCase()}
                  </span>

                  <span className="sf-user-name">
                    {firstName}
                  </span>
                </div>

                <button
                  className="sf-logout"
                  onClick={logout}
                  title="Sign out"
                >
                  Sign out
                </button>
              </>
            ) : (
              <button
                className="sf-register-button"
                onClick={() =>
                  navigate('register')
                }
              >
                Create account
                <span>→</span>
              </button>
            )}
          </div>

          {/* Mobile button */}

          <button
            className="sf-mobile-toggle"
            onClick={() =>
              setMobileMenuOpen(
                (current) => !current
              )
            }
            aria-label="Toggle navigation"
            aria-expanded={mobileMenuOpen}
          >
            <span />
            <span />
            <span />
          </button>
        </div>

        {/* Mobile navigation */}

        {mobileMenuOpen && (
          <div className="sf-mobile-menu">
            {user ? (
              <>
                <button
                  onClick={() =>
                    navigate('dashboard')
                  }
                  className={
                    activeTab === 'dashboard'
                      ? 'sf-mobile-item active'
                      : 'sf-mobile-item'
                  }
                >
                  Overview
                </button>

                <button
                  onClick={() =>
                    navigate('assessment')
                  }
                  className={
                    activeTab === 'assessment'
                      ? 'sf-mobile-item active'
                      : 'sf-mobile-item'
                  }
                >
                  Assessment
                </button>

                <button
                  onClick={() =>
                    navigate('profile')
                  }
                  className={
                    activeTab === 'profile'
                      ? 'sf-mobile-item active'
                      : 'sf-mobile-item'
                  }
                >
                  Profile
                </button>

                <button
                  onClick={() =>
                    navigate('health')
                  }
                  className={
                    activeTab === 'health'
                      ? 'sf-mobile-item active'
                      : 'sf-mobile-item'
                  }
                >
                  System
                </button>

                <button
                  onClick={() => {
                    logout();
                    setMobileMenuOpen(false);
                  }}
                  className="sf-mobile-item sf-mobile-logout"
                >
                  Sign out
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() =>
                    navigate('login')
                  }
                  className="sf-mobile-item"
                >
                  Sign in
                </button>

                <button
                  onClick={() =>
                    navigate('register')
                  }
                  className="sf-mobile-item active"
                >
                  Create account
                </button>

                <button
                  onClick={() =>
                    navigate('health')
                  }
                  className="sf-mobile-item"
                >
                  System
                </button>
              </>
            )}
          </div>
        )}
      </header>

      <main className="sf-main">
        {!user &&
          activeTab === 'login' && (
            <Login
              onSwitchToRegister={() =>
                setActiveTab('register')
              }
              onSuccess={() =>
                setActiveTab('dashboard')
              }
            />
          )}

        {!user &&
          activeTab === 'register' && (
            <Register
              onSwitchToLogin={() =>
                setActiveTab('login')
              }
              onSuccess={() =>
                setActiveTab('dashboard')
              }
            />
          )}

        {user &&
          activeTab === 'dashboard' && (
            <Dashboard />
          )}

        {user &&
          activeTab === 'assessment' && (
            <Assessment />
          )}

        {user &&
          activeTab === 'profile' && (
            <Profile />
          )}

        {activeTab === 'health' && (
          <HealthStatus />
        )}
      </main>

      <footer className="sf-footer">
        <div>
          <strong>
            SkillForge AI
          </strong>

          <span>
            Adaptive placement intelligence
          </span>
        </div>

        <span>
          Built for smarter preparation.
        </span>
      </footer>
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
