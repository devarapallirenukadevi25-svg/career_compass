import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/auth';
import { Compass, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Register() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    try {
      await registerUser(data.name, data.email, data.password);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to register');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] px-4 py-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card w-full max-w-md p-8"
      >
        <div className="flex flex-col items-center mb-8">
          <Compass className="h-10 w-10 text-primary-500 mb-2" />
          <h2 className="text-2xl font-bold">Create Account</h2>
          <p className="text-textMuted">Join Career Compass to get started</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-6 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium mb-2">Full Name</label>
            <input
              type="text"
              className="input-field"
              placeholder="John Doe"
              {...register('name', { required: 'Name is required' })}
            />
            {errors.name && <p className="text-red-400 text-sm mt-1">{errors.name.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Email Address</label>
            <input
              type="email"
              className="input-field"
              placeholder="you@example.com"
              {...register('email', { required: 'Email is required' })}
            />
            {errors.email && <p className="text-red-400 text-sm mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Password</label>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              {...register('password', { 
                required: 'Password is required',
                minLength: { value: 6, message: 'Password must be at least 6 characters' }
              })}
            />
            {errors.password && <p className="text-red-400 text-sm mt-1">{errors.password.message}</p>}
          </div>

          <button 
            type="submit" 
            className="btn-primary w-full flex justify-center items-center mt-2"
            disabled={isLoading}
          >
            {isLoading ? <Loader2 className="animate-spin h-5 w-5" /> : 'Create Account'}
          </button>
        </form>

        <p className="text-center mt-6 text-textMuted text-sm">
          Already have an account? <Link to="/login" className="text-primary-400 hover:text-primary-300 transition-colors">Sign in</Link>
        </p>
      </motion.div>
    </div>
  );
}
