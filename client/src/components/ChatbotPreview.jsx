import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import './ChatbotPreview.css';

function ChatbotPreview({ chatbot, apiKey }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    if (chatbot?.config?.welcome_message) {
      setMessages([{
        role: 'assistant',
        content: chatbot.config.welcome_message,
        timestamp: new Date()
      }]);
    }
  }, [chatbot]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.sendChatMessage(
        chatbot._id,
        input,
        sessionId,
        apiKey
      );

      setSessionId(response.session_id);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.message,
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const primaryColor = chatbot?.config?.primary_color || '#646cff';

  return (
    <div className="chatbot-preview-container">
      <div className="chatbot-preview-header">
        <h3>Chatbot Preview</h3>
        <p>Test your chatbot before embedding it</p>
      </div>
      
      <div 
        className="chatbot-preview-widget"
        style={{ '--primary-color': primaryColor }}
      >
        <div className="chatbot-header" style={{ backgroundColor: primaryColor }}>
          <div className="chatbot-header-content">
            <div className="chatbot-avatar">🤖</div>
            <div>
              <div className="chatbot-name">{chatbot?.config?.name || 'Chatbot'}</div>
              <div className="chatbot-status">Online</div>
            </div>
          </div>
        </div>

        <div className="chatbot-messages">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`chatbot-message ${msg.role}`}
            >
              <div className="message-content">{msg.content}</div>
              <div className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </div>
            </div>
          ))}
          {loading && (
            <div className="chatbot-message assistant">
              <div className="message-content">
                <span className="typing-indicator">
                  <span></span><span></span><span></span>
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSend} className="chatbot-input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="chatbot-input"
            disabled={loading}
          />
          <button
            type="submit"
            className="chatbot-send-button"
            style={{ backgroundColor: primaryColor }}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatbotPreview;

