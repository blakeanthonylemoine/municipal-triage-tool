import axios from 'axios';
import { clearAdminToken, getAdminToken } from './adminAuth';

const adminApi = axios.create({ baseURL: 'http://localhost:8000' });

adminApi.interceptors.request.use((config) => {
  const token = getAdminToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

adminApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAdminToken();
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

export default adminApi;
