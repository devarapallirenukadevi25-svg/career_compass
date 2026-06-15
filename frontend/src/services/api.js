import axios from 'axios';

const DEFAULT_API_URL = 'http://127.0.0.1:5000/api';
const API_URL = (import.meta.env.VITE_API_URL || DEFAULT_API_URL).replace(/\/+$/, '');

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isCurrentUserLookup = error.config?.url?.includes('/auth/me');
    if (error.response?.status === 401 || (isCurrentUserLookup && error.response?.status === 404)) {
      localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);

export default api;
