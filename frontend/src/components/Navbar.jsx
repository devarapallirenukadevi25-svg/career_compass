import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/auth';
import { Compass, LogOut } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="border-b border-surfaceHighlight bg-surface/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <Compass className="h-8 w-8 text-primary-500" />
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-600">
                Career Compass
              </span>
            </Link>
          </div>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Link to="/dashboard" className="text-textMuted hover:text-textMain transition-colors">
                  Dashboard
                </Link>
                <Link to="/profile" className="text-textMuted hover:text-textMain transition-colors">
                  Profile
                </Link>
                <button 
                  onClick={handleLogout}
                  className="flex items-center space-x-2 text-textMuted hover:text-red-400 transition-colors"
                >
                  <LogOut className="h-5 w-5" />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-textMuted hover:text-textMain transition-colors">
                  Login
                </Link>
                <Link to="/register" className="btn-primary py-2 px-4">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
