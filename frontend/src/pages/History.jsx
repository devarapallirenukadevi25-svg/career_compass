import { useState, useEffect } from 'react';
import api from '../services/api';
import { Loader2, Calendar, Clock, Target, Briefcase } from 'lucide-react';
import { motion } from 'framer-motion';

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/predict/history');
        setHistory(res.data);
      } catch {
        setError('Failed to load prediction history');
      } finally {
        setLoading(false);
      }
    };
    
    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-4rem)]">
        <Loader2 className="animate-spin h-8 w-8 text-primary-500" />
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">Prediction History</h1>
      <p className="text-textMuted mb-8">Track your progress and prediction changes over time.</p>

      {error && <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-6">{error}</div>}

      {history.length === 0 && !error ? (
        <div className="glass-card p-12 text-center">
          <Clock className="h-16 w-16 text-textMuted mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-semibold mb-2">No History Available</h3>
          <p className="text-textMuted">Generate your first prediction to see it here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((record, index) => (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              key={index} 
              className="glass-card p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 hover:bg-surface/90 transition-colors"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-surfaceHighlight rounded-lg">
                  <Calendar className="h-6 w-6 text-primary-400" />
                </div>
                <div>
                  <p className="text-sm text-textMuted mb-1">{formatDate(record.created_at)}</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className="px-3 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-full text-xs font-medium">
                      {record.student_cluster}
                    </span>
                    <span className={`px-3 py-1 border rounded-full text-xs font-medium ${
                      record.svm_prediction === 1 
                        ? 'bg-green-500/10 text-green-400 border-green-500/20' 
                        : 'bg-red-500/10 text-red-400 border-red-500/20'
                    }`}>
                      SVM: {record.svm_prediction === 1 ? 'Placed' : 'Not Placed'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-8 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 border-surfaceHighlight pt-4 md:pt-0">
                <div className="text-center">
                  <p className="text-sm text-textMuted flex items-center justify-center gap-1 mb-1">
                    <Target className="h-4 w-4" /> Probability
                  </p>
                  <p className="text-2xl font-bold text-white">{record.placement_probability}%</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-textMuted flex items-center justify-center gap-1 mb-1">
                    <Briefcase className="h-4 w-4" /> Expected
                  </p>
                  <p className="text-2xl font-bold text-white">{record.salary_prediction} <span className="text-sm font-normal text-textMuted">LPA</span></p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
