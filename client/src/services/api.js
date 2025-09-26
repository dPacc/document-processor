import axios from 'axios';

// Get API base URL from environment or default to localhost
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8050';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for processing
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`Received response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || 
                     error.response.data?.message || 
                     `Server error: ${error.response.status}`;
      throw new Error(message);
    } else if (error.request) {
      // Request made but no response received
      throw new Error('Unable to connect to server. Please check if the service is running.');
    } else {
      // Something happened in setting up the request
      throw new Error(`Request failed: ${error.message}`);
    }
  }
);

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export const processDocument = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/process', formData);
    return response.data;
  } catch (error) {
    console.error('Document processing failed:', error);
    throw error;
  }
};

export const processBatch = async (files) => {
  try {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post('/process-batch', formData);
    return response.data;
  } catch (error) {
    console.error('Batch processing failed:', error);
    throw error;
  }
};

export const getApiInfo = async () => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    console.error('Failed to get API info:', error);
    throw error;
  }
};

// Export the API instance for direct use if needed
export default api;