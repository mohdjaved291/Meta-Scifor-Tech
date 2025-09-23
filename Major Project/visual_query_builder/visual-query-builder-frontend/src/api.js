import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const queryBuilderAPI = {
    getConnections: () => api.get('/connections/'),
    getSchema: (connectionId) => api.get(`/connections/${connectionId}/schema/`),
    buildQuery: (data) => api.post('/query/build/', data),
    executeQuery: (data) => api.post('/query/execute/', data),
};

export default api;