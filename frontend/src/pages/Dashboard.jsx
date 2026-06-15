import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { motion } from 'framer-motion';
import { 
  PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer,
  RadialBarChart, RadialBar
} from 'recharts';
import { AlertCircle, Award, Briefcase, Compass, FileText, Gauge, Layers, Loader2, Target, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [insights, setInsights] = useState(null);
  const [roles, setRoles] = useState([]);
  const [targetRole, setTargetRole] = useState('');
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [refreshingInsights, setRefreshingInsights] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const profileRes = await api.get('/profile');
        setProfile(profileRes.data);

        try {
          const predictionRes = await api.get('/predict/current');
          setPrediction(predictionRes.data);
        } catch {
          console.log("No current prediction available");
        }

        try {
          const rolesRes = await api.get('/insights/roles');
          setRoles(rolesRes.data.roles || []);
        } catch {
          setRoles([]);
        }

        try {
          const insightsRes = await api.get('/insights/summary');
          setInsights(insightsRes.data);
          setTargetRole(insightsRes.data.skill_gap?.target_role || '');
        } catch (insightErr) {
          if (insightErr.response?.status !== 404) {
            setError('Dashboard loaded, but career insights could not be refreshed');
          }
        }
      } catch (err) {
        if (err.response?.status === 404) {
          navigate('/profile');
        } else {
          setError('Failed to load dashboard data');
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [navigate]);

  const refreshInsights = async (role = targetRole) => {
    setRefreshingInsights(true);
    setError('');
    try {
      const endpoint = role ? `/insights/summary?target_role=${encodeURIComponent(role)}` : '/insights/summary';
      const res = await api.get(endpoint);
      setInsights(res.data);
      setTargetRole(res.data.skill_gap?.target_role || role || '');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to refresh career insights');
    } finally {
      setRefreshingInsights(false);
    }
  };

  const handlePredict = async () => {
    setPredicting(true);
    setError('');
    try {
      const res = await api.post('/predict/');
      setPrediction(res.data);
      const profileRes = await api.get('/profile');
      setProfile(profileRes.data);
      await refreshInsights();
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed');
    } finally {
      setPredicting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-4rem)]">
        <Loader2 className="animate-spin h-8 w-8 text-primary-500" />
      </div>
    );
  }

  const radialData = prediction ? [
    { name: 'Probability', value: prediction.placement_probability, fill: '#0ea5e9' }
  ] : [];

  const radarData = profile ? [
    { metric: 'CGPA', value: Math.min(Number(profile.cgpa || 0) * 10, 100) },
    { metric: 'DSA', value: Math.min(Number(profile.leetcode || 0) / 5, 100) },
    { metric: 'Projects', value: Math.min(Number(profile.projects || 0) * 20, 100) },
    { metric: 'Internships', value: Math.min(Number(profile.internships || 0) * 35, 100) },
    { metric: 'Comm.', value: Math.min(Number(profile.communication || profile.communication_score || 0) * 10, 100) },
    { metric: 'ATS', value: insights?.ats?.ats_score || profile.ats_score || 0 },
  ] : [];

  const ats = insights?.ats;
  const skillGap = insights?.skill_gap;
  const roleRecommendations = insights?.role_recommendations || [];
  const domainMatch = insights?.domain_match;
  const resumeSummary = insights?.resume_summary;
  const readinessScore = prediction?.readiness_score ?? skillGap?.readiness_score ?? 0;
  const skillMatchScore = prediction?.skill_match ?? domainMatch?.match_percentage ?? 0;
  const resumeStrength = prediction?.resume_strength ?? ats?.ats_score ?? profile.ats_score ?? 0;
  const missingSkills = prediction?.missing_skills?.length ? prediction.missing_skills : (skillGap?.missing_skills || []);
  const recommendations = prediction?.recommendations?.length ? prediction.recommendations : (ats?.improvement_suggestions || []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-textMuted">Career Compass Pro insights and placement intelligence</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
          <select
            value={targetRole}
            onChange={(event) => {
              setTargetRole(event.target.value);
              refreshInsights(event.target.value);
            }}
            className="input-field min-w-[220px]"
          >
            <option value="">Auto target role</option>
            {roles.map((role) => (
              <option key={role} value={role}>{role}</option>
            ))}
          </select>
          <Link to="/profile" className="btn-secondary py-2 px-4">Edit Profile</Link>
          <button 
            onClick={handlePredict} 
            disabled={predicting}
            className="btn-primary py-2 px-4 flex items-center gap-2"
          >
            {predicting ? <Loader2 className="animate-spin h-5 w-5" /> : <TrendingUp className="h-5 w-5" />}
            {prediction ? 'Update Prediction' : 'Generate Prediction'}
          </button>
          <button
            onClick={() => refreshInsights()}
            disabled={refreshingInsights}
            className="btn-secondary py-2 px-4 flex items-center gap-2"
          >
            {refreshingInsights ? <Loader2 className="animate-spin h-5 w-5" /> : <Gauge className="h-5 w-5" />}
            Refresh Insights
          </button>
        </div>
      </div>

      {error && <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-6">{error}</div>}

      {!prediction ? (
        <div className="glass-card p-12 text-center">
          <Compass className="h-16 w-16 text-primary-500 mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-semibold mb-2">No Predictions Yet</h3>
          <p className="text-textMuted mb-6">Click generate prediction to analyze your profile.</p>
          <button onClick={handlePredict} disabled={predicting} className="btn-primary">
            {predicting ? 'Analyzing...' : 'Generate Prediction'}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid md:grid-cols-3 gap-6">
            {/* Probability Card */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="glass-card p-6 flex flex-col items-center justify-center relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary-500/10 to-transparent"></div>
              <h3 className="text-lg font-medium text-textMuted mb-2">Placement Probability</h3>
              <p className="text-xs text-textMuted mb-2">Weighted profile score</p>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="100%" barSize={20} data={radialData} startAngle={180} endAngle={0}>
                    <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                    <RadialBar minAngle={15} background clockWise dataKey="value" cornerRadius={10} />
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>
              <div className="absolute top-[60%] flex flex-col items-center">
                <span className="text-4xl font-bold text-white">{prediction.placement_probability}%</span>
              </div>
            </motion.div>

            {/* Expected Salary Card */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="glass-card p-6 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Briefcase className="h-5 w-5 text-green-400" />
                  <h3 className="text-lg font-medium text-textMuted">Expected Salary</h3>
                </div>
                <div className="mt-4">
                  <span className="text-5xl font-bold text-white">{prediction.salary_prediction}</span>
                  <span className="text-xl text-textMuted ml-2">LPA</span>
                </div>
              </div>
              <div className="mt-6 pt-4 border-t border-surfaceHighlight">
                <p className="text-sm text-textMuted flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  SVM Prediction: <strong className={prediction.svm_prediction === 1 ? 'text-green-400' : 'text-red-400'}>
                    {prediction.svm_prediction === 1 ? 'Placed' : 'Not Placed'}
                  </strong>
                </p>
              </div>
            </motion.div>

            {/* Cluster Analysis Card */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
              className="glass-card p-6 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <AlertCircle className="h-5 w-5 text-purple-400" />
                  <h3 className="text-lg font-medium text-textMuted">Student Cluster</h3>
                </div>
                <h4 className="text-2xl font-bold text-purple-300 bg-purple-500/10 inline-block px-4 py-2 rounded-lg border border-purple-500/20">
                  {prediction.student_cluster}
                </h4>
              </div>
              <div className="mt-6">
                <Link to="/roadmap" className="btn-primary w-full block text-center py-3">
                  View AI Roadmap
                </Link>
              </div>
            </motion.div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="glass-card p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <Gauge className="h-5 w-5 text-cyan-400" />
                <h3 className="text-lg font-medium text-textMuted">Resume Strength</h3>
              </div>
              <div className="text-5xl font-bold text-white">{resumeStrength}%</div>
              <p className="text-sm text-textMuted mt-3">{ats?.weaknesses?.[0] || 'Resume signals are ready for scoring.'}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(ats?.missing_sections || []).slice(0, 4).map((section) => (
                  <span key={section} className="px-3 py-1 rounded-full bg-red-500/10 text-red-300 text-xs border border-red-500/20">{section}</span>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="glass-card p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <Target className="h-5 w-5 text-emerald-400" />
                <h3 className="text-lg font-medium text-textMuted">Skill Gap</h3>
              </div>
              <div className="text-sm text-textMuted mb-3">Target: <span className="text-white">{skillGap?.target_role || 'Auto selected'}</span></div>
              <div className="flex flex-wrap gap-2">
                {missingSkills.slice(0, 6).map((skill) => (
                  <span key={skill} className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-200 text-xs border border-amber-500/20">{skill}</span>
                ))}
                {missingSkills.length === 0 && <span className="text-sm text-textMuted">No major required skill gaps found.</span>}
              </div>
              <p className="text-sm text-textMuted mt-4">Skill match: <span className="text-white font-semibold">{skillMatchScore}%</span></p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
              className="glass-card p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <Award className="h-5 w-5 text-yellow-400" />
                <h3 className="text-lg font-medium text-textMuted">Readiness Score</h3>
              </div>
              <div className="text-5xl font-bold text-white">{readinessScore}%</div>
              <p className="text-sm text-textMuted mt-3">
                Based on current skills versus {skillGap?.target_role || 'target role'} requirements.
              </p>
            </motion.div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="glass-card p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <Layers className="h-5 w-5 text-indigo-400" />
                <h3 className="text-lg font-medium text-textMuted">Domain Match</h3>
              </div>
              <div className="text-4xl font-bold text-white">{domainMatch?.match_percentage || 0}%</div>
              <p className="text-sm text-textMuted mt-2">{domainMatch?.domain_name || profile.interested_domain || 'No domain selected'}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(domainMatch?.matched_items || []).slice(0, 4).map((item) => (
                  <span key={item} className="px-3 py-1 rounded-full bg-primary-500/10 text-primary-300 text-xs border border-primary-500/20">{item}</span>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="glass-card p-6 lg:col-span-2"
            >
              <div className="flex items-center gap-2 mb-4">
                <Briefcase className="h-5 w-5 text-green-400" />
                <h3 className="text-lg font-medium text-textMuted">Role Recommendations</h3>
              </div>
              <div className="space-y-3">
                {roleRecommendations.map((role) => (
                  <div key={role.role_name} className="border border-surfaceHighlight rounded-lg p-3">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                      <div>
                        <p className="font-semibold text-white">{role.role_name}</p>
                        <p className="text-xs text-textMuted">{role.reasoning}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-bold text-primary-400">{role.match_percentage}%</p>
                        <p className="text-xs text-textMuted">{role.salary_range}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="glass-card p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <FileText className="h-5 w-5 text-sky-400" />
                <h3 className="text-lg font-medium text-textMuted">Resume Summary</h3>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><p className="text-textMuted">Resume</p><p className="font-semibold">{resumeSummary?.has_resume ? 'Uploaded' : 'Missing'}</p></div>
                <div><p className="text-textMuted">Skills</p><p className="font-semibold">{resumeSummary?.skills_count || 0}</p></div>
                <div><p className="text-textMuted">Languages</p><p className="font-semibold">{resumeSummary?.languages_count || 0}</p></div>
                <div><p className="text-textMuted">Certifications</p><p className="font-semibold">{resumeSummary?.certifications_count || 0}</p></div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="glass-card p-6 lg:col-span-2"
            >
              <h3 className="text-lg font-medium text-textMuted mb-4">Personalized Recommendations</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-semibold mb-2">ATS Improvements</p>
                  <ul className="space-y-2 text-sm text-textMuted">
                    {recommendations.slice(0, 4).map((item) => <li key={item}>{item}</li>)}
                  </ul>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-2">Courses and Certifications</p>
                  <ul className="space-y-2 text-sm text-textMuted">
                    {(skillGap?.recommended_courses || []).slice(0, 2).map((item) => <li key={item}>{item}</li>)}
                    {(skillGap?.recommended_certifications || []).slice(0, 2).map((item) => <li key={item}>{item}</li>)}
                  </ul>
                </div>
              </div>
            </motion.div>
          </div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-medium text-textMuted mb-6">Career Readiness Radar</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="metric" stroke="#94a3b8" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#475569" />
                  <Radar name="Readiness" dataKey="value" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.35} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
