from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import PyPDF2
from docx import Document
import re

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config.update({
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SECURE': os.getenv('SESSION_COOKIE_SECURE', 'false').lower() in ('1', 'true', 'yes'),
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'PREFERRED_URL_SCHEME': os.getenv('PREFERRED_URL_SCHEME', 'https')
})
if os.getenv('ENABLE_PROXY_FIX', 'false').lower() in ('1', 'true', 'yes'):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)


# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Sample data for testing
RESUME_SKILLS = [
    'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Ruby', 'SQL', 'NoSQL',
    'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Flask', 'Django',
    'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'TensorFlow', 'PyTorch', 'Git', 'CI/CD'
]

RESUME_KEYWORDS = [
    'machine learning', 'data analysis', 'web development', 'cloud computing', 'microservices',
    'api development', 'automation', 'testing', 'agile methodology', 'devops',
    'continuous integration', 'technical leadership', 'performance optimization',
    'user experience', 'cybersecurity'
]

SAMPLE_INTERVIEW_QUESTIONS = {
    'technical': [
        {'question': 'Explain the difference between supervised and unsupervised learning.', 'difficulty': 'Medium'},
        {'question': 'How does garbage collection work in Python?', 'difficulty': 'Hard'},
        {'question': 'What is REST API?', 'difficulty': 'Easy'}
    ],
    'hr': [
        {'question': 'Tell me about a time you faced a challenge at work.', 'difficulty': 'Medium'},
        {'question': 'Why do you want to work here?', 'difficulty': 'Easy'},
        {'question': 'Where do you see yourself in 5 years?', 'difficulty': 'Medium'}
    ]
}

INTERVIEW_DOMAIN_KEYWORDS = {
    'machine learning': 'Machine Learning',
    'data science': 'Data Science',
    'web development': 'Web Development',
    'frontend': 'Frontend Development',
    'backend': 'Backend Development',
    'devops': 'DevOps',
    'cloud': 'Cloud Engineering',
    'cybersecurity': 'Cybersecurity',
    'product': 'Product Development'
}

TECHNICAL_QUESTION_TEMPLATES = [
    {'template': 'Explain the core principles of {topic} and describe how you applied them in a project.', 'difficulty': 'Medium'},
    {'template': 'Describe a challenging {topic} problem you solved and the outcome of your approach.', 'difficulty': 'Hard'},
    {'template': 'How do you design scalable {topic} systems that meet performance and reliability goals?', 'difficulty': 'Hard'},
    {'template': 'What are the key tools and technologies you use for {topic} implementation?', 'difficulty': 'Easy'}
]

HR_QUESTION_TEMPLATES = [
    {'question': 'Describe a time when you led a project from concept to delivery.', 'difficulty': 'Medium'},
    {'question': 'How do you handle competing priorities and tight deadlines?', 'difficulty': 'Easy'},
    {'question': 'Tell me about a situation where you improved collaboration across teams.', 'difficulty': 'Medium'},
    {'question': 'How do you stay motivated during long-term or ambiguous projects?', 'difficulty': 'Medium'}
]

SAMPLE_FEEDBACK = [
    'Add more quantifiable achievements in your experience section.',
    'Include keywords like "agile methodology" and "scrum" for better ATS matching.',
    'Strengthen your project descriptions with specific technologies used.',
    'Consider adding certifications in cloud computing.'
]

SAMPLE_PORTFOLIO = {
    'github': 'https://github.com/username',
    'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'Docker'],
    'projects': [
        {'name': 'AI Resume Analyzer', 'description': 'Web app for resume analysis', 'tech': ['Flask', 'JavaScript']},
        {'name': 'E-commerce Platform', 'description': 'Full-stack online store', 'tech': ['React', 'Node.js']}
    ]
}

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def normalize_text(text):
    return re.sub(r'[^a-z0-9\s]', ' ', text.lower())

SKILL_CATEGORIES = {
    'Programming Languages': ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Ruby', 'SQL', 'HTML', 'CSS'],
    'Frameworks & Tools': ['React', 'Angular', 'Vue', 'Node.js', 'Express', 'Flask', 'Django', 'Docker', 'Kubernetes', 'TensorFlow', 'PyTorch', 'Git', 'CI/CD'],
    'Databases': ['MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Redis', 'Oracle', 'SQL Server', 'NoSQL'],
    'Other Technologies': ['AWS', 'Azure', 'GCP', 'REST', 'GraphQL', 'Microservices', 'DevOps', 'Containerization']
}

SOFT_SKILLS = [
    'leadership', 'communication', 'teamwork', 'collaboration', 'problem solving', 'critical thinking',
    'adaptability', 'time management', 'attention to detail', 'project management', 'strategic planning', 'creative'
]

DOMAIN_KEYWORDS = {
    'Machine Learning / AI': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'scikit-learn'],
    'Data Science': ['data analysis', 'data science', 'statistics', 'data modeling', 'data visualization', 'pandas', 'numpy'],
    'Web Development': ['web development', 'frontend', 'backend', 'full stack', 'html', 'css', 'javascript', 'react', 'angular', 'vue'],
    'Cloud & DevOps': ['aws', 'azure', 'gcp', 'kubernetes', 'docker', 'ci/cd', 'devops', 'cloud computing'],
    'Software Engineering': ['software engineering', 'architecture', 'system design', 'microservices', 'api development', 'backend', 'frontend'],
    'Cybersecurity': ['cybersecurity', 'security', 'penetration testing', 'vulnerability', 'network security']
}

PROJECT_IMPACT_TERMS = [
    'improved', 'reduced', 'increased', 'automated', 'deployed', 'optimized', 'scaled', 'accelerated', 'enabled', 'designed', 'built'
]


def extract_projects(text):
    lines = text.splitlines()
    project_sections = []

    for i, line in enumerate(lines):
        if re.search(r'\bProject(?:s)?\b', line, re.IGNORECASE):
            title = line.strip()
            block = []
            for j in range(i + 1, len(lines)):
                if not lines[j].strip():
                    break
                block.append(lines[j].strip())
            if block:
                project_sections.append((title, block))

    if not project_sections:
        project_matches = re.findall(r'Project[s]?:\s*([^\n\r]+)', text, re.IGNORECASE)
        if not project_matches:
            project_matches = re.findall(r'\b([A-Z][A-Za-z0-9\s\-]{8,60})\b(?=\s*(?:project|application|platform|system))', text)
        return [{
            'title': p.strip(),
            'purpose': p.strip(),
            'technologies': [],
            'impact': 'Project details are limited in the resume.',
            'strengths': []
        } for p in project_matches if len(p.strip()) > 5][:4]

    projects = []
    normalized_text = normalize_text(text)
    for title, block in project_sections:
        description = ' '.join(block)
        purpose = block[0] if block else title
        technologies = []
        for category, terms in SKILL_CATEGORIES.items():
            for term in terms:
                if re.search(r'\b' + re.escape(term.lower()) + r'\b', normalize_text(description)):
                    technologies.append(term)
        if not technologies:
            technologies = [skill for skill in RESUME_SKILLS if re.search(r'\b' + re.escape(skill.lower()) + r'\b', normalized_text)][:5]

        impact_text = next((line for line in block if any(re.search(r'\b' + term + r'\b', line, re.IGNORECASE) for term in PROJECT_IMPACT_TERMS)),
                           'Delivered measurable improvements through project execution.')
        strengths = []
        if any(re.search(r'\b' + term + r'\b', description, re.IGNORECASE) for term in PROJECT_IMPACT_TERMS):
            strengths.append('Strong focus on business impact and measurable results.')
        if technologies:
            strengths.append('Utilizes relevant technologies and modern toolchains.')
        if len(block) > 1:
            strengths.append('Includes a clear implementation narrative and outcome statements.')
        if not strengths:
            strengths.append('Project description conveys real technical ownership and delivery.')

        projects.append({
            'title': title,
            'purpose': purpose,
            'technologies': sorted(set(technologies))[:6],
            'impact': impact_text,
            'strengths': strengths
        })

    return projects[:4]


def detect_education(text):
    education_matches = re.findall(r'((?:Bachelor|Master|PhD|B\.Tech|M\.Tech|BSc|MSc|MBA)[^\n\r]*)', text, re.IGNORECASE)
    return [match.strip() for match in education_matches][:3]


def detect_certifications(text):
    certifications = re.findall(r'Certification[s]?:\s*([^\n\r]+)', text, re.IGNORECASE)
    if not certifications:
        certifications = re.findall(r'([A-Z][A-Za-z0-9\s]+(?:Certified|Certification|Certificate))', text)
    return [match.strip() for match in certifications][:3]


def detect_experience(text):
    years_match = re.search(r'(\d+)\+?\s+years? of experience', text, re.IGNORECASE)
    if years_match:
        years = int(years_match.group(1))
    else:
        year_ranges = re.findall(r'(20\d{2})\s*[-–]\s*(20\d{2})', text)
        if year_ranges:
            first_year = int(year_ranges[0][0])
            last_year = int(year_ranges[0][1])
            years = max(0, last_year - first_year)
        else:
            years = None

    if years is None:
        if re.search(r'\b(senior|lead|principal|manager)\b', text, re.IGNORECASE):
            return 'Senior-level'
        if re.search(r'\b(mid|associate)\b', text, re.IGNORECASE):
            return 'Intermediate'
        if re.search(r'\b(junior|intern)\b', text, re.IGNORECASE):
            return 'Beginner'
        return 'Intermediate'

    if years >= 8:
        return 'Strong Professional'
    if years >= 4:
        return 'Intermediate'
    return 'Beginner'


def identify_domain(text):
    normalized = normalize_text(text)
    for domain, terms in DOMAIN_KEYWORDS.items():
        if any(term in normalized for term in terms):
            return domain
    return 'Software Engineering'


def summarize_candidate(text, career_domain, experience_level):
    normalized = normalize_text(text)
    summary = f'{experience_level} {career_domain} professional with demonstrated ability to deliver technical solutions.'
    if experience_level == 'Beginner':
        summary = f'Early-career {career_domain} professional with a strong foundation in technical delivery and cross-functional collaboration.'
    if 'machine learning' in normalized or 'data analysis' in normalized:
        summary = f'{experience_level} {career_domain} specialist with practical experience in data-driven insights and solution delivery.'
    return summary


def categorize_skills(text):
    normalized = normalize_text(text)
    categories = {category: [] for category in SKILL_CATEGORIES}
    categories['Soft Skills'] = []

    for category, terms in SKILL_CATEGORIES.items():
        for term in terms:
            if re.search(r'\b' + re.escape(term.lower()) + r'\b', normalized):
                categories[category].append(term)

    categories['Soft Skills'] = [skill for skill in SOFT_SKILLS if re.search(r'\b' + re.escape(skill) + r'\b', normalized)]

    for category in categories:
        categories[category] = sorted(set(categories[category]))

    return categories


def build_resume_summary(data):
    experience_level = detect_experience(data['raw_text'])
    career_domain = identify_domain(data['raw_text'])
    professional_summary = summarize_candidate(data['raw_text'], career_domain, experience_level)
    return {
        'professional_summary': professional_summary,
        'career_domain': career_domain,
        'experience_level': experience_level
    }


def compute_strengths(analysis):
    strengths = []
    if analysis['skills']:
        strengths.append('Strong technical competency with clearly identified skills.')
    if analysis['projects'] and any(isinstance(project, dict) for project in analysis['projects']):
        strengths.append('Relevant project experience is present with clear technology usage.')
    if analysis['education'] and not isinstance(analysis['education'][0], str):
        strengths.append('Education background is included, supporting professional credibility.')
    if analysis['certifications'] and not isinstance(analysis['certifications'][0], str):
        strengths.append('Certifications add domain credibility and career differentiation.')
    if analysis['keywords']:
        strengths.append('Resume contains important ATS-friendly keywords and domain terms.')
    if not strengths:
        strengths.append('The resume includes foundational sections but can be strengthened further.')
    return strengths


def compute_weaknesses(analysis):
    weaknesses = []
    if not analysis['skills']:
        weaknesses.append('No clear technical skills were detected; add a dedicated skills section.')
    if not analysis['projects'] or (isinstance(analysis['projects'][0], dict) and not analysis['projects'][0]['technologies']):
        weaknesses.append('Project descriptions are weak or missing important technical detail.')
    if not analysis['education'] or isinstance(analysis['education'][0], str) and 'Add degree' in analysis['education'][0]:
        weaknesses.append('Education section is missing or lacks complete degree information.')
    if not analysis['certifications'] or isinstance(analysis['certifications'][0], str) and 'Add certifications' in analysis['certifications'][0]:
        weaknesses.append('Certification details are sparse or missing. Add relevant credentials where possible.')
    if analysis['missing_keywords']:
        weaknesses.append('Critical ATS keywords are missing, which may reduce visibility in screening systems.')
    if len(analysis['projects']) < 2:
        weaknesses.append('Add at least two strong projects with measurable outcomes and technical details.')
    return weaknesses


def build_career_feedback(text, analysis):
    formatting_score = analysis['scores']['formatting']
    keyword_score = analysis['scores']['keyword_matching']
    project_score = analysis['scores']['projects']
    skills_score = analysis['scores']['skills']
    overall_score = analysis['scores']['overall']
    resume_quality_score = analysis['final_evaluation']['quality_score']
    technical_profile_score = round((skills_score + project_score) / 20, 1)
    overall_employability_score = round((overall_score * 0.4 + resume_quality_score * 10 * 0.25 + technical_profile_score * 10 * 0.35) / 10, 1)
    domain = analysis['summary']['career_domain']

    overall_impression = []
    if formatting_score >= 75:
        overall_impression.append('The resume is presented with a clean and professional structure.')
    else:
        overall_impression.append('The resume layout needs stronger section organization and consistent formatting.')

    if keyword_score >= 60:
        overall_impression.append('It includes relevant ATS keywords that suit the candidate’s domain.')
    else:
        overall_impression.append('It would benefit from more ATS-friendly keywords and domain-specific terminology.')

    if skills_score >= 60:
        overall_impression.append('Technical strengths are clearly communicated with relevant skills.')
    else:
        overall_impression.append('The technical profile could be strengthened by adding more explicit skills and tools.')

    review = {
        'structure': 'The resume has a solid overall structure, but may need better section headings and spacing.' if formatting_score < 75 else 'The structure is strong, with good section separation and readability.',
        'clarity': 'The content is generally clear, though some project and experience descriptions could be more concise and results-oriented.' if len(analysis['projects']) else 'The content needs clearer project and achievement descriptions to communicate impact.',
        'ats': 'The resume has a fair ATS fit, but it can improve by adding missing keywords and standard terminology.' if keyword_score < 65 else 'The resume is reasonably ATS-compatible with relevant keywords and industry terms.',
        'technical': 'Technical depth is moderate; adding more specific tools, architectures, and measurable results would improve the profile.' if skills_score < 60 else 'Technical depth is strong, supported by relevant skills and project experience.'
    }

    strengths = []
    if any(analysis['skills'][category] for category in ['Programming Languages', 'Frameworks & Tools', 'Databases', 'Other Technologies']):
        strengths.append('A clearly defined technical skill set is present, including programming languages, frameworks, and tools.')
    if analysis['projects']:
        strengths.append(f'The resume contains project experience, which is valuable for demonstrating real-world delivery.')
    if analysis['education']:
        strengths.append('Education details support the candidate’s professional background.')
    if analysis['certifications']:
        strengths.append('Certifications add credibility and signal continuous learning.')
    if analysis['keywords']:
        strengths.append('The resume uses domain-relevant keywords that align with employer expectations.')
    if not strengths:
        strengths.append('The resume includes foundational sections but has room to build stronger achievements and section clarity.')

    areas = []
    if not any(analysis['skills'][category] for category in ['Programming Languages', 'Frameworks & Tools', 'Databases', 'Other Technologies']):
        areas.append('Add a dedicated technical skills section with clear, categorized skills.')
    if len(analysis['projects']) < 2:
        areas.append('Provide at least two detailed project entries with measurable outcomes and technology stacks.')
    if not analysis['education']:
        areas.append('Include complete education details such as degree, institution, and graduation date.')
    if not analysis['certifications']:
        areas.append('List relevant certifications or training programs to strengthen professional credibility.')
    if analysis['missing_keywords']:
        areas.append('Incorporate missing ATS keywords like: ' + ', '.join(analysis['missing_keywords'][:4]) + '.')
    if formatting_score < 70:
        areas.append('Improve formatting consistency, section headings, and bullet point alignment.')
    if not any(analysis['skills']['Soft Skills']):
        areas.append('Add soft skills and professional strengths to balance the technical profile.')
    if not areas:
        areas.append('Continue refining clarity and impact statements to further strengthen the resume.')

    if domain == 'Machine Learning / AI':
        skill_recommendations = ['MLOps', 'Deep Learning', 'Model Deployment', 'Data Engineering']
        certification_suggestions = ['TensorFlow Developer', 'AWS Machine Learning Specialty', 'IBM AI Engineering']
        project_suggestions = ['end-to-end model deployment', 'predictive analytics pipeline', 'AI-driven automation tool']
    elif domain == 'Data Science':
        skill_recommendations = ['Statistical Modeling', 'Data Visualization', 'Feature Engineering', 'Big Data']
        certification_suggestions = ['Google Data Analytics', 'AWS Data Analytics', 'Microsoft Certified: Data Analyst Associate']
        project_suggestions = ['analytics dashboard', 'forecasting model', 'customer segmentation engine']
    elif domain == 'Web Development':
        skill_recommendations = ['REST API Design', 'Responsive UI', 'Modern JavaScript Frameworks', 'Testing & Automation']
        certification_suggestions = ['AWS Developer Associate', 'Microsoft Azure Fundamentals', 'Certified Kubernetes Application Developer']
        project_suggestions = ['progressive web app', 'microservices platform', 'full-stack SaaS application']
    elif domain == 'Cloud & DevOps':
        skill_recommendations = ['Infrastructure as Code', 'CI/CD Pipelines', 'Container Orchestration', 'Observability']
        certification_suggestions = ['AWS Solutions Architect Associate', 'Azure Fundamentals', 'Docker Certified Associate']
        project_suggestions = ['cloud deployment pipeline', 'containerized microservices', 'automated infrastructure provisioning']
    elif domain == 'Cybersecurity':
        skill_recommendations = ['Application Security', 'Vulnerability Assessment', 'Identity Management', 'Incident Response']
        certification_suggestions = ['CompTIA Security+', 'Certified Ethical Hacker', 'Cisco CCNA Security']
        project_suggestions = ['secure application audit', 'incident response workflow', 'threat modeling exercise']
    else:
        skill_recommendations = ['System Design', 'API Development', 'Software Architecture', 'Test Automation']
        certification_suggestions = ['AWS Solutions Architect', 'Professional Scrum Master', 'ISTQB Certified Tester']
        project_suggestions = ['scalable backend service', 'cross-platform application', 'team collaboration tool']

    career_suggestions = {
        'learn': [f'Build deeper expertise in {skill}.' for skill in skill_recommendations[:3]],
        'certifications': certification_suggestions[:3],
        'portfolio': [
            'Add project case studies with clear outcomes, tech stack, and your role.',
            'Link to GitHub repos or live demos for key projects.',
            'Highlight problem statements, solutions, and measurable impact.'
        ],
        'project_ideas': project_suggestions[:3]
    }

    placement = {
        'internships': 'Suitable for internships with continued focus on structured project experience.' if overall_score >= 45 else 'May need more practical experience and clearer resume structure before internship applications.',
        'entry_level': 'Ready for entry-level roles if the resume is polished and projects are clarified.' if overall_score >= 55 else 'Needs stronger project impact and ATS optimization for entry-level roles.',
        'product_based': 'Potential fit for product-based firms with additional product-focused achievements.' if overall_score >= 65 else 'Requires stronger product-oriented project examples to compete at product-based companies.',
        'service_based': 'Good fit for service-based companies, especially with client-focused delivery examples.' if overall_score >= 50 else 'May fit service-based roles after enhancing technical clarity and project descriptions.'
    }

    return {
        'overall_impression': ' '.join(overall_impression),
        'review': review,
        'strengths': strengths,
        'areas_for_improvement': areas,
        'career_suggestions': career_suggestions,
        'placement_readiness': placement,
        'final_scores': {
            'ats_score': overall_score,
            'resume_quality_score': resume_quality_score,
            'technical_profile_score': technical_profile_score,
            'overall_employability_score': overall_employability_score
        }
    }


def build_optimization_suggestions(career_domain, missing_keywords, formatting_score):
    industry_keywords = []
    if career_domain == 'Machine Learning / AI':
        industry_keywords = ['machine learning', 'deep learning', 'neural networks', 'data pipelines', 'model deployment']
    elif career_domain == 'Data Science':
        industry_keywords = ['data analysis', 'statistical modeling', 'data visualization', 'business intelligence', 'predictive analytics']
    elif career_domain == 'Web Development':
        industry_keywords = ['web application', 'REST API', 'responsive design', 'frontend development', 'backend development']
    elif career_domain == 'Cloud & DevOps':
        industry_keywords = ['cloud architecture', 'CI/CD', 'containerization', 'infrastructure as code', 'automation']
    else:
        industry_keywords = ['technical leadership', 'cross-functional collaboration', 'process improvement', 'results-driven', 'stakeholder engagement']

    suggestions = []
    if missing_keywords:
        suggestions.append('Add keywords such as: ' + ', '.join(missing_keywords[:5]) + '.')
    if formatting_score < 75:
        suggestions.append('Use clear section headings, bullet points, and consistent formatting throughout the resume.')
    suggestions.append('Keep bullet points concise and focus on achievement-oriented language.')
    suggestions.append('Place the summary at the top and use a consistent font/style for better readability.')

    return {
        'industry_keywords': industry_keywords,
        'formatting': 'Use clear section headings, bullet points, and consistent spacing between sections.',
        'readability': 'Use 1-2 line bullets, strong action verbs, and quantifiable outcomes for each achievement.',
        'suggestions': suggestions
    }


def evaluate_resume(overall_score):
    score_out_of_10 = round(overall_score / 10, 1)
    if overall_score >= 80:
        level = 'Strong Professional'
    elif overall_score >= 55:
        level = 'Intermediate'
    else:
        level = 'Beginner'
    return {
        'quality_score': score_out_of_10,
        'level': level
    }


def analyze_resume(text):
    normalized = normalize_text(text)
    skill_categories = categorize_skills(text)
    skills_found = [skill for cat in skill_categories for skill in skill_categories[cat] if cat != 'Soft Skills']
    soft_skills_found = skill_categories['Soft Skills']

    projects = extract_projects(text)
    education = detect_education(text)
    certifications = detect_certifications(text)

    keywords_found = [kw for kw in RESUME_KEYWORDS if kw in normalized]
    missing_keywords = [kw for kw in RESUME_KEYWORDS if kw not in normalized][:6]

    formatting_sections = ['experience', 'education', 'skills', 'projects', 'certifications', 'summary', 'objective', 'contact']
    sections_found = sum(1 for section in formatting_sections if section in normalized)
    formatting_score = min(95, 40 + sections_found * 9 + (10 if re.search(r'\b(bullet|•|- )', text) else 0))

    skills_score = min(100, 40 + len(skills_found) * 6)
    project_score = min(100, 30 + len(projects) * 15)
    keyword_score = min(100, int((len(keywords_found) / max(len(RESUME_KEYWORDS), 1)) * 100))
    overall_score = int((keyword_score * 0.35) + (formatting_score * 0.25) + (project_score * 0.2) + (skills_score * 0.2))

    resume_data = {
        'raw_text': text,
        'skills': skills_found,
        'soft_skills': soft_skills_found,
        'skill_categories': skill_categories,
        'projects': projects,
        'education': education if education else [],
        'certifications': certifications if certifications else [],
        'keywords': keywords_found,
        'missing_keywords': missing_keywords,
        'scores': {
            'overall': overall_score,
            'keyword_matching': keyword_score,
            'formatting': formatting_score,
            'projects': project_score,
            'skills': skills_score
        }
    }

    summary_data = build_resume_summary(resume_data)
    strengths = compute_strengths(resume_data)
    weaknesses = compute_weaknesses(resume_data)
    optimization = build_optimization_suggestions(summary_data['career_domain'], missing_keywords, formatting_score)
    final_evaluation = evaluate_resume(overall_score)
    career_feedback = build_career_feedback(text, {
        'summary': summary_data,
        'skills': skill_categories,
        'projects': projects,
        'education': education if education else [],
        'certifications': certifications if certifications else [],
        'keywords': keywords_found,
        'missing_keywords': missing_keywords,
        'scores': resume_data['scores'],
        'final_evaluation': final_evaluation
    })

    return {
        'summary': summary_data,
        'skills': skill_categories,
        'projects': projects,
        'education': education if education else [],
        'certifications': certifications if certifications else [],
        'keywords': keywords_found,
        'missing_keywords': missing_keywords,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'optimization': optimization,
        'final_evaluation': final_evaluation,
        'career_feedback': career_feedback,
        'scores': resume_data['scores']
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_docx(file_path)

            if not text.strip():
                raise ValueError('Unable to extract text from the document.')

            analysis = analyze_resume(text)
            ats_score = analysis['scores']

            feedback = []
            if not any(analysis['skills'].values()):
                feedback.append('Add a dedicated skills section with technologies, tools, and frameworks.')
            if not analysis['projects'] or (isinstance(analysis['projects'][0], dict) and not analysis['projects'][0].get('technologies')):
                feedback.append('List 2-3 strong projects describing your role and impact.')
            if not analysis['education']:
                feedback.append('Include education details with degree, institution, and year.')
            if not analysis['certifications']:
                feedback.append('Add certifications or professional training relevant to your career goals.')
            if analysis['missing_keywords']:
                feedback.append('Improve ATS match by adding keywords: ' + ', '.join(analysis['missing_keywords'][:4]) + '.')
            if ats_score['formatting'] < 70:
                feedback.append('Use clear section headers, bullet points, and consistent formatting for readability.')
            if ats_score['overall'] < 70:
                feedback.append('Enhance your resume with stronger metrics, results, and keywords to boost the overall score.')
            if not feedback:
                feedback.append('Your resume has strong structure and keyword relevance. Keep refining details for higher ATS results.')

            return jsonify({
                'analysis': analysis,
                'ats_score': ats_score,
                'feedback': feedback
            })
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        return jsonify({'error': 'Invalid file type. Please upload PDF or DOCX.'}), 400

def extract_interview_context(text):
    normalized = normalize_text(text)
    skills = []
    frameworks = []
    databases = []
    technologies = []
    certifications = []
    soft_skills = []

    for skill in RESUME_SKILLS:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', normalized):
            if skill in SKILL_CATEGORIES['Programming Languages']:
                skills.append(skill)
            elif skill in SKILL_CATEGORIES['Databases']:
                databases.append(skill)
            elif skill in SKILL_CATEGORIES['Frameworks & Tools']:
                frameworks.append(skill)
            else:
                technologies.append(skill)

    for category, terms in SKILL_CATEGORIES.items():
        for term in terms:
            if re.search(r'\b' + re.escape(term.lower()) + r'\b', normalized):
                if category == 'Programming Languages' and term not in skills:
                    skills.append(term)
                elif category == 'Frameworks & Tools' and term not in frameworks:
                    frameworks.append(term)
                elif category == 'Databases' and term not in databases:
                    databases.append(term)
                elif category == 'Other Technologies' and term not in technologies:
                    technologies.append(term)

    soft_skills = [skill for skill in SOFT_SKILLS if re.search(r'\b' + re.escape(skill) + r'\b', normalized)]
    certifications = re.findall(r'([A-Z][A-Za-z0-9\s]+(?:Certified|Certification|Certificate))', text)

    return {
        'skills': sorted(set(skills)),
        'frameworks': sorted(set(frameworks)),
        'databases': sorted(set(databases)),
        'technologies': sorted(set(technologies)),
        'software_skills': sorted(set(soft_skills)),
        'certifications': sorted(set(certifications))
    }


def extract_interview_projects(text):
    projects = []
    lines = text.splitlines()

    for i, line in enumerate(lines):
        if re.search(r'\bproject\b', line, re.IGNORECASE):
            title = line.strip()
            description = []
            for j in range(i + 1, len(lines)):
                if not lines[j].strip():
                    break
                description.append(lines[j].strip())
            projects.append({
                'title': title,
                'description': ' '.join(description) if description else title
            })

    if not projects:
        project_matches = re.findall(r'(?:built|developed|designed|launched|created)\s+([A-Z][A-Za-z0-9\s]{5,60})', text, re.IGNORECASE)
        for match in project_matches:
            title = match.strip()
            projects.append({
                'title': title,
                'description': f'Built {title} as a core project.'
            })

    return projects[:3]


def choose_interview_domain(prompt):
    normalized = normalize_text(prompt)
    for key, label in INTERVIEW_DOMAIN_KEYWORDS.items():
        if key in normalized:
            return label
    return 'Software Engineering'


def make_question(question, difficulty, suggested_answer, key_points, confidence_tip):
    return {
        'question': question,
        'difficulty': difficulty,
        'suggested_answer': suggested_answer,
        'key_points': key_points,
        'confidence_tip': confidence_tip
    }


def generate_technical_questions(context, domain_label):
    questions = []
    primary_skill = context['skills'][0] if context['skills'] else domain_label
    framework = context['frameworks'][0] if context['frameworks'] else None
    database = context['databases'][0] if context['databases'] else None
    technology = context['technologies'][0] if context['technologies'] else None

    questions.append(make_question(
        f'Explain the role of {primary_skill} in your most recent technical project.',
        'Easy',
        f'Mention your key contributions using {primary_skill}, any libraries or tools, and the business outcome.',
        [f'{primary_skill} experience', 'project ownership', 'business impact'],
        'Speak clearly about your primary technical responsibility and connect it to results.'
    ))

    if framework:
        questions.append(make_question(
            f'How did you use {framework} to build a stable and maintainable application?',
            'Medium',
            f'Discuss architecture, component structure, and any performance or security tradeoffs.',
            ['framework design', 'modularity', 'scalability'],
            'Describe the architecture while keeping the answer concrete and concise.'
        ))
    else:
        questions.append(make_question(
            f'Describe your experience working with modern frameworks or libraries in a technical project.',
            'Medium',
            'Highlight patterns, state management, and the developer workflow.',
            ['framework choices', 'development process', 'maintainability'],
            'Use examples from a real project and avoid abstract statements.'
        ))

    if database:
        questions.append(make_question(
            f'Explain how you modeled data and optimized queries using {database}.',
            'Medium',
            f'Share realistic schema decisions, indexing strategy, and how this improved performance.',
            ['data modeling', 'query optimization', 'scalability'],
            'Speak confidently about the practical improvements you made in the database.'
        ))
    else:
        questions.append(make_question(
            'Describe a time you designed or optimized data storage for a real application.',
            'Medium',
            'Discuss the storage choice, structure, and how it supported the product goals.',
            ['data design', 'performance', 'reliability'],
            'Explain the business need behind your data solution clearly.'
        ))

    questions.append(make_question(
        f'How would you design and secure APIs for a {domain_label} solution?',
        'Hard',
        'Cover authentication, request validation, versioning, and error handling.',
        ['API design', 'security', 'scalability'],
        'Keep the architecture organized and mention specific protection strategies.'
    ))

    questions.append(make_question(
        'Describe a problem-solving challenge you faced in production and how you resolved it.',
        'Hard',
        'Use the situation-action-result structure to explain your debugging approach, tools, and impact.',
        ['root cause analysis', 'debugging tools', 'measured outcome'],
        'Emphasize your ownership, diagnostic steps, and outcome in a confident tone.'
    ))

    if technology and technology not in [primary_skill, framework, database]:
        questions.append(make_question(
            f'How did {technology} contribute to the success of your project?',
            'Easy',
            f'Explain its role and why it was a suitable choice for the solution.',
            [technology, 'technical fit', 'business value'],
            'Keep the answer focused on practical adoption and benefits.'
        ))

    return questions[:6]


def generate_project_questions(context):
    questions = []
    projects = context['projects'] if context['projects'] else []

    if projects:
        for project in projects:
            title = project['title']
            description = project['description']
            questions.append(make_question(
                f'Describe the architecture and core components of "{title}".',
                'Medium',
                f'Share how the solution was structured, the main modules, and how data flowed end to end.',
                ['architecture', 'components', 'data flow'],
                'Use a simple high-level model and mention the technologies that supported it.'
            ))
            questions.append(make_question(
                f'What was the biggest challenge when building "{title}" and how did you overcome it?',
                'Hard',
                'Identify a technical or team challenge, your approach, and the positive outcome.',
                ['challenge resolution', 'team collaboration', 'result'],
                'Be honest about the challenge and clear about your role in solving it.'
            ))
            questions.append(make_question(
                f'Why did you choose the technologies used in "{title}" and how did they support deployment?',
                'Medium',
                'Explain the tradeoffs behind your technology choices and the deployment path.',
                ['technology rationale', 'deployment strategy', 'operational readiness'],
                'Frame your response around practical benefits and maintainability.'
            ))
    else:
        questions.append(make_question(
            'Describe a significant project from your resume and the business problem it solved.',
            'Easy',
            'Explain the goal, your role, and how the project delivered value.',
            ['project goal', 'role', 'outcome'],
            'Keep the answer structured and highlight measurable results.'
        ))
        questions.append(make_question(
            'What architecture choices did you make on your key project and why?',
            'Medium',
            'Share the design decisions, any frameworks chosen, and the rationale.',
            ['architecture', 'design reasoning', 'technology fit'],
            'Be concise and focus on the strongest decisions you made.'
        ))
        questions.append(make_question(
            'How did you deploy and maintain your project in a production-like environment?',
            'Hard',
            'Describe the deployment pipeline, monitoring, and stability practices.',
            ['deployment', 'monitoring', 'maintenance'],
            'Mention the tools and process you used to keep the project stable.'
        ))

    return questions[:6]


def generate_hr_questions(context):
    questions = []
    questions.append(make_question(
        'Introduce yourself and summarize your professional background.',
        'Easy',
        'Focus on your core strengths, relevant experience, and what motivates you.',
        ['clear introduction', 'relevant experience', 'career motivation'],
        'Keep your introduction concise and aligned to the role.'
    ))
    questions.append(make_question(
        'What are your greatest strengths and how have they helped you in your career?',
        'Medium',
        'Choose strengths supported by examples and relate them to technical delivery.',
        ['strength examples', 'impact', 'relevance'],
        'Connect strengths to real situations and practical outcomes.'
    ))
    questions.append(make_question(
        'What is one area you are improving and how are you working on it?',
        'Medium',
        'Share a genuine growth area and the concrete steps you are taking.',
        ['self awareness', 'growth plan', 'improvement'],
        'Be honest, but frame this as a positive development opportunity.'
    ))
    questions.append(make_question(
        'Describe a time when you collaborated with a team to deliver a project.',
        'Easy',
        'Highlight communication, coordination, and the shared outcome.',
        ['teamwork', 'communication', 'delivery'],
        'Emphasize how you contributed and how the team succeeded together.'
    ))
    questions.append(make_question(
        'How do you approach leadership or influence in cross-functional work?',
        'Medium',
        'Explain how you lead by example, build consensus, and drive progress.',
        ['leadership style', 'influence', 'collaboration'],
        'Show confidence in your ability to guide work without overclaiming.'
    ))
    questions.append(make_question(
        'Where do you see your career in the next two to three years?',
        'Easy',
        'Share a clear, realistic growth plan and how this role fits into it.',
        ['career goals', 'development', 'fit'],
        'Be aspirational but grounded in practical goals and skill growth.'
    ))
    return questions[:6]


def generate_scenario_questions(context):
    questions = []
    questions.append(make_question(
        'How would you handle a last-minute change in project requirements from a client?',
        'Medium',
        'Describe how you would assess impact, communicate with stakeholders, and deliver a revised plan.',
        ['stakeholder communication', 'adaptability', 'planning'],
        'Speak calmly and show that you can balance flexibility with delivery discipline.'
    ))
    questions.append(make_question(
        'A deployment fails in production. What is your debugging process?',
        'Hard',
        'Walk through your investigation steps, tools used, and how you restore service quickly.',
        ['incident response', 'root cause analysis', 'recovery'],
        'Frame your answer around speed, accuracy, and learning after resolution.'
    ))
    questions.append(make_question(
        'A customer requests a feature that conflicts with the current architecture. What do you do?',
        'Hard',
        'Discuss how you evaluate technical feasibility, trade-offs, and propose a practical solution.',
        ['technical evaluation', 'trade offs', 'recommendation'],
        'Show that you can balance customer needs with technical constraints.'
    ))
    questions.append(make_question(
        'How do you handle ambiguous requirements during the early stage of a project?',
        'Easy',
        'Explain how you clarify goals, gather details, and reduce risk before starting development.',
        ['clarification', 'requirements gathering', 'risk reduction'],
        'Demonstrate that you seek clarity and avoid assumptions.'
    ))
    return questions[:6]


def generate_interview_questions(prompt):
    normalized = normalize_text(prompt)
    context = extract_interview_context(prompt)
    context['projects'] = extract_interview_projects(prompt)
    domain_label = choose_interview_domain(prompt)

    return {
        'summary': f'Interview questions generated for a {domain_label} candidate with expertise in {", ".join(context["skills"] + context["frameworks"] + context["databases"] + context["technologies"]) or domain_label}.',
        'technical': {
            'title': 'Technical Questions',
            'questions': generate_technical_questions(context, domain_label)
        },
        'project_based': {
            'title': 'Project-Based Questions',
            'questions': generate_project_questions(context)
        },
        'hr': {
            'title': 'HR Interview Questions',
            'questions': generate_hr_questions(context)
        },
        'scenario': {
            'title': 'Scenario-Based Questions',
            'questions': generate_scenario_questions(context)
        },
        'interviewer_expectations': [
            'Look for concrete examples, clear structure, and real outcomes.',
            'Evaluate whether the candidate understands trade-offs and technical decisions.',
            'Check if the candidate demonstrates teamwork, communication, and problem-solving maturity.'
        ],
        'confidence_tips': [
            'Use the STAR method: Situation, Task, Action, Result.',
            'Keep your responses concise, specific, and aligned to the role.',
            'Speak with confidence and highlight your ownership in project outcomes.'
        ]
    }


@app.route('/interview')
def interview():
    prompt = request.args.get('prompt', '').strip()
    if prompt:
        return jsonify(generate_interview_questions(prompt))
    return jsonify({
        'summary': 'Enter your resume or prompt to generate personalized interview questions.',
        'technical': {
            'title': 'Technical Questions',
            'questions': []
        },
        'project_based': {
            'title': 'Project-Based Questions',
            'questions': []
        },
        'hr': {
            'title': 'HR Interview Questions',
            'questions': []
        },
        'scenario': {
            'title': 'Scenario-Based Questions',
            'questions': []
        },
        'interviewer_expectations': [],
        'confidence_tips': []
    })

def build_portfolio_data(analysis):
    """Build professional portfolio content from resume analysis."""
    summary = analysis['summary']
    skills = analysis['skills']
    projects = analysis['projects']
    domain = summary['career_domain']
    
    # Design palette suggestions based on domain
    design_suggestions = {
        'Machine Learning / AI': {
            'theme': 'Futuristic & Data-Driven',
            'colors': ['#00D9FF', '#0066FF', '#6B21A8', '#000000'],
            'fonts': ['Space Grotesk', 'Inter'],
            'hero_style': 'Animated gradient with floating particles',
            'animations': ['Fade-in cards', 'Hover effects', 'Smooth scrolling']
        },
        'Data Science': {
            'theme': 'Analytical & Professional',
            'colors': ['#2563EB', '#1E40AF', '#DC2626', '#F3F4F6'],
            'fonts': ['Poppins', 'IBM Plex Mono'],
            'hero_style': 'Chart visualization or analytics dashboard',
            'animations': ['Number counters', 'Data visualization', 'Interactive elements']
        },
        'Web Development': {
            'theme': 'Modern & Interactive',
            'colors': ['#6366F1', '#3B82F6', '#EC4899', '#14B8A6'],
            'fonts': ['JetBrains Mono', 'Playfair Display'],
            'hero_style': 'Interactive code snippets or live demo',
            'animations': ['Typing effect', 'Smooth transitions', 'Interactive widgets']
        },
        'Cloud & DevOps': {
            'theme': 'Scalable & Technical',
            'colors': ['#F97316', '#0EA5E9', '#06B6D4', '#1E293B'],
            'fonts': ['Roboto Mono', 'Raleway'],
            'hero_style': 'Infrastructure diagram or cloud visualization',
            'animations': ['Loading sequences', 'Process flows', 'Terminal-style typing']
        }
    }
    
    default_design = {
        'theme': 'Clean & Professional',
        'colors': ['#7C3AED', '#8B5CF6', '#38BDF8', '#1F2937'],
        'fonts': ['Inter', 'JetBrains Mono'],
        'hero_style': 'Gradient background with profile image',
        'animations': ['Fade-in elements', 'Hover effects', 'Scroll animations']
    }
    
    design = design_suggestions.get(domain, default_design)
    
    # Extract name from text if possible
    name = summary.get('professional_summary', 'Full Stack Professional').split('\n')[0][:50] or 'Professional Developer'
    
    portfolio = {
        'hero': {
            'name': name,
            'title': summary['experience_level'] + ' ' + domain,
            'introduction': f"Dedicated {domain} professional with a passion for building impactful solutions. Specialized in leveraging modern technologies to solve complex problems and drive innovation.",
            'career_objective': f"Seeking opportunities to contribute expertise in {domain} while growing skills in emerging technologies and leading impactful projects."
        },
        'about': {
            'background': f"With a strong foundation in {domain}, I bring proven expertise in delivering scalable, efficient solutions. My career is marked by continuous learning and a commitment to best practices in software development and deployment.",
            'skills_summary': f"Proficient in {', '.join(skills.get('Programming Languages', [])[:3] if skills.get('Programming Languages') else ['Python', 'JavaScript', 'Java'])}. Experienced with {', '.join(skills.get('Frameworks & Tools', [])[:3] if skills.get('Frameworks & Tools') else ['React', 'Node.js', 'Django'])} and various cloud platforms.",
            'passion': "Passionate about creating elegant, maintainable code and contributing to open-source projects. Enjoys collaborating with teams and mentoring junior developers."
        },
        'skills': {
            'programming_languages': skills.get('Programming Languages', [])[:5] or ['Python', 'JavaScript', 'Java'],
            'frameworks': skills.get('Frameworks & Tools', [])[:6] or ['React', 'Node.js', 'Django', 'Flask', 'Spring Boot', 'Express'],
            'tools': skills.get('Other Technologies', [])[:5] or ['Git', 'Docker', 'Kubernetes', 'CI/CD'],
            'databases': skills.get('Databases', [])[:4] or ['PostgreSQL', 'MongoDB', 'MySQL'],
            'soft_skills': skills.get('Soft Skills', [])[:5] or ['Problem Solving', 'Team Leadership', 'Communication', 'Project Management', 'Mentoring']
        },
        'projects': [
            {
                'title': p.get('title', 'Untitled Project') if isinstance(p, dict) else f'Project {i+1}',
                'description': p.get('purpose', 'Building innovative solutions') if isinstance(p, dict) else 'A meaningful project that demonstrates technical expertise',
                'technologies': p.get('technologies', []) if isinstance(p, dict) else [],
                'features': p.get('impact', '').split('.') if isinstance(p, dict) else ['Core feature 1', 'Core feature 2'],
                'challenges': 'Optimized performance, ensured scalability, maintained code quality',
                'github_link': 'https://github.com/yourusername/project-name',
                'live_demo': 'https://project-demo.com'
            } for i, p in enumerate(projects[:4])
        ],
        'experience': {
            'internships': ['Internship Program at Leading Tech Company', 'Open Source Contributions'],
            'certifications': analysis.get('certifications', ['AWS Certified', 'Professional Development Course']) or ['Professional Development Certifications'],
            'achievements': [
                'Successfully delivered 5+ major projects',
                'Improved system performance by 40%',
                'Led a team of 3+ developers',
                'Contributed to open-source projects with 100+ stars'
            ]
        },
        'contact': {
            'email': 'your.email@example.com',
            'linkedin': 'linkedin.com/in/yourprofile',
            'github': 'github.com/yourprofile',
            'portfolio': 'yourportfolio.com'
        },
        'design': design,
        'responsive_layout': {
            'desktop': 'Multi-column layout with sidebar navigation',
            'tablet': 'Adjusted grid layout with collapsible sections',
            'mobile': 'Single-column stack with hamburger menu'
        }
    }
    
    return portfolio

@app.route('/portfolio-builder', methods=['POST'])
def portfolio_builder():
    """Generate portfolio data from resume analysis."""
    try:
        data = request.get_json()
        if not data or 'analysis' not in data:
            return jsonify({'error': 'Analysis data required'}), 400
        
        portfolio = build_portfolio_data(data['analysis'])
        return jsonify({'portfolio': portfolio})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/portfolio')
def portfolio():
    return jsonify(SAMPLE_PORTFOLIO)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
