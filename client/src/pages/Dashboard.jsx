import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import ChatbotPreview from '../components/ChatbotPreview';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [chatbots, setChatbots] = useState([]);
  const [selectedChatbot, setSelectedChatbot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newChatbot, setNewChatbot] = useState({
    name: '',
    description: '',
    system_prompt: 'You are a helpful assistant for a service business.',
    welcome_message: 'Hello! How can I help you today?',
    primary_color: '#646cff',
    enabled: true
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [businessData, chatbotsData] = await Promise.all([
        api.getCurrentBusiness(),
        api.getChatbots()
      ]);
      setBusiness(businessData);
      setChatbots(chatbotsData);
      if (chatbotsData.length > 0 && !selectedChatbot) {
        setSelectedChatbot(chatbotsData[0]);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
      navigate('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChatbot = async (e) => {
    e.preventDefault();
    try {
      const chatbot = await api.createChatbot(newChatbot);
      setChatbots([...chatbots, chatbot]);
      setSelectedChatbot(chatbot);
      setShowCreateForm(false);
      setNewChatbot({
        name: '',
        description: '',
        system_prompt: 'You are a helpful assistant for a service business.',
        welcome_message: 'Hello! How can I help you today?',
        primary_color: '#646cff',
        enabled: true
      });
    } catch (error) {
      alert('Failed to create chatbot: ' + error.message);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
    navigate('/login');
  };

  if (loading) {
    return <div className="dashboard">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <h1>Chatbot Platform</h1>
        <div className="nav-actions">
          <span className="business-name">{business?.name}</span>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="dashboard-sidebar">
          <div className="sidebar-section">
            <h2>Your Chatbots</h2>
            <button 
              onClick={() => setShowCreateForm(true)}
              className="btn btn-primary btn-full"
            >
              + Create Chatbot
            </button>
          </div>

          {showCreateForm && (
            <div className="create-chatbot-form">
              <h3>Create New Chatbot</h3>
              <form onSubmit={handleCreateChatbot}>
                <div className="form-group">
                  <label>Name</label>
                  <input
                    type="text"
                    value={newChatbot.name}
                    onChange={(e) => setNewChatbot({...newChatbot, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <input
                    type="text"
                    value={newChatbot.description}
                    onChange={(e) => setNewChatbot({...newChatbot, description: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Welcome Message</label>
                  <input
                    type="text"
                    value={newChatbot.welcome_message}
                    onChange={(e) => setNewChatbot({...newChatbot, welcome_message: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Primary Color</label>
                  <input
                    type="color"
                    value={newChatbot.primary_color}
                    onChange={(e) => setNewChatbot({...newChatbot, primary_color: e.target.value})}
                  />
                </div>
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary">Create</button>
                  <button type="button" onClick={() => setShowCreateForm(false)} className="btn btn-secondary">Cancel</button>
                </div>
              </form>
            </div>
          )}

          <div className="chatbot-list">
            {chatbots.length === 0 ? (
              <p className="empty-state">No chatbots yet. Create one to get started!</p>
            ) : (
              chatbots.map((chatbot) => (
                <div
                  key={chatbot._id}
                  className={`chatbot-item ${selectedChatbot?._id === chatbot._id ? 'active' : ''}`}
                  onClick={() => setSelectedChatbot(chatbot)}
                >
                  <div className="chatbot-item-name">{chatbot.config.name}</div>
                  <div className="chatbot-item-status">
                    {chatbot.config.enabled ? '✓ Active' : '○ Inactive'}
                  </div>
                </div>
              ))
            )}
          </div>

          {business?.api_key && (
            <div className="sidebar-section api-key-section">
              <h3>API Key</h3>
              <code className="api-key">{business.api_key}</code>
              <p className="api-key-note">Use this key to embed your chatbots</p>
            </div>
          )}
        </div>

        <div className="dashboard-main">
          {selectedChatbot ? (
            <div className="chatbot-details">
              <div className="chatbot-details-header">
                <h2>{selectedChatbot.config.name}</h2>
              </div>

              <div className="chatbot-info">
                <div className="info-item">
                  <label>Description</label>
                  <p>{selectedChatbot.config.description || 'No description'}</p>
                </div>
                <div className="info-item">
                  <label>Status</label>
                  <p>{selectedChatbot.config.enabled ? 'Active' : 'Inactive'}</p>
                </div>
                <div className="info-item">
                  <label>Model</label>
                  <p>{selectedChatbot.config.model}</p>
                </div>
              </div>

              {business?.api_key && (
                <ChatbotPreview 
                  chatbot={selectedChatbot} 
                  apiKey={business.api_key}
                />
              )}
            </div>
          ) : (
            <div className="empty-selection">
              <h2>Select a chatbot to preview</h2>
              <p>Choose a chatbot from the sidebar or create a new one</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

