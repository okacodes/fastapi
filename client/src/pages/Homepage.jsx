import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import './Homepage.css';

function Homepage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getUser()
      .then((userData) => {
        console.log(userData);
        setUser(userData);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Failed to get user:', error);
        setLoading(false);
      });
  }, []);

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (err) {
      console.error('Logout error:', err);
    }
    setUser(null);
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="homepage">
        <div className="loading-container">
          <div className="loading-spinner">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="homepage">
      <nav className="navbar">
        <h1>Firstpoint</h1>
        <div className="nav-buttons">
          {user ? (
            <>
              <span className="welcome-text">Welcome, {user.user}!</span>
              <button onClick={handleLogout} className="btn btn-secondary">
                Logout
              </button>
            </>
          ) : (
            <>
              <button onClick={() => navigate('/business/login')} className="btn btn-primary">
                Business Login
              </button>
              <button onClick={() => navigate('/business/register')} className="btn btn-secondary">
                Business Sign Up
              </button>
            </>
          )}
        </div>
      </nav>

      <main className="homepage-content">
        <div className="hero">
          <h2>Welcome to Firstpoint</h2>
          <p>
            {user
              ? `You're logged in as ${user.username}. Enjoy your stay!`
              : 'Get started by logging in or creating a new account.'}
          </p>
          {!user && (
            <div className="cta-buttons">
              <button onClick={() => navigate('/business/login')} className="btn btn-primary btn-large">
                Business Login
              </button>
              <button onClick={() => navigate('/business/register')} className="btn btn-secondary btn-large">
                Business Sign Up
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default Homepage;

