def _unique(values):
    seen = set()
    result = []
    for value in values:
        text = str(value).strip()
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            result.append(text)
    return result


OPTION_CATALOG = {
    "skills": [
        "DSA", "System Design", "API Design", "API Development", "REST APIs",
        "Database Design", "Authentication", "Frontend Development", "Backend Development",
        "Responsive UI", "State Management", "Accessibility", "Performance Optimization",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Model Evaluation",
        "Feature Engineering", "MLOps", "Statistics", "Data Wrangling", "Experiment Design",
        "Data Cleaning", "Dashboarding", "Business Analysis", "SQL Analysis",
        "Network Security", "Threat Analysis", "Vulnerability Assessment", "Incident Response",
        "Cloud Architecture", "Networking", "Cost Optimization", "Security",
        "CI/CD", "Infrastructure as Code", "Monitoring", "Release Automation",
        "Mobile UI", "API Integration", "App Store Deployment", "Offline Storage",
        "Smart Contracts", "Token Standards", "Web3 Integration", "Security Auditing",
        "Game Mechanics", "Physics", "Level Design", "Optimization",
        "Testing", "Code Review", "Test Planning", "Automation Testing",
        "Bug Reporting", "Regression Testing", "Product Thinking", "Analytics",
        "User Research", "Full Stack Delivery",
    ],
    "programming_languages": [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "Go",
        "Rust", "SQL", "R", "Bash", "PowerShell", "YAML", "Kotlin", "Swift",
        "Dart", "Solidity", "Lua", "HTML", "CSS",
    ],
    "frameworks": [
        "Flask", "Django", "FastAPI", "Express.js", "Express", "Node.js",
        "Spring Boot", "React", "Next.js", "Angular", "Vue", "Bootstrap",
        "Tailwind CSS", "TensorFlow", "PyTorch", "Scikit-learn", "Keras",
        "Pandas", "NumPy", "Spark", "Serverless Framework", "CDK",
        "Ansible", "Helm", "Flutter", "React Native", "SwiftUI",
        "Jetpack Compose", "Ethers.js", "Web3.js", "OpenZeppelin",
        "Unity Engine", "Unreal Engine", "Godot", "Pytest", "JUnit",
        "Playwright", "TestNG",
    ],
    "tools": [
        "Git", "GitHub", "VS Code", "Postman", "Docker", "Figma",
        "IntelliJ IDEA", "Eclipse", "Jupyter Notebook", "Jupyter", "Linux",
        "MLflow", "Weights & Biases", "Tableau", "Power BI", "Excel",
        "Looker", "Wireshark", "Burp Suite", "Nmap", "Metasploit",
        "Terraform", "Jenkins", "GitHub Actions", "Android Studio",
        "Xcode", "Firebase", "Hardhat", "Truffle", "MetaMask",
        "Ganache", "Unity", "Unreal Engine", "Blender", "Jira",
        "PostHog", "Selenium", "Cypress", "Webpack", "Vite",
    ],
    "databases": ["MongoDB", "MySQL", "PostgreSQL", "SQLite", "Redis", "Oracle", "SQL Server", "DynamoDB", "Firebase Firestore"],
    "platforms": ["AWS", "Azure", "Google Cloud", "Vercel", "Netlify", "Render", "Heroku", "Kubernetes", "Docker Hub"],
    "technologies": [
        "LLMs", "Vector Databases", "ETL", "Big Data", "Data Pipelines",
        "Predictive Modeling", "Data Warehousing", "BI Reporting", "A/B Testing",
        "SIEM", "IAM", "Firewalls", "Zero Trust", "Containers",
        "Serverless", "Cloud Storage", "Observability", "Container Orchestration",
        "Cloud Platforms", "REST APIs", "Microservices", "Authentication",
        "SPA", "SSR", "Design Systems", "Web APIs", "OAuth",
        "Push Notifications", "Mobile Analytics", "Ethereum", "Polygon",
        "DeFi", "NFTs", "3D Rendering", "Animation", "Multiplayer",
        "AR/VR", "Distributed Systems", "APIs", "Experimentation",
        "Feature Flags", "API Testing", "Performance Testing", "CI Testing",
        "Manual Testing",
    ],
    "soft_skills": ["Communication", "Problem Solving", "Teamwork", "Leadership", "Adaptability", "Critical Thinking", "Time Management", "Collaboration"],
}


DOMAINS = {
    "Artificial Intelligence / Machine Learning": {
        "skills": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Model Evaluation"],
        "programming_languages": ["Python", "R", "SQL"],
        "tools": ["Jupyter Notebook", "Git", "MLflow", "Weights & Biases"],
        "frameworks": ["TensorFlow", "PyTorch", "Scikit-learn", "Keras"],
        "technologies": ["LLMs", "Vector Databases", "MLOps", "Feature Engineering"],
    },
    "Data Science": {
        "skills": ["Statistics", "Machine Learning", "Data Wrangling", "Experiment Design"],
        "programming_languages": ["Python", "R", "SQL"],
        "tools": ["Jupyter Notebook", "Tableau", "Power BI", "Git"],
        "frameworks": ["Pandas", "NumPy", "Scikit-learn", "Spark"],
        "technologies": ["Data Pipelines", "Predictive Modeling", "ETL", "Big Data"],
    },
    "Data Analytics": {
        "skills": ["Data Cleaning", "Dashboarding", "Business Analysis", "SQL Analysis"],
        "programming_languages": ["SQL", "Python", "R"],
        "tools": ["Excel", "Power BI", "Tableau", "Looker"],
        "frameworks": ["Pandas", "NumPy"],
        "technologies": ["ETL", "Data Warehousing", "BI Reporting", "A/B Testing"],
    },
    "Cyber Security": {
        "skills": ["Network Security", "Threat Analysis", "Vulnerability Assessment", "Incident Response"],
        "programming_languages": ["Python", "Bash", "PowerShell", "SQL"],
        "tools": ["Wireshark", "Burp Suite", "Nmap", "Metasploit"],
        "frameworks": ["MITRE ATT&CK", "OWASP"],
        "technologies": ["SIEM", "IAM", "Firewalls", "Zero Trust"],
    },
    "Cloud Computing": {
        "skills": ["Cloud Architecture", "Networking", "Cost Optimization", "Security"],
        "programming_languages": ["Python", "Go", "Bash"],
        "tools": ["Terraform"],
        "frameworks": ["Serverless Framework", "CDK"],
        "platforms": ["AWS", "Azure", "Google Cloud"],
        "technologies": ["Containers", "Kubernetes", "Serverless", "Cloud Storage"],
    },
    "DevOps": {
        "skills": ["CI/CD", "Infrastructure as Code", "Monitoring", "Release Automation"],
        "programming_languages": ["Python", "Go", "Bash", "YAML"],
        "tools": ["Docker", "Jenkins", "GitHub Actions"],
        "frameworks": ["Terraform", "Ansible", "Helm"],
        "platforms": ["Kubernetes"],
        "technologies": ["Observability", "Container Orchestration", "Linux", "Cloud Platforms"],
    },
    "Full Stack Development": {
        "skills": ["API Design", "Frontend Development", "Backend Development", "Database Design"],
        "programming_languages": ["JavaScript", "TypeScript", "Python", "Java"],
        "tools": ["Git", "Postman", "Docker", "VS Code"],
        "frameworks": ["React", "Node.js", "Express", "Flask"],
        "databases": ["MongoDB"],
        "technologies": ["REST APIs", "SQL", "Authentication"],
    },
    "Frontend Development": {
        "skills": ["Responsive UI", "State Management", "Accessibility", "Performance Optimization"],
        "programming_languages": ["JavaScript", "TypeScript", "HTML", "CSS"],
        "tools": ["Vite", "Webpack", "Figma", "Git"],
        "frameworks": ["React", "Vue", "Angular", "Tailwind CSS"],
        "technologies": ["SPA", "SSR", "Design Systems", "Web APIs"],
    },
    "Backend Development": {
        "skills": ["API Development", "Database Design", "Authentication", "System Design"],
        "programming_languages": ["Python", "Java", "JavaScript", "Go"],
        "tools": ["Postman", "Docker", "Git"],
        "frameworks": ["Flask", "Django", "Express", "Spring Boot"],
        "databases": ["MongoDB", "Redis"],
        "technologies": ["REST APIs", "Microservices", "SQL"],
    },
    "Mobile App Development": {
        "skills": ["Mobile UI", "API Integration", "App Store Deployment", "Offline Storage"],
        "programming_languages": ["Kotlin", "Swift", "Dart", "JavaScript"],
        "tools": ["Android Studio", "Xcode", "Git"],
        "frameworks": ["Flutter", "React Native", "SwiftUI", "Jetpack Compose"],
        "platforms": ["Firebase"],
        "databases": ["SQLite"],
        "technologies": ["Push Notifications", "Mobile Analytics", "OAuth"],
    },
    "Blockchain": {
        "skills": ["Smart Contracts", "Token Standards", "Web3 Integration", "Security Auditing"],
        "programming_languages": ["Solidity", "JavaScript", "TypeScript", "Rust"],
        "tools": ["Hardhat", "Truffle", "MetaMask", "Ganache"],
        "frameworks": ["Ethers.js", "Web3.js", "OpenZeppelin"],
        "technologies": ["Ethereum", "Polygon", "DeFi", "NFTs"],
    },
    "Game Development": {
        "skills": ["Game Mechanics", "Physics", "Level Design", "Optimization"],
        "programming_languages": ["C#", "C++", "JavaScript", "Lua"],
        "tools": ["Unity", "Unreal Engine", "Blender", "Git"],
        "frameworks": ["Unity Engine", "Unreal Engine", "Godot"],
        "technologies": ["3D Rendering", "Animation", "Multiplayer", "AR/VR"],
    },
    "Software Engineering": {
        "skills": ["DSA", "System Design", "Testing", "Code Review"],
        "programming_languages": ["Java", "Python", "C++", "JavaScript"],
        "tools": ["Git", "Docker", "Linux", "Postman"],
        "frameworks": ["Spring Boot", "Flask", "React", "Express"],
        "technologies": ["Distributed Systems", "APIs", "CI/CD"],
    },
    "Product Engineering": {
        "skills": ["Product Thinking", "Full Stack Delivery", "Analytics", "User Research"],
        "programming_languages": ["JavaScript", "TypeScript", "Python", "SQL"],
        "tools": ["Figma", "PostHog", "Git", "Jira"],
        "frameworks": ["React", "Node.js", "Next.js", "Flask"],
        "technologies": ["Experimentation", "Feature Flags", "Analytics", "APIs"],
    },
    "QA / Testing": {
        "skills": ["Test Planning", "Automation Testing", "Bug Reporting", "Regression Testing"],
        "programming_languages": ["Java", "Python", "JavaScript", "SQL"],
        "tools": ["Selenium", "Postman", "Jira", "Cypress"],
        "frameworks": ["Pytest", "JUnit", "Playwright", "TestNG"],
        "technologies": ["API Testing", "Performance Testing", "CI Testing", "Manual Testing"],
    },
}


def get_domains_payload():
    return [{"name": name, **metadata} for name, metadata in DOMAINS.items()]


def get_option_catalog():
    catalog = {key: list(values) for key, values in OPTION_CATALOG.items()}
    for metadata in DOMAINS.values():
        for field in catalog:
            catalog[field] = _unique([*catalog[field], *metadata.get(field, [])])
    return catalog


DEFAULT_CERTIFICATIONS = {
    "Artificial Intelligence / Machine Learning": ["TensorFlow Developer Certificate", "Microsoft Azure AI Fundamentals", "AWS Machine Learning Specialty"],
    "Data Science": ["IBM Data Science Professional Certificate", "Google Advanced Data Analytics", "Microsoft Azure Data Scientist"],
    "Data Analytics": ["Google Data Analytics Professional Certificate", "Microsoft Power BI Data Analyst", "Tableau Desktop Specialist"],
    "Cyber Security": ["CompTIA Security+", "Certified Ethical Hacker", "Google Cybersecurity Certificate"],
    "Cloud Computing": ["AWS Cloud Practitioner", "Azure Fundamentals", "Google Associate Cloud Engineer"],
    "DevOps": ["Docker Certified Associate", "Certified Kubernetes Application Developer", "HashiCorp Terraform Associate"],
    "Full Stack Development": ["Meta Full-Stack Engineer Certificate", "MongoDB Developer Certification", "AWS Cloud Practitioner"],
    "Frontend Development": ["Meta Front-End Developer Certificate", "freeCodeCamp Front End Libraries", "Google UX Design Certificate"],
    "Backend Development": ["Meta Back-End Developer Certificate", "MongoDB Developer Certification", "AWS Developer Associate"],
    "Mobile App Development": ["Meta React Native Certificate", "Google Associate Android Developer", "Flutter Certified Application Developer"],
    "Blockchain": ["Certified Blockchain Developer", "Ethereum Developer Certification", "Blockchain Council Certification"],
    "Game Development": ["Unity Certified User", "Unreal Engine Certification", "Game Design and Development Specialization"],
    "Software Engineering": ["Oracle Java Certification", "AWS Developer Associate", "ISTQB Foundation"],
    "Product Engineering": ["Scrum Master Certification", "Google UX Design Certificate", "Product Analytics Certification"],
    "QA / Testing": ["ISTQB Foundation", "Certified Selenium Tester", "Postman API Fundamentals"],
}


DOMAIN_ALIASES = {
    "AI/ML": "Artificial Intelligence / Machine Learning",
    "Software Development": "Software Engineering",
    "Frontend": "Frontend Development",
    "Backend": "Backend Development",
    "Full Stack": "Full Stack Development",
    "Mobile Development": "Mobile App Development",
    "Testing": "QA / Testing",
    "UI/UX": "Product Engineering",
}


for domain_name, metadata in list(DOMAINS.items()):
    metadata.setdefault("certifications", DEFAULT_CERTIFICATIONS.get(domain_name, []))

for alias, source_name in DOMAIN_ALIASES.items():
    source = DOMAINS[source_name]
    DOMAINS.setdefault(alias, {key: list(value) for key, value in source.items()})
