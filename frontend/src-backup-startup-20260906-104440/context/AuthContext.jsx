import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser, getStudentProfile } from '../api/client';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('skillforge_token') || null);
  const [loading, setLoading] = useState(true);

  const loadUserData = async () => {
    if (!token) {
      setUser(null);
      setProfile(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    const userRes = await getCurrentUser();
    if (userRes.success) {
      setUser(userRes.data);
      const profRes = await getStudentProfile();
      if (profRes.success) {
        setProfile(profRes.data);
      }
    } else {
      // Invalid/expired token
      logout();
    }
    setLoading(false);
  };

  useEffect(() => {
    loadUserData();
  }, [token]);

  const loginSession = (newToken, userData) => {
    localStorage.setItem('skillforge_token', newToken);
    setToken(newToken);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('skillforge_token');
    setToken(null);
    setUser(null);
    setProfile(null);
  };

  return (
    <AuthContext.Provider value={{ user, profile, token, loading, loginSession, logout, refreshProfile: loadUserData }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
