import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Compass, TrendingUp, Target, Brain } from 'lucide-react';

export default function Landing() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] px-4">
      <motion.div 
        className="max-w-4xl w-full text-center space-y-12"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants} className="space-y-6">
          <div className="inline-flex items-center justify-center p-3 bg-primary-500/10 rounded-full mb-4">
            <Compass className="h-12 w-12 text-primary-400" />
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            Navigate Your Future with <br/>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-600">
              AI Precision
            </span>
          </h1>
          <p className="text-xl text-textMuted max-w-2xl mx-auto">
            Leverage advanced Machine Learning models to predict your placement probability, estimate expected salary, and generate a highly personalized career roadmap.
          </p>
        </motion.div>

        <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/register" className="btn-primary text-lg px-8 py-4 w-full sm:w-auto text-center">
            Start Your Journey
          </Link>
          <Link to="/login" className="btn-secondary text-lg px-8 py-4 w-full sm:w-auto text-center">
            Sign In
          </Link>
        </motion.div>

        <motion.div variants={itemVariants} className="grid md:grid-cols-3 gap-6 pt-16">
          <div className="glass-card p-6 text-left">
            <TrendingUp className="h-8 w-8 text-primary-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Predictive Analytics</h3>
            <p className="text-textMuted">Analyze your academic and co-curricular profile to estimate your placement chances and salary potential.</p>
          </div>
          <div className="glass-card p-6 text-left">
            <Target className="h-8 w-8 text-primary-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Smart Clustering</h3>
            <p className="text-textMuted">Get categorized into specialized student clusters using K-Means to identify where you stand among peers.</p>
          </div>
          <div className="glass-card p-6 text-left">
            <Brain className="h-8 w-8 text-primary-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">AI Roadmaps</h3>
            <p className="text-textMuted">Receive a dynamically generated, personalized 4-month plan powered by Groq's cutting-edge AI.</p>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
