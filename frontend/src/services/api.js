/**
 * API Service
 * Communicates with Node.js middleware (port 5000)
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

/**
 * Ask a question to the LLM
 */
export const askQuestion = async (query, mode = 'auto') => {
  const response = await apiClient.post('/ask', { query, mode });
  return response.data;
};

/**
 * Query RAG vectorstore
 */
export const queryRAG = async (query, topK = 5) => {
  const response = await apiClient.post('/rag', { query, top_k: topK });
  return response.data;
};

/**
 * Query the ReAct agent
 */
export const queryAgent = async (query, mode = 'auto', maxIterations = 5) => {
  const response = await apiClient.post('/agent', { 
    query, 
    mode, 
    max_iterations: maxIterations 
  });
  return response.data;
};

/**
 * Predict crop yield
 */
export const predictYield = async (data) => {
  const response = await apiClient.post('/predict_yield', data);
  return response.data;
};

/**
 * Detect plant disease from image
 */
export const detectPest = async (imageFile, topK = 3) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('top_k', topK);

  const response = await apiClient.post('/detect_pest', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Translate text
 */
export const translateText = async (text, sourceLang = 'auto', targetLang = 'en') => {
  const response = await apiClient.post('/translate', {
    text,
    source_lang: sourceLang,
    target_lang: targetLang,
  });
  return response.data;
};

/**
 * Health check
 */
export const healthCheck = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * Save conversation to history
 */
export const saveConversation = async (sessionId, title, messages, userId = 'anonymous') => {
  const response = await apiClient.post('/api/conversations/save', {
    session_id: sessionId,
    title: title,
    messages: messages,
    user_id: userId
  });
  return response.data;
};

/**
 * Get list of user's conversations
 */
export const getConversations = async (userId = 'anonymous', limit = 20) => {
  const response = await apiClient.post('/api/conversations/list', {
    user_id: userId,
    limit: limit
  });
  return response.data;
};

/**
 * Get a specific conversation
 */
export const getConversation = async (sessionId, userId = 'anonymous') => {
  const response = await apiClient.post('/api/conversations/get', {
    session_id: sessionId,
    user_id: userId
  });
  return response.data;
};

/**
 * Delete a conversation
 */
export const deleteConversation = async (sessionId, userId = 'anonymous') => {
  const response = await apiClient.post('/api/conversations/delete', {
    session_id: sessionId,
    user_id: userId
  });
  return response.data;
};

export default {
  askQuestion,
  queryRAG,
  queryAgent,
  predictYield,
  detectPest,
  translateText,
  healthCheck,
  saveConversation,
  getConversations,
  getConversation,
  deleteConversation,
};
