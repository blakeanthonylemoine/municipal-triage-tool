import axios from 'axios';
import { clearTenantToken, getTenantToken } from './tenantAuth';

const tenantApi = axios.create({ baseURL: 'http://localhost:8000' });

tenantApi.interceptors.request.use((config) => {
  const token = getTenantToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

tenantApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearTenantToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default tenantApi;
