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

    // Mock analyze resume
    const analyzeBtn = document.querySelector('.btn-secondary');
    const results = document.getElementById('results');
    analyzeBtn.addEventListener('click', () => {
        results.innerHTML = '<p>Analysis complete! Your resume is 85% optimized.</p>';
    });
});