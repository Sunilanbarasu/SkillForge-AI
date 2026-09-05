import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor to attach JWT Authorization header
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('skillforge_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const getHealthStatus = async () => {
  try {
    const response = await apiClient.get('/health');
    return { success: true, data: response.data };
  } catch (error) {
    if (error.response) {
      return { success: false, data: error.response.data, status: error.response.status };
    }
    return { success: false, data: null, error: error.message || 'Unable to connect to backend.' };
  }
};

export const registerUser = async (name, email, password) => {
  try {
    const response = await apiClient.post('/auth/register', { name, email, password });
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Registration failed.';
    return { success: false, error: errorMsg };
  }
};

export const loginUser = async (email, password) => {
  try {
    const response = await apiClient.post('/auth/login', { email, password });
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Login failed.';
    return { success: false, error: errorMsg };
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/users/me');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to fetch current user.';
    return { success: false, error: errorMsg };
  }
};

export const getStudentProfile = async () => {
  try {
    const response = await apiClient.get('/profile');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to fetch profile.';
    return { success: false, error: errorMsg };
  }
};

export const updateStudentProfile = async (profileData) => {
  try {
    const response = await apiClient.put('/profile', profileData);
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to update profile.';
    return { success: false, error: errorMsg };
  }
};

export const startAssessment = async () => {
  try {
    const response = await apiClient.post('/assessments/start');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to start assessment.';
    return { success: false, error: errorMsg };
  }
};

export const submitAssessment = async (assessmentId, answersList) => {
  try {
    const response = await apiClient.post(
      `/assessments/${assessmentId}/submit`,
      { answers: answersList }
    );
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to submit assessment.';
    return { success: false, error: errorMsg };
  }
};

export const getAssessmentHistory = async () => {
  try {
    const response = await apiClient.get('/assessments/history');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to fetch assessment history.';
    return { success: false, error: errorMsg };
  }
};

export const getAssessmentResult = async (assessmentId) => {
  try {
    const response = await apiClient.get(`/assessments/${assessmentId}/result`);
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to fetch assessment result.';
    return { success: false, error: errorMsg };
  }
};

export const generateAIAnalysis = async (assessmentId) => {
  try {
    const response = await apiClient.post(
      `/assessments/${assessmentId}/ai-analysis`
    );
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to generate AI analysis.';
    return { success: false, error: errorMsg };
  }
};

export const generateStudyPlan = async () => {
  try {
    const response = await apiClient.post('/study-plans/generate');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to generate study plan.';
    return { success: false, error: errorMsg };
  }
};

export const getCurrentStudyPlan = async () => {
  try {
    const response = await apiClient.get('/study-plans/current');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to fetch study plan.';
    return { success: false, error: errorMsg };
  }
};

export const updateTaskStatus = async (taskId, status) => {
  try {
    const response = await apiClient.patch(
      `/study-plans/tasks/${taskId}`,
      { status }
    );
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to update task status.';
    return { success: false, error: errorMsg };
  }
};

// Phase 6: Get progress between the two latest assessments
export const getCurrentProgress = async () => {
  try {
    const response = await apiClient.get('/progress/current');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to fetch progress.';
    return { success: false, error: errorMsg };
  }
};

// Phase 6: Generate an adaptive study plan
export const adaptStudyPlan = async () => {
  try {
    const response = await apiClient.post('/study-plans/adapt');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed to adapt study plan.';
    return { success: false, error: errorMsg };
  }
};

// Phase 8: Get placement skill alignment
export const getPlacementAlignment = async () => {
  try {
    const response = await apiClient.get('/placement/alignment');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg =
      error.response?.data?.detail ||
      'Failed to fetch placement alignment.';
    return { success: false, error: errorMsg };
  }
};

// Phase 8: Get available placement roles
export const getPlacementRoles = async () => {
  try {
    const response = await apiClient.get('/placement/roles');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg =
      error.response?.data?.detail ||
      'Failed to fetch placement roles.';
    return { success: false, error: errorMsg };
  }
};

// Phase 9: Ask the student-aware AI study coach
export const askStudyCoach = async (question) => {
  try {
    const response = await apiClient.post('/coach/ask', { question });
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg =
      error.response?.data?.detail ||
      'Failed to get a response from the AI study coach.';
    return { success: false, error: errorMsg };
  }
};

// Phase 10: Get evidence-based achievements
export const getAchievements = async () => {
  try {
    const response = await apiClient.get('/achievements');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMsg =
      error.response?.data?.detail ||
      'Failed to fetch achievements.';
    return { success: false, error: errorMsg };
  }
};
export default apiClient;


