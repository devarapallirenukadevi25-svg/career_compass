# Career Compass Pro API Documentation

Base URL: `/api`

All routes below require a JWT bearer token unless noted.

## Existing Routes

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Profile
- `GET /profile`
- `POST /profile`
- `GET /profile/domains`
- `POST /profile/resume`

### Prediction
- `POST /predict`
- `GET /predict/history`

### Roadmap
- `POST /roadmap`
- `GET /roadmap/latest`

## Career Compass Pro Routes

### `GET /insights/roles`
Returns supported target roles for skill gap analysis.

Response:
```json
{
  "roles": ["ML Engineer", "Data Scientist", "Backend Developer"]
}
```

### `GET /insights/ats`
Calculates the current user's ATS score, saves it to the profile, and appends an ATS history record.

Response:
```json
{
  "ats_score": 76,
  "strengths": ["GitHub profile is available"],
  "weaknesses": ["Project portfolio can be stronger"],
  "missing_sections": ["Certifications"],
  "improvement_suggestions": ["Add one recognized certification for the selected domain"]
}
```

### `POST /insights/ats`
Same behavior as `GET /insights/ats`. Kept for command-style clients that prefer explicit recalculation.

### `GET /insights/ats/history`
Returns the 20 most recent ATS snapshots.

### `GET /insights/skill-gap?target_role=Backend%20Developer`
Returns skill gap analysis for a target role. If `target_role` is omitted, the backend uses the top recommended role.

### `POST /insights/skill-gap`
Request:
```json
{
  "target_role": "Backend Developer"
}
```

Response:
```json
{
  "target_role": "Backend Developer",
  "current_skills": ["API Development", "Database Design"],
  "missing_skills": ["System Design"],
  "recommended_courses": ["Backend API Design"],
  "recommended_certifications": ["Meta Back-End Developer Certificate"],
  "readiness_score": 60
}
```

### `GET /insights/role-recommendations`
Returns the top 5 role recommendations.

Response:
```json
{
  "recommendations": [
    {
      "role_name": "Backend Developer",
      "match_percentage": 92,
      "salary_range": "6-18 LPA",
      "reasoning": "Matches API Development, Database Design; Aligned with selected domain"
    }
  ]
}
```

### `GET /insights/domain-match`
Returns the user's strongest selected-domain match.

### `GET /insights/summary?target_role=Backend%20Developer`
Aggregates ATS, skill gap, role recommendations, domain match, and resume summary for dashboard use.

Response:
```json
{
  "ats": {},
  "skill_gap": {},
  "role_recommendations": [],
  "domain_match": {},
  "resume_summary": {}
}
```

## MongoDB Collections

- `users`
- `profiles`
- `predictions`
- `roadmaps`
- `ats_history`
