import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add CSRF token to all requests
api.interceptors.request.use((config) => {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
});

// Auth
export const getCsrfToken = () => api.get('/csrf/');
export const login = (username, password) => api.post('/login/', { username, password });
export const logout = () => api.post('/logout/');
export const getCurrentUser = () => api.get('/me/');

// Posts
export const getPosts = () => api.get('/posts/');
export const getPost = (id) => api.get(`/posts/${id}/`);
export const createPost = (content) => api.post('/posts/', { content });
export const likePost = (id) => api.post(`/posts/${id}/like/`);

// Comments
export const createComment = (postId, content, parentId = null) =>
    api.post('/comments/', { post: postId, content, parent: parentId });
export const likeComment = (id) => api.post(`/comments/${id}/like/`);

// Leaderboard
export const getLeaderboard = () => api.get('/leaderboard/');

// Users
export const getUser = (id) => api.get(`/users/${id}/`);

export default api;
