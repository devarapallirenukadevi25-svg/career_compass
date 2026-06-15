import { useCallback, useEffect, useState } from 'react';
import { useFieldArray, useForm, useWatch } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Loader2, Save, Upload } from 'lucide-react';
import { motion } from 'framer-motion';

const DEFAULT_DOMAINS = [
  'Artificial Intelligence / Machine Learning',
  'AI/ML',
  'Data Science',
  'Data Analytics',
  'Cyber Security',
  'Cloud Computing',
  'DevOps',
  'Software Development',
  'Full Stack Development',
  'Full Stack',
  'Frontend Development',
  'Frontend',
  'Backend Development',
  'Backend',
  'Mobile App Development',
  'Mobile Development',
  'Blockchain',
  'Game Development',
  'Testing',
  'UI/UX',
  'Software Engineering',
  'Product Engineering',
  'QA / Testing',
].map((name) => ({ name, skills: [], programming_languages: [], frameworks: [], tools: [], technologies: [], certifications: [] }));

const DEFAULT_OPTIONS = {
  skills: [],
  programming_languages: ['Python', 'Java', 'C', 'C++', 'JavaScript', 'TypeScript', 'Go', 'Rust'],
  frameworks: ['Flask', 'Django', 'FastAPI', 'Express.js', 'Spring Boot', 'React', 'Next.js', 'Angular', 'Vue', 'Bootstrap', 'Tailwind CSS'],
  tools: ['Git', 'GitHub', 'VS Code', 'Postman', 'Docker', 'Figma', 'IntelliJ IDEA', 'Eclipse', 'Jupyter Notebook', 'Linux'],
  databases: ['MongoDB', 'MySQL', 'PostgreSQL', 'SQLite', 'Redis'],
  platforms: [],
  technologies: [],
  soft_skills: ['Communication', 'Problem Solving', 'Teamwork'],
  education: [],
  certifications: [],
  achievements: [],
  hackathons: [],
};

const STRUCTURED_FIELD_META = {
  certifications: {
    empty: { name: '', issuer: '', year: '' },
    fields: [
      { key: 'name', label: 'Certificate name', type: 'text', placeholder: 'e.g. AWS Cloud Practitioner' },
      { key: 'issuer', label: 'Issuer', type: 'text', placeholder: 'e.g. Amazon Web Services' },
      { key: 'year', label: 'Year', type: 'number', placeholder: 'e.g. 2025' },
    ],
  },
  achievements: {
    empty: { title: '', description: '', year: '' },
    fields: [
      { key: 'title', label: 'Achievement', type: 'text', placeholder: 'e.g. Hackathon finalist' },
      { key: 'description', label: 'Details', type: 'text', placeholder: 'Short description of the achievement' },
      { key: 'year', label: 'Year', type: 'number', placeholder: 'e.g. 2025' },
    ],
  },
  hackathons: {
    empty: { name: '', position: '', year: '' },
    fields: [
      { key: 'name', label: 'Hackathon name', type: 'text', placeholder: 'e.g. Smart India Hackathon' },
      { key: 'position', label: 'Position', type: 'text', placeholder: 'e.g. Winner / Finalist / Participant' },
      { key: 'year', label: 'Year', type: 'number', placeholder: 'e.g. 2025' },
    ],
  },
};

const ARRAY_FIELDS = [
  'skills',
  'programming_languages',
  'frameworks',
  'tools',
  'databases',
  'platforms',
  'technologies',
  'soft_skills',
  'education',
  'certifications',
  'achievements',
  'hackathons',
];

const emptyProfile = {
  cgpa: '',
  leetcode: '',
  codechef_rating: '',
  codeforces_rating: '',
  github_activity: '',
  projects: '',
  project_complexity: '',
  internships: '',
  communication: '',
  degree: '',
  branch: '',
  skills: [],
  interested_domain: '',
  programming_languages: [],
  frameworks: [],
  tools: [],
  databases: [],
  platforms: [],
  technologies: [],
  soft_skills: [],
  education: [],
  certifications: [],
  achievements: [],
  hackathons: [],
  github_profile: '',
  linkedin_profile: '',
  resume_url: '',
  resume_text: '',
  ats_score: 0,
};

function toList(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  return String(value)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function mergeUnique(...lists) {
  const seen = new Set();
  const merged = [];
  lists.flat().forEach((item) => {
    const value = String(item).trim();
    const key = value.toLowerCase();
    if (value && !seen.has(key)) {
      seen.add(key);
      merged.push(value);
    }
  });
  return merged;
}

function normalizeStructuredItems(field, value) {
  const meta = STRUCTURED_FIELD_META[field];
  const list = Array.isArray(value) ? value : (value ? [value] : []);
  const seen = new Set();
  const normalized = [];

  list.forEach((item) => {
    const base = { ...meta.empty, ...(item && typeof item === 'object' ? item : {}) };
    const cleaned = {};
    Object.entries(base).forEach(([key, raw]) => {
      const text = String(raw ?? '').trim();
      if (!text) return;
      cleaned[key] = key === 'year' && /^\d{4}$/.test(text) ? Number(text) : text;
    });

    const primaryKey = String(cleaned[meta.fields[0].key] || '').trim();
    if (!primaryKey) return;

    const dedupeKey = meta.fields.map((fieldDef) => String(cleaned[fieldDef.key] || '').toLowerCase()).join('|');
    if (seen.has(dedupeKey)) return;
    seen.add(dedupeKey);
    normalized.push(cleaned);
  });

  return normalized;
}

function compactStructuredItems(field, value) {
  return normalizeStructuredItems(field, value).map((item) => {
    const compact = {};
    Object.entries(item).forEach(([key, raw]) => {
      if (raw === '' || raw === null || raw === undefined) return;
      compact[key] = raw;
    });
    return compact;
  });
}

function StructuredFieldGroup({ title, field, register, control }) {
  const { fields, append, remove } = useFieldArray({ control, name: field });
  const meta = STRUCTURED_FIELD_META[field];

  useEffect(() => {
    if (fields.length === 0) {
      append({ ...meta.empty });
    }
  }, [append, fields.length, meta.empty]);

  return (
    <div>
      <div className="flex items-center justify-between gap-3 mb-3">
        <label className="block text-sm font-medium">{title}</label>
        <button
          type="button"
          onClick={() => append({ ...meta.empty })}
          className="text-sm text-primary-400 hover:text-primary-300"
        >
          Add {title.slice(0, -1)}
        </button>
      </div>
      <div className="space-y-3">
        {fields.map((item, index) => (
          <div key={item.id} className="border border-surfaceHighlight rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-medium text-textMuted">Entry {index + 1}</p>
              {fields.length > 1 && (
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="text-xs text-red-300 hover:text-red-200"
                >
                  Remove
                </button>
              )}
            </div>
            <div className="grid md:grid-cols-3 gap-3">
              {meta.fields.map((fieldDef) => (
                <div key={fieldDef.key}>
                  <label className="block text-xs font-medium mb-2 text-textMuted">{fieldDef.label}</label>
                  <input
                    type={fieldDef.type}
                    className="input-field"
                    placeholder={fieldDef.placeholder}
                    {...register(`${field}.${index}.${fieldDef.key}`)}
                  />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Profile() {
  const { register, handleSubmit, setValue, control, reset, getValues, formState: { errors } } = useForm({
    defaultValues: emptyProfile,
  });

  const [domains, setDomains] = useState(DEFAULT_DOMAINS);
  const [optionCatalog, setOptionCatalog] = useState(DEFAULT_OPTIONS);
  const [isLoading, setIsLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeSummary, setResumeSummary] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const selectedDomainName = useWatch({ control, name: 'interested_domain' }) || '';
  const watchedArrays = {
    skills: useWatch({ control, name: 'skills' }) || [],
    programming_languages: useWatch({ control, name: 'programming_languages' }) || [],
    frameworks: useWatch({ control, name: 'frameworks' }) || [],
    tools: useWatch({ control, name: 'tools' }) || [],
    databases: useWatch({ control, name: 'databases' }) || [],
    platforms: useWatch({ control, name: 'platforms' }) || [],
    technologies: useWatch({ control, name: 'technologies' }) || [],
    soft_skills: useWatch({ control, name: 'soft_skills' }) || [],
    education: useWatch({ control, name: 'education' }) || [],
  };

  const hydrateProfile = useCallback((profile) => {
    const nextProfile = { ...emptyProfile, ...profile };
    ARRAY_FIELDS.forEach((field) => {
      nextProfile[field] = STRUCTURED_FIELD_META[field]
        ? normalizeStructuredItems(field, nextProfile[field])
        : toList(nextProfile[field]);
    });
    nextProfile.communication = profile.communication ?? profile.communication_score ?? '';
    reset(nextProfile);
  }, [reset]);

  const fetchProfile = useCallback(async () => {
    try {
      const res = await api.get('/profile');
      hydrateProfile(res.data || {});
    } catch (err) {
      if (err.response?.status !== 404) {
        setError('Failed to load profile data');
      }
    }
  }, [hydrateProfile]);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const domainsRes = await api.get('/profile/domains');
        setDomains(domainsRes.data.domains || DEFAULT_DOMAINS);
        setOptionCatalog({ ...DEFAULT_OPTIONS, ...(domainsRes.data.options || {}) });
      } catch {
        setDomains(DEFAULT_DOMAINS);
        setOptionCatalog(DEFAULT_OPTIONS);
      }

      await fetchProfile();
      setFetching(false);
    };

    loadInitialData();
  }, [fetchProfile]);

  const toggleValue = (field, value) => {
    const current = toList(getValues(field));
    if (current.includes(value)) {
      setValue(field, current.filter((item) => item !== value), { shouldDirty: true });
    } else {
      setValue(field, [...current, value], { shouldDirty: true });
    }
  };

  const handleDomainChange = (event) => {
    const domainName = event.target.value;
    setValue('interested_domain', domainName, { shouldDirty: true });
  };

  const buildProfilePayload = (data) => {
    const payload = {
      ...data,
      interested_domain: getValues('interested_domain'),
      resume_url: getValues('resume_url'),
      resume_text: getValues('resume_text'),
      ats_score: getValues('ats_score'),
      communication_score: data.communication,
    };
    ARRAY_FIELDS.forEach((field) => {
      payload[field] = STRUCTURED_FIELD_META[field]
        ? compactStructuredItems(field, getValues(field))
        : toList(getValues(field));
    });

    return payload;
  };

  const uploadSelectedResume = async () => {
    if (!resumeFile) return null;

    const formData = new FormData();
    formData.append('resume', resumeFile);
    const res = await api.post('/profile/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    setResumeSummary(res.data.extracted);
    setResumeFile(null);
    if (res.data.profile) {
      hydrateProfile(res.data.profile);
    }
    return res.data;
  };

  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await api.post('/profile', buildProfilePayload(data));
      if (res.data.profile) {
        hydrateProfile(res.data.profile);
      }
      setSuccess('Profile updated successfully.');
      setTimeout(() => navigate('/dashboard'), 1200);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResumeUpload = async () => {
    if (!resumeFile) {
      setError('Choose a PDF resume first.');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');
    setResumeSummary(null);

    try {
      const uploadResult = await uploadSelectedResume();
      if (!uploadResult?.profile) {
        await fetchProfile();
      }
      setSuccess('Resume analyzed and profile fields pre-filled.');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to analyze resume');
    } finally {
      setUploading(false);
    }
  };

  const renderChipGroup = (title, field, options) => {
    const values = toList(watchedArrays[field]);
    const allOptions = mergeUnique(options, values);

    return (
      <div>
        <label className="block text-sm font-medium mb-3">{title}</label>
        <div className="flex flex-wrap gap-3">
          {allOptions.map((option) => (
            <button
              key={`${field}-${option}`}
              type="button"
              onClick={() => toggleValue(field, option)}
              className={`px-4 py-2 rounded-full border transition-all ${
                values.includes(option)
                  ? 'bg-primary-500/20 border-primary-500 text-primary-400'
                  : 'bg-surface border-surfaceHighlight text-textMuted hover:border-textMuted'
              }`}
            >
              {option}
            </button>
          ))}
        </div>
        {values.length > 0 && (
          <p className="text-xs text-textMuted mt-3">Selected: {values.join(', ')}</p>
        )}
      </div>
    );
  };

  if (fetching) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-4rem)]">
        <Loader2 className="animate-spin h-8 w-8 text-primary-500" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 md:p-8"
      >
        <h2 className="text-3xl font-bold mb-2">Student Profile</h2>
        <p className="text-textMuted mb-8">Update your academic details, target domain, skills, and resume analysis inputs.</p>

        {error && <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-6">{error}</div>}
        {success && <div className="bg-green-500/10 border border-green-500/50 text-green-500 px-4 py-3 rounded-lg mb-6">{success}</div>}

        <div className="glass-panel p-5 mb-8">
          <div className="flex flex-col md:flex-row md:items-end gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">Upload Resume (PDF)</label>
              <input
                type="file"
                accept="application/pdf,.pdf"
                className="input-field"
                onChange={(event) => setResumeFile(event.target.files?.[0] || null)}
              />
            </div>
            <button type="button" onClick={handleResumeUpload} disabled={uploading} className="btn-secondary flex items-center justify-center gap-2">
              {uploading ? <Loader2 className="animate-spin h-5 w-5" /> : <Upload className="h-5 w-5" />}
              Analyze Resume
            </button>
          </div>

          {resumeSummary && (
            <div className="mt-4 text-sm text-textMuted">
              Extracted {resumeSummary.skills?.length || 0} skills, {resumeSummary.programming_languages?.length || 0} languages,
              {` ${resumeSummary.frameworks?.length || 0}`} frameworks, and {resumeSummary.certifications?.length || 0} certifications.
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          <div className="grid md:grid-cols-2 gap-6">
            <input type="hidden" {...register('interested_domain')} />
            <input type="hidden" {...register('resume_url')} />
            <input type="hidden" {...register('resume_text')} />
            <input type="hidden" {...register('ats_score')} />
            <input type="hidden" {...register('education')} />

            <div>
              <label className="block text-sm font-medium mb-2">CGPA (0-10)</label>
              <input type="number" step="0.01" min="0" max="10" className="input-field" {...register('cgpa', { required: 'CGPA is required', min: 0, max: 10 })} />
              {errors.cgpa && <p className="text-red-400 text-sm mt-1">{errors.cgpa.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Degree</label>
              <input type="text" className="input-field" placeholder="e.g. B.Tech" {...register('degree')} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Branch</label>
              <input type="text" className="input-field" placeholder="e.g. Computer Science" {...register('branch')} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">LeetCode Problems Solved</label>
              <input type="number" min="0" className="input-field" {...register('leetcode', { required: 'LeetCode count is required', min: 0 })} />
              {errors.leetcode && <p className="text-red-400 text-sm mt-1">{errors.leetcode.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">CodeChef Rating</label>
              <input type="number" min="0" className="input-field" {...register('codechef_rating', { min: 0 })} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Codeforces Rating</label>
              <input type="number" min="0" className="input-field" {...register('codeforces_rating', { min: 0 })} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">GitHub Activity Score (0-100)</label>
              <input type="number" min="0" max="100" className="input-field" {...register('github_activity', { min: 0, max: 100 })} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Number of Projects</label>
              <input type="number" min="0" className="input-field" {...register('projects', { required: 'Projects count is required', min: 0 })} />
              {errors.projects && <p className="text-red-400 text-sm mt-1">{errors.projects.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Project Complexity</label>
              <select className="input-field" {...register('project_complexity')}>
                <option value="">Select complexity</option>
                <option value="basic">Basic</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Number of Internships</label>
              <input type="number" min="0" className="input-field" {...register('internships', { required: 'Internships count is required', min: 0 })} />
              {errors.internships && <p className="text-red-400 text-sm mt-1">{errors.internships.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Communication Score (1-10)</label>
              <input type="number" min="1" max="10" className="input-field" {...register('communication', { required: 'Communication score is required', min: 1, max: 10 })} />
              {errors.communication && <p className="text-red-400 text-sm mt-1">{errors.communication.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Interested Domain</label>
              <select className="input-field" value={selectedDomainName} onChange={handleDomainChange}>
                <option value="">Select a domain</option>
                {domains.map((domain) => (
                  <option key={domain.name} value={domain.name}>{domain.name}</option>
                ))}
              </select>
            </div>
          </div>

          {renderChipGroup('Technical Skills', 'skills', optionCatalog.skills)}
          {renderChipGroup('Programming Languages', 'programming_languages', optionCatalog.programming_languages)}
          {renderChipGroup('Frameworks', 'frameworks', optionCatalog.frameworks)}
          {renderChipGroup('Tools', 'tools', optionCatalog.tools)}
          {renderChipGroup('Databases', 'databases', optionCatalog.databases)}
          {renderChipGroup('Platforms', 'platforms', optionCatalog.platforms)}
          {renderChipGroup('Technologies', 'technologies', optionCatalog.technologies)}
          {renderChipGroup('Soft Skills', 'soft_skills', optionCatalog.soft_skills)}
          <StructuredFieldGroup
            title="Certifications"
            field="certifications"
            register={register}
            control={control}
          />
          <StructuredFieldGroup
            title="Achievements"
            field="achievements"
            register={register}
            control={control}
          />
          <StructuredFieldGroup
            title="Hackathons"
            field="hackathons"
            register={register}
            control={control}
          />

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">GitHub Profile</label>
              <input type="url" className="input-field" placeholder="https://github.com/username" {...register('github_profile')} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">LinkedIn Profile</label>
              <input type="url" className="input-field" placeholder="https://linkedin.com/in/username" {...register('linkedin_profile')} />
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <button type="submit" className="btn-primary flex items-center gap-2 px-8" disabled={isLoading}>
              {isLoading ? <Loader2 className="animate-spin h-5 w-5" /> : <Save className="h-5 w-5" />}
              Save Profile
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
