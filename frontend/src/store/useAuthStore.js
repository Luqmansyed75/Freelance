import { create } from 'zustand';
import api from '../api';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  // Initialize Auth state from token
  checkAuth: async () => {
    set({ isLoading: true });
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await api.get('/auth/me');
        set({ user: response.data, isAuthenticated: true, isLoading: false });
      } catch (error) {
        localStorage.removeItem('token');
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } else {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  // Login handler
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email); // FastAPI uses username field
    formData.append('password', password);

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    
    // Fetch user profile immediately
    const profileResponse = await api.get('/auth/me');
    set({ user: profileResponse.data, isAuthenticated: true });
  },

  // Register handler
  register: async (email, password) => {
    await api.post('/auth/register', { email, password });
    // After returning successfully, auto login
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const loginResponse = await api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    localStorage.setItem('token', loginResponse.data.access_token);
    const profileResponse = await api.get('/auth/me');
    set({ user: profileResponse.data, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, isAuthenticated: false });
  }
}));

export default useAuthStore;
