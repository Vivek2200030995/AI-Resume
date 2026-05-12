# AI Resume & Interview Assistant

A premium modern web application for resume optimization and interview preparation using AI, built with Flask, HTML, CSS, and JavaScript.

## Features

- Professional landing page with hero section, gradient background, responsive navbar, feature cards, glassmorphism UI, hover animations, smooth scrolling, dark theme, and mobile-friendly layout
- Resume Analyzer: Upload PDF/DOCX resumes, extract text, analyze skills, projects, education, certifications, and keywords
- ATS Score System: Calculate ATS score with keyword matching, formatting quality, project quality, and skills evaluation, displayed with animated progress bars and charts
- Interview Preparation Dashboard: Generate technical and HR interview questions with difficulty levels and interactive cards
- AI Feedback Section: Provide resume improvement suggestions, recommend missing technologies and skills
- Portfolio Builder Preview: Generate portfolio preview with GitHub section, skills showcase, and project showcase

## Technologies Used

- Backend: Flask (Python)
- Frontend: HTML5, CSS3 (with glassmorphism, gradients, animations), JavaScript (ES6+)
- Libraries: PyPDF2, python-docx for document processing

## Installation

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open `http://127.0.0.1:5000` in your browser.

## Project Structure

```
AI-Resume/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── script.js
├── uploads/
├── .github/
│   └── copilot-instructions.md
└── README.md
```

## Usage

- Navigate through the sections using the navbar.
- Upload a resume in the analyzer section to get analysis, ATS score, and feedback.
- Explore interview questions by switching between Technical and HR tabs.
- View the portfolio preview section.

## Production Deployment

This project is production-ready with Gunicorn and environment-based configuration.

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Set a secure `SECRET_KEY` in your production environment.
3. Start the app with Gunicorn:
   - `gunicorn app:app --bind 0.0.0.0:${PORT:-5000}`
4. If you are using Render, the existing `Procfile` is already configured:
   - `web: gunicorn app:app`
5. For local development, copy `.env.example` to `.env` and update values.

### Environment variables

- `SECRET_KEY` — required for session security in production.
- `PORT` — port used by the app in local testing and some hosting providers.
- `FLASK_ENV` — set to `production` for production deployments.
- `SESSION_COOKIE_SECURE` — recommended `true` for HTTPS-only cookies.
- `PREFERRED_URL_SCHEME` — set to `https` for production.
- `ENABLE_PROXY_FIX` — set to `true` when behind a reverse proxy.

## Docker Deployment

This app can also run in a production container using the included `Dockerfile`.

1. Build the Docker image:
   - `docker build -t ai-resume-assistant .`
2. Run the container:
   - `docker run -e SECRET_KEY=your-secret-key -p 5000:5000 ai-resume-assistant`
3. Open `http://127.0.0.1:5000` in your browser.

For production, provide `SECRET_KEY` and any other environment variables securely through your container platform or orchestration layer.

## Contributing

Feel free to contribute by submitting issues or pull requests.

## License

This project is open source.