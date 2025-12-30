import axios from 'axios';

// Use environment variable for API URL (Vite uses import.meta.env.VITE_...)
export const API_URL = import.meta.env.VITE_API_URL || 'http://192.168.1.245:8016/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getSessions = async () => {
    const response = await api.get('/sessions');
    return response.data;
};

export const createSession = async () => {
    const response = await api.post('/sessions', { title: 'New Chat' });
    return response.data;
};

export const getSessionHistory = async (id) => {
    const response = await api.get(`/sessions/${id}`);
    return response.data;
};

export const updateSessionTitle = async (id, title) => {
    const response = await api.patch(`/sessions/${id}`, { title });
    return response.data;
};

export const deleteSession = async (id) => {
    const response = await api.delete(`/sessions/${id}`);
    return response.data;
};

// API_URL is already exported at the top
export default api;
