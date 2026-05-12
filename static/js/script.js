document.addEventListener('DOMContentLoaded', () => {
    // Hamburger menu
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    // Smooth scrolling for nav links
    const links = document.querySelectorAll('.nav-links a');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            target.scrollIntoView({ behavior: 'smooth' });
        });
    });

    // Resume upload and analysis
    const uploadForm = document.getElementById('upload-form');
    const resumeInput = document.getElementById('resume-upload');
    const resultsDiv = document.getElementById('results');
    const overallScoreDiv = document.getElementById('overall-score');
    const scoreDetailsDiv = document.getElementById('score-details');
    const feedbackListDiv = document.getElementById('feedback-list');
    const submitButton = uploadForm.querySelector('[type="submit"]');
    let currentAnalysis = null;

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!resumeInput || !resumeInput.files || resumeInput.files.length === 0) {
            resultsDiv.innerHTML = '<p class="error-message">Please select a PDF or DOCX resume file first.</p>';
            console.warn('No file selected for upload');
            return;
        }

        const file = resumeInput.files[0];
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const maxSize = 16 * 1024 * 1024; // 16MB

        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.docx')) {
            resultsDiv.innerHTML = '<p class="error-message">Please upload a valid PDF or DOCX file.</p>';
            console.warn('Invalid file type:', file.type, file.name);
            return;
        }

        if (file.size > maxSize) {
            resultsDiv.innerHTML = '<p class="error-message">File size too large. Please upload a file smaller than 16MB.</p>';
            console.warn('File too large:', file.size);
            return;
        }

        const originalButtonText = submitButton ? submitButton.textContent : 'Analyzing...';
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Analyzing...';
            submitButton.classList.add('loading');
        }

        resultsDiv.innerHTML = '<div class="loading"></div><p class="status-message">Analyzing resume...</p>';
        overallScoreDiv.textContent = '';
        scoreDetailsDiv.innerHTML = '';
        feedbackListDiv.innerHTML = '';

        const formData = new FormData(uploadForm);
        console.log('Submitting resume for analysis', { fileName: resumeInput.files[0]?.name, fileSize: resumeInput.files[0]?.size });

        try {
            console.log('Sending fetch request to /analyze');
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            console.log('Received response', { status: response.status, ok: response.ok, statusText: response.statusText });

            const contentType = response.headers.get('content-type') || '';
            console.log('Response content-type:', contentType);

            const text = await response.text();
            console.log('Response text length:', text.length);
            console.log('Response text preview:', text.substring(0, 200) + (text.length > 200 ? '...' : ''));

            let data = null;
            if (contentType.includes('application/json') || text.trim().startsWith('{')) {
                try {
                    data = JSON.parse(text);
                    console.log('Successfully parsed JSON response:', data);
                } catch (parseError) {
                    console.error('Failed to parse JSON from /analyze response:', parseError);
                    console.error('Raw response text:', text);
                    resultsDiv.innerHTML = '<p class="error-message">Server returned invalid response format. Please try again.</p>';
                    return;
                }
            } else {
                console.error('Expected JSON response but received:', { contentType, text });
                resultsDiv.innerHTML = '<p class="error-message">Server returned unexpected response format. Please try again.</p>';
                return;
            }

            if (response.ok && data) {
                console.log('Response is OK and data exists, checking for analysis data');
                if (data.analysis) {
                    console.log('Analysis data found, displaying results');
                    displayAnalysis(data);
                    displayATSScore(data.ats_score || {});
                    displayFeedback(data.feedback || []);
                    currentAnalysis = { analysis: data.analysis };
                    console.log('Analysis displayed successfully');
                } else {
                    console.warn('Response OK but no analysis data in response:', data);
                    const errorMessage = data.error || 'Analysis failed: No analysis data received from server.';
                    resultsDiv.innerHTML = `<p class="error-message">${errorMessage}</p>`;
                }
            } else {
                console.error('Response not OK or no data:', { ok: response.ok, data });
                const errorMessage = data?.error || (response.ok ? 'Unexpected server response. Please try again.' : `Server error ${response.status}: ${response.statusText}`);
                resultsDiv.innerHTML = `<p class="error-message">${errorMessage}</p>`;
            }
        } catch (error) {
            console.error('Network or fetch error while analyzing resume:', error);
            resultsDiv.innerHTML = '<p class="error-message">Unable to analyze resume right now. Please check your connection and try again.</p>';
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
                submitButton.classList.remove('loading');
            }
            console.log('Analysis request completed');
        }
    });

    function displayAnalysis(data) {
        console.log('Displaying analysis data:', data);
        const analysis = data.analysis || {};
        const summary = analysis.summary || {};
        const skills = analysis.skills || {};
        const projects = analysis.projects || [];
        const strengths = analysis.strengths || [];
        const weaknesses = analysis.weaknesses || [];
        const optimization = analysis.optimization || {};
        const finalEvaluation = analysis.final_evaluation || {};

        resultsDiv._analysisData = analysis;
        resultsDiv.innerHTML = `
            <div class="analysis-section">
                <h3>Resume Summary</h3>
                <p>${summary.professional_summary || 'Summary not available'}</p>
                <p><strong>Domain:</strong> ${summary.career_domain || 'Not detected'}</p>
                <p><strong>Experience Level:</strong> ${summary.experience_level || 'Not determined'}</p>
            </div>
            <div class="analysis-section">
                <h3>Skills Analysis</h3>
                <div class="skill-category">
                    <h4>Programming Languages</h4>
                    <p>${(skills['Programming Languages'] || []).length ? skills['Programming Languages'].join(', ') : 'None detected'}</p>
                </div>
                <div class="skill-category">
                    <h4>Frameworks & Tools</h4>
                    <p>${(skills['Frameworks & Tools'] || []).length ? skills['Frameworks & Tools'].join(', ') : 'None detected'}</p>
                </div>
                <div class="skill-category">
                    <h4>Databases</h4>
                    <p>${(skills['Databases'] || []).length ? skills['Databases'].join(', ') : 'None detected'}</p>
                </div>
                <div class="skill-category">
                    <h4>Other Technologies</h4>
                    <p>${(skills['Other Technologies'] || []).length ? skills['Other Technologies'].join(', ') : 'None detected'}</p>
                </div>
                <div class="skill-category">
                    <h4>Soft Skills</h4>
                    <p>${(skills['Soft Skills'] || []).length ? skills['Soft Skills'].join(', ') : 'None detected'}</p>
                </div>
            </div>
            <div class="analysis-section">
                <h3>Project Analysis</h3>
                ${projects.length ? projects.map(project => `
                    <div class="project-summary">
                        <h4>${project.title || 'Untitled Project'}</h4>
                        <p><strong>Purpose:</strong> ${project.purpose || 'Not specified'}</p>
                        <p><strong>Technologies:</strong> ${(project.technologies || []).length ? project.technologies.join(', ') : 'Not listed'}</p>
                        <p><strong>Impact:</strong> ${project.impact || 'Not specified'}</p>
                        <p><strong>Strengths:</strong> ${(project.strengths || []).join(' ')}</p>
                    </div>
                `).join('') : '<p>No projects could be analyzed from the resume.</p>'}
            </div>
            <div class="analysis-section">
                <h3>Resume Strengths</h3>
                <ul>${strengths.length ? strengths.map(item => `<li>${item}</li>`).join('') : '<li>No strengths identified</li>'}</ul>
            </div>
            <div class="analysis-section">
                <h3>Weaknesses & Missing Areas</h3>
                <ul>${weaknesses.length ? weaknesses.map(item => `<li>${item}</li>`).join('') : '<li>No weaknesses identified</li>'}</ul>
            </div>
            <div class="analysis-section">
                <h3>ATS Optimization Suggestions</h3>
                <p><strong>Industry Keywords:</strong> ${(optimization.industry_keywords || []).join(', ')}</p>
                <p><strong>Formatting:</strong> ${optimization.formatting || 'Not available'}</p>
                <p><strong>Readability:</strong> ${optimization.readability || 'Not available'}</p>
                <ul>${(optimization.suggestions || []).length ? optimization.suggestions.map(item => `<li>${item}</li>`).join('') : '<li>No suggestions available</li>'}</ul>
            </div>
            <div class="analysis-section">
                <h3>Final Evaluation</h3>
                <p><strong>Resume Quality Score:</strong> ${finalEvaluation.quality_score || 'N/A'} / 10</p>
                <p><strong>Professional Level:</strong> ${finalEvaluation.level || 'Not determined'}</p>
            </div>
        `;
        console.log('Analysis displayed successfully');
    }

    function displayATSScore(atsScore) {
        console.log('Displaying ATS score:', atsScore);
        const overall = atsScore.overall || 0;
        const keywordMatching = atsScore.keyword_matching || 0;
        const formatting = atsScore.formatting || 0;
        const projects = atsScore.projects || 0;
        const skills = atsScore.skills || 0;

        overallScoreDiv.textContent = `${overall}%`;
        scoreDetailsDiv.innerHTML = `
            <div class="score-item">
                <h4>Keyword Matching</h4>
                <p>${keywordMatching}%</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${keywordMatching}%"></div>
                </div>
            </div>
            <div class="score-item">
                <h4>Formatting</h4>
                <p>${formatting}%</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${formatting}%"></div>
                </div>
            </div>
            <div class="score-item">
                <h4>Projects</h4>
                <p>${projects}%</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${projects}%"></div>
                </div>
            </div>
            <div class="score-item">
                <h4>Skills</h4>
                <p>${skills}%</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${skills}%"></div>
                </div>
            </div>
        `;
        console.log('ATS score displayed successfully');
    }

    function displayFeedback(feedback) {
        console.log('Displaying feedback:', feedback);
        const cf = feedback && typeof feedback === 'object' && !Array.isArray(feedback) && feedback.overall_impression ? feedback : null;
        if (cf) {
            feedbackListDiv.innerHTML = `
                <div class="feedback-section">
                    <h3>Overall Impression</h3>
                    <p>${cf.overall_impression || 'Not available'}</p>
                </div>
                <div class="feedback-section">
                    <h3>Resume Quality Review</h3>
                    <ul>
                        <li><strong>Structure & Formatting:</strong> ${cf.review?.structure || 'Not available'}</li>
                        <li><strong>Content Clarity:</strong> ${cf.review?.clarity || 'Not available'}</li>
                        <li><strong>ATS Compatibility:</strong> ${cf.review?.ats || 'Not available'}</li>
                        <li><strong>Technical Depth:</strong> ${cf.review?.technical || 'Not available'}</li>
                    </ul>
                </div>
                <div class="feedback-section">
                    <h3>Strengths</h3>
                    <ul>${(cf.strengths || []).length ? cf.strengths.map(item => `<li>${item}</li>`).join('') : '<li>No strengths listed</li>'}</ul>
                </div>
                <div class="feedback-section">
                    <h3>Areas for Improvement</h3>
                    <ul>${(cf.areas_for_improvement || []).length ? cf.areas_for_improvement.map(item => `<li>${item}</li>`).join('') : '<li>No areas for improvement listed</li>'}</ul>
                </div>
                <div class="feedback-section">
                    <h3>Career Improvement Suggestions</h3>
                    <p><strong>Skills to learn:</strong> ${(cf.career_suggestions?.learn || []).join(', ')}</p>
                    <p><strong>Suggested certifications:</strong> ${(cf.career_suggestions?.certifications || []).join(', ')}</p>
                    <p><strong>Portfolio improvements:</strong> ${(cf.career_suggestions?.portfolio || []).join(' ')}</p>
                    <p><strong>Project ideas:</strong> ${(cf.career_suggestions?.project_ideas || []).join(', ')}</p>
                </div>
                <div class="feedback-section">
                    <h3>Placement Readiness</h3>
                    <ul>
                        <li><strong>Internships:</strong> ${cf.placement_readiness?.internships || 'Not available'}</li>
                        <li><strong>Entry-level:</strong> ${cf.placement_readiness?.entry_level || 'Not available'}</li>
                        <li><strong>Product-based companies:</strong> ${cf.placement_readiness?.product_based || 'Not available'}</li>
                        <li><strong>Service-based companies:</strong> ${cf.placement_readiness?.service_based || 'Not available'}</li>
                    </ul>
                </div>
                <div class="feedback-section">
                    <h3>Final Feedback Score</h3>
                    <ul>
                        <li><strong>ATS Score:</strong> ${cf.final_scores?.ats_score || 'N/A'}%</li>
                        <li><strong>Resume Quality Score:</strong> ${cf.final_scores?.resume_quality_score || 'N/A'} / 10</li>
                        <li><strong>Technical Profile Score:</strong> ${cf.final_scores?.technical_profile_score || 'N/A'} / 10</li>
                        <li><strong>Overall Employability Score:</strong> ${cf.final_scores?.overall_employability_score || 'N/A'} / 10</li>
                    </ul>
                </div>
            `;
        } else if (Array.isArray(feedback)) {
            feedbackListDiv.innerHTML = feedback.length ? feedback.map(item => `
                <div class="feedback-item">
                    <p>${item}</p>
                </div>
            `).join('') : '<div class="feedback-item"><p>No feedback available at this time.</p></div>';
        } else {
            feedbackListDiv.innerHTML = '<div class="feedback-item"><p>No feedback available at this time. Please analyze a resume first.</p></div>';
        }
        console.log('Feedback displayed successfully');
    }

    // Interview questions
    const tabBtns = document.querySelectorAll('.tab-btn');
    const questionsContainer = document.getElementById('questions-container');
    const promptInput = document.getElementById('interview-prompt');
    const generateBtn = document.getElementById('generate-questions');
    let activeType = 'technical';
    const sectionGroups = {
        technical: ['technical', 'project_based'],
        hr: ['hr', 'scenario']
    };

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeType = btn.dataset.tab;
            loadQuestions(activeType);
        });
    });

    generateBtn.addEventListener('click', () => {
        loadQuestions(activeType);
    });

    async function loadQuestions(type) {
        questionsContainer.innerHTML = '<div class="loading"></div> Preparing questions...';
        try {
            const prompt = encodeURIComponent(promptInput.value.trim());
            const url = prompt ? `/interview?prompt=${prompt}` : '/interview';
            const response = await fetch(url);
            const data = await response.json();
            displayInterviewQuestions(data, type);
        } catch (error) {
            questionsContainer.innerHTML = '<p class="error-message">Unable to load questions. Try again.</p>';
        }
    }

    function displayInterviewQuestions(data, activeType) {
        let html = '';
        const categories = sectionGroups[activeType] || ['technical'];

        if (data.summary) {
            html += `<div class="interview-summary"><p>${data.summary}</p></div>`;
        }

        let questionsFound = false;
        categories.forEach(sectionKey => {
            const section = data[sectionKey];
            if (!section || !Array.isArray(section.questions) || section.questions.length === 0) return;
            questionsFound = true;
            html += `<div class="question-group">
                        <h3>${section.title}</h3>
                        ${section.questions.map((q, index) => `
                            <div class="question-card">
                                <div class="question-number">${index + 1}</div>
                                <p class="question-text">${q.question}</p>
                                ${q.key_points ? `<p class="question-meta"><strong>Focus:</strong> ${Array.isArray(q.key_points) ? q.key_points.join(', ') : q.key_points}</p>` : ''}
                                ${q.suggested_answer ? `<p class="question-meta"><strong>Answer Tip:</strong> ${q.suggested_answer}</p>` : ''}
                            </div>
                        `).join('')}
                    </div>`;
        });

        if (!questionsFound) {
            html += '<div class="no-questions">No personalized questions found yet. Enter a prompt and try again.</div>';
        }

        if (data.interviewer_expectations) {
            html += `<div class="interview-summary"><h4>Interviewer Expectations</h4><ul>${data.interviewer_expectations.map(item => `<li>${item}</li>`).join('')}</ul></div>`;
        }

        if (data.confidence_tips) {
            html += `<div class="interview-summary"><h4>Confidence Tips</h4><ul>${data.confidence_tips.map(item => `<li>${item}</li>`).join('')}</ul></div>`;
        }

        questionsContainer.innerHTML = html;
    }

    // Load initial questions
    loadQuestions('technical');

    // Portfolio
    const portfolioContent = document.getElementById('portfolio-content');

    async function loadPortfolio() {
        try {
            const response = await fetch('/portfolio');
            const data = await response.json();
            portfolioContent.innerHTML = `
                <div class="portfolio-section">
                    <h3>GitHub</h3>
                    <p><a href="${data.github}" target="_blank">${data.github}</a></p>
                </div>
                <div class="portfolio-section">
                    <h3>Skills</h3>
                    <ul>${data.skills.map(skill => `<li>${skill}</li>`).join('')}</ul>
                </div>
                <div class="portfolio-section">
                    <h3>Projects</h3>
                    ${data.projects.map(project => `
                        <div class="project-card">
                            <h4>${project.name}</h4>
                            <p>${project.description}</p>
                            <p><strong>Technologies:</strong> ${project.tech.join(', ')}</p>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            portfolioContent.innerHTML = '<p>Error loading portfolio.</p>';
        }
    }

    loadPortfolio();

    // Portfolio Builder
    const generatePortfolioBtn = document.getElementById('generate-portfolio');

    generatePortfolioBtn.addEventListener('click', async () => {
        if (!currentAnalysis || !currentAnalysis.analysis) {
            portfolioContent.innerHTML = '<div class="portfolio-placeholder"><p>Please upload and analyze a resume first to generate a portfolio.</p></div>';
            return;
        }

        portfolioContent.innerHTML = '<div class="loading"></div> Generating portfolio...';
        try {
            const response = await fetch('/portfolio-builder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentAnalysis)
            });
            const data = await response.json();
            displayPortfolioBuilder(data.portfolio);
        } catch (error) {
            portfolioContent.innerHTML = '<p class="error-message">Error generating portfolio. Please try again.</p>';
        }
    });

    function displayPortfolioBuilder(portfolio) {
        const design = portfolio.design;
        portfolioContent.innerHTML = `
            <div class="portfolio-builder">
                <!-- Hero Section -->
                <div class="portfolio-section hero-section">
                    <h3>Hero Section</h3>
                    <div class="portfolio-preview-card">
                        <h4>${portfolio.hero.name}</h4>
                        <p class="role">${portfolio.hero.title}</p>
                        <p class="intro">${portfolio.hero.introduction}</p>
                        <p class="objective"><strong>Career Objective:</strong> ${portfolio.hero.career_objective}</p>
                    </div>
                </div>

                <!-- About Section -->
                <div class="portfolio-section about-section">
                    <h3>About Section</h3>
                    <div class="portfolio-preview-card">
                        <h4>Professional Background</h4>
                        <p>${portfolio.about.background}</p>
                        <h4 style="margin-top: 1rem;">Skills Summary</h4>
                        <p>${portfolio.about.skills_summary}</p>
                        <h4 style="margin-top: 1rem;">Passion & Interests</h4>
                        <p>${portfolio.about.passion}</p>
                    </div>
                </div>

                <!-- Skills Section -->
                <div class="portfolio-section skills-section">
                    <h3>Skills Breakdown</h3>
                    <div class="portfolio-preview-card">
                        <div class="skill-row">
                            <h4>Programming Languages</h4>
                            <div class="skill-tags">${portfolio.skills.programming_languages.map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
                        </div>
                        <div class="skill-row">
                            <h4>Frameworks & Tools</h4>
                            <div class="skill-tags">${portfolio.skills.frameworks.map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
                        </div>
                        <div class="skill-row">
                            <h4>Databases</h4>
                            <div class="skill-tags">${portfolio.skills.databases.map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
                        </div>
                        <div class="skill-row">
                            <h4>Other Technologies</h4>
                            <div class="skill-tags">${portfolio.skills.tools.map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
                        </div>
                        <div class="skill-row">
                            <h4>Soft Skills</h4>
                            <div class="skill-tags">${portfolio.skills.soft_skills.map(s => `<span class="skill-tag soft">${s}</span>`).join('')}</div>
                        </div>
                    </div>
                </div>

                <!-- Projects Section -->
                <div class="portfolio-section projects-section">
                    <h3>Featured Projects</h3>
                    ${portfolio.projects.map((p, i) => `
                        <div class="portfolio-preview-card project-card">
                            <h4>${p.title}</h4>
                            <p>${p.description}</p>
                            <p><strong>Technologies:</strong> ${p.technologies.join(', ')}</p>
                            <p><strong>GitHub:</strong> <a href="${p.github_link}" target="_blank">${p.github_link}</a></p>
                            <p><strong>Live Demo:</strong> <a href="${p.live_demo}" target="_blank">${p.live_demo}</a></p>
                        </div>
                    `).join('')}
                </div>

                <!-- Experience & Certifications -->
                <div class="portfolio-section experience-section">
                    <h3>Experience & Achievements</h3>
                    <div class="portfolio-preview-card">
                        <h4>Internships</h4>
                        <ul>${portfolio.experience.internships.map(i => `<li>${i}</li>`).join('')}</ul>
                        <h4 style="margin-top: 1rem;">Certifications</h4>
                        <ul>${portfolio.experience.certifications.map(c => `<li>${c}</li>`).join('')}</ul>
                        <h4 style="margin-top: 1rem;">Achievements</h4>
                        <ul>${portfolio.experience.achievements.map(a => `<li>${a}</li>`).join('')}</ul>
                    </div>
                </div>

                <!-- Contact Section -->
                <div class="portfolio-section resume-download-section">
                    <h3>Resume Download Section</h3>
                    <div class="portfolio-preview-card">
                        <p>Include a prominent resume download button at the top of the portfolio page.</p>
                        <p><strong>Button label suggestion:</strong> "Download Resume"</p>
                        <p><strong>Placement:</strong> Hero section and contact section for easy access.</p>
                    </div>
                </div>

                <div class="portfolio-section contact-section">
                    <h3>Contact Information</h3>
                    <div class="portfolio-preview-card">
                        <p><strong>Email:</strong> ${portfolio.contact.email}</p>
                        <p><strong>LinkedIn:</strong> ${portfolio.contact.linkedin}</p>
                        <p><strong>GitHub:</strong> ${portfolio.contact.github}</p>
                        <p><strong>Portfolio:</strong> ${portfolio.contact.portfolio}</p>
                    </div>
                </div>

                <!-- Design Suggestions -->
                <div class="portfolio-section design-section">
                    <h3>Design Recommendations</h3>
                    <div class="portfolio-preview-card design-card">
                        <h4>Theme: ${design.theme}</h4>
                        <p><strong>Color Palette:</strong> ${design.colors.join(', ')}</p>
                        <p><strong>Typography:</strong> ${design.fonts.join(', ')}</p>
                        <p><strong>Hero Style:</strong> ${design.hero_style}</p>
                        <p><strong>Animation Ideas:</strong> ${design.animations.join(', ')}</p>
                        <div style="margin-top: 1rem;">
                            <strong>Responsive Layout:</strong>
                            <p>Desktop: ${portfolio.responsive_layout.desktop}</p>
                            <p>Tablet: ${portfolio.responsive_layout.tablet}</p>
                            <p>Mobile: ${portfolio.responsive_layout.mobile}</p>
                        </div>
                    </div>
                </div>

                <!-- Export & Download -->
                <div class="portfolio-section export-section">
                    <h3>Export Portfolio</h3>
                    <div class="portfolio-preview-card">
                        <p>Download your portfolio content as:</p>
                        <div style="margin-top: 1rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                            <button onclick="downloadPortfolioJSON()" class="btn-secondary">JSON</button>
                            <button onclick="downloadPortfolioHTML()" class="btn-secondary">HTML Template</button>
                            <button onclick="downloadPortfolioPDF()" class="btn-secondary">PDF Report</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Store portfolio for download
        window.portfolioData = portfolio;
    }

    // Helper functions for download
    window.downloadPortfolioJSON = function() {
        const dataStr = JSON.stringify(window.portfolioData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'portfolio.json';
        link.click();
    };

    window.downloadPortfolioHTML = function() {
        const p = window.portfolioData;
        const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${p.hero.name} - Portfolio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: ${p.design.fonts[0]}, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
        section { padding: 60px 0; }
        h1 { font-size: 2.5rem; margin-bottom: 10px; }
        h2 { font-size: 2rem; margin-bottom: 30px; }
        h3, h4 { margin-top: 20px; margin-bottom: 10px; }
        .hero { background: linear-gradient(135deg, ${p.design.colors[0]}, ${p.design.colors[1]}); color: white; text-align: center; }
        .skill-tag { display: inline-block; background: ${p.design.colors[0]}; color: white; padding: 5px 10px; border-radius: 20px; margin: 5px; }
        a { color: ${p.design.colors[2]}; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <section class="hero">
        <div class="container">
            <h1>${p.hero.name}</h1>
            <h2>${p.hero.title}</h2>
            <p>${p.hero.introduction}</p>
        </div>
    </section>
    <section class="about">
        <div class="container">
            <h2>About Me</h2>
            <p>${p.about.background}</p>
            <h3>Skills Summary</h3>
            <p>${p.about.skills_summary}</p>
        </div>
    </section>
    <section class="skills">
        <div class="container">
            <h2>Skills</h2>
            <h3>Programming Languages</h3>
            <p>${p.skills.programming_languages.join(', ')}</p>
            <h3>Frameworks</h3>
            <p>${p.skills.frameworks.join(', ')}</p>
        </div>
    </section>
    <section class="contact">
        <div class="container">
            <h2>Contact</h2>
            <p>Email: <a href="mailto:${p.contact.email}">${p.contact.email}</a></p>
            <p>LinkedIn: <a href="https://${p.contact.linkedin}">${p.contact.linkedin}</a></p>
            <p>GitHub: <a href="https://${p.contact.github}">${p.contact.github}</a></p>
        </div>
    </section>
</body>
</html>
        `;
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'portfolio.html';
        link.click();
    };

    window.downloadPortfolioPDF = function() {
        alert('PDF export will be available soon. For now, use your browser\'s "Save as PDF" feature (Ctrl+P or Cmd+P).');
    };
});