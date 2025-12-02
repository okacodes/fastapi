const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

export const api = {
  async login(username, password) {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || error.message || 'Login failed');
    }
    
    return await response.json();
  },

  async register(username, password) {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Registration failed');
    }
    
    return await response.json();
  },

  async getUser() {
    const response = await fetch(`${API_BASE_URL}/api/user`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }
    
    return await response.json();
  },

  async logout() {
    const response = await fetch(`${API_BASE_URL}/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    
    if (!response.ok) {
      throw new Error('Logout failed');
    }
    
    return await response.json();
  },

  // Business endpoints
  async registerBusiness(businessData) {
    const response = await fetch(`${API_BASE_URL}/api/business/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(businessData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }
    
    return await response.json();
  },

  async loginBusiness(username, password) {
    const response = await fetch(`${API_BASE_URL}/api/business/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed' + API_BASE_URL);
    }
    
    return await response.json();
  },

  async getCurrentBusiness() {
    const response = await fetch(`${API_BASE_URL}/api/business/me`, {
      method: 'GET',
      credentials: 'include',
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch business');
    }
    
    return await response.json();
  },

  async getChatbots() {
    const response = await fetch(`${API_BASE_URL}/api/business/chatbots`, {
      method: 'GET',
      credentials: 'include',
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch chatbots');
    }
    
    return await response.json();
  },

  async createChatbot(chatbotConfig) {
    const response = await fetch(`${API_BASE_URL}/api/business/chatbots`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(chatbotConfig),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create chatbot');
    }
    
    return await response.json();
  },

  async updateChatbot(chatbotId, chatbotConfig) {
    const response = await fetch(`${API_BASE_URL}/api/business/chatbots/${chatbotId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(chatbotConfig),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update chatbot');
    }
    
    return await response.json();
  },

  async getChatbot(chatbotId) {
    const response = await fetch(`${API_BASE_URL}/api/business/chatbots/${chatbotId}`, {
      method: 'GET',
      credentials: 'include',
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch chatbot');
    }
    
    return await response.json();
  },

  // Chat endpoint for preview
  async sendChatMessage(chatbotId, message, sessionId, apiKey) {
    const response = await fetch(`${API_BASE_URL}/api/chat/${chatbotId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }
    
    return await response.json();
  },
};

