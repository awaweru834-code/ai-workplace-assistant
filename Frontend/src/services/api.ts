import axios from 'axios';
import { jwtDecode, JwtPayload } from 'jwt-decode';

// 1. Tell TypeScript about our custom FastAPI token structure
export interface AuthTokenPayload extends JwtPayload {
  role: string;
}

export const api = axios.create({
  baseURL: ' https://ai-workplace-assistant-1.onrender.com',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token.replace(/"/g, '')}`;
  return config;
});

api.interceptors.response.use(res => res, err => {
  if (err.response?.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login'; 
  }
  return Promise.reject(err);
});

// 2. Apply the custom type to the return payload
export const loginUser = async (username: string, password: string): Promise<AuthTokenPayload> => {
  const body = new URLSearchParams({ username, password });
  const { data } = await api.post('/auth/login', body);
  
  localStorage.setItem('token', data.access_token);
  return jwtDecode<AuthTokenPayload>(data.access_token);
};
// Add this below your loginUser function
export const getUserProfile = async () => {
  const { data } = await api.get('/users/me');
  return data;
};
// Fetches the saved PostgreSQL memory for this specific user
export const getChatHistory = async () => {
  const { data } = await api.get('/hr-chat/history');
  return data;
};

// Sends a new message to the AI Assistant
export const sendChatMessage = async (message: string) => {
  // Assuming your FastAPI Pydantic schema expects a JSON body with a "message" key.
  // If your backend expects a different key (like "text" or "query"), update it here.
  const { data } = await api.post('/hr-chat/', { message });
  return data;
};
// Fetches the direct array of all users
export const getAllUsers = async () => {
  const { data } = await api.get('/users/');
  return data;
};
// Update this specific function in src/services/api.ts
export const createUser = async (username: string, password: string, role: string = 'new_hire') => {
  const payload = { username, password, role };
  
  // Note: Using the POST /users/ endpoint from your API contract
  const { data } = await api.post('/users/', payload); 
  return data;
};


// Deactivates a specific user account
export const deactivateUser = async (userId: string | number) => {
  const { data } = await api.patch(`/users/${userId}/deactivate`);
  return data;
};
export const uploadPolicyDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file); 
  
  // Updated to match your FastAPI router prefix
  const { data } = await api.post('/docs/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return data;
};
