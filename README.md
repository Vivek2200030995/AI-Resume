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

## Contributing

Feel free to contribute by submitting issues or pull requests.

## License

This project is open source.