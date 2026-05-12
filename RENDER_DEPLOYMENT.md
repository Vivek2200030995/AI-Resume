# Render Deployment Guide

## ✅ Deployment Preparation Complete

Your Flask application has been configured for production deployment on Render. Here's what was fixed and configured:

### Files Created/Updated:
1. **Procfile** - Tells Render how to start the application
   - Content: `web: gunicorn app:app`
   - Location: Project root

2. **requirements.txt** - Updated with production dependencies
   - Added: `gunicorn==21.2.0` (production WSGI server)
   - Added: `python-dotenv==1.0.0` (environment variable management)

3. **.env.example** - Template for local development
   - Copy to `.env` for local development
   - Do NOT commit `.env` to Git

4. **.gitignore** - Prevents sensitive files from being deployed
   - Ignores: `__pycache__/`, `*.pyc`, `uploads/`, `.env`, etc.

5. **app.py** - Updated for production
   - Secret key now uses environment variable: `os.getenv('SECRET_KEY', 'fallback-key')`
   - PORT handling: `port = int(os.getenv('PORT', 5000))`
   - Host set to `'0.0.0.0'` (required for cloud deployment)
   - Debug mode controlled by FLASK_ENV environment variable

### Project Structure (Verified):
```
AI-Resume/
├── app.py                  ✅ Main Flask app
├── Procfile               ✅ Render startup config (NEW)
├── requirements.txt       ✅ Dependencies updated
├── .gitignore            ✅ Deployment safety (NEW)
├── .env.example          ✅ Environment template (NEW)
├── README.md             ✅ Project documentation
├── templates/
│   └── index.html        ✅ Single-page app
├── static/
│   ├── css/
│   │   └── styles.css    ✅ Glassmorphism design
│   └── js/
│       └── script.js     ✅ Frontend logic
└── uploads/              ✅ Created at runtime (max 16MB files)
```

## Steps to Deploy on Render

### 1. Push to GitHub
```bash
git add .
git commit -m "Configure for Render deployment"
git push origin main
```

### 2. Create Render Account & Web Service
1. Go to https://render.com
2. Sign up/Login
3. Click "New Web Service"
4. Select "Build and deploy from a Git repository"
5. Connect your GitHub repository

### 3. Configure Render Settings

**Build Settings:**
- Build Command: `pip install -r requirements.txt`
- Start Command: Leave blank (Procfile will be used)

**Environment Variables** (add these in Render dashboard):
```
FLASK_ENV=production
SECRET_KEY=[Generate a strong random key here]
```

**Resources:**
- Instance Type: Free tier is fine for testing
- Disk: 0.5 GB minimum

### 4. Deploy
1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repo
   - Install dependencies from requirements.txt
   - Read Procfile for startup command
   - Start the gunicorn server
   - Assign a URL like `https://your-app-name.onrender.com`

## ✅ Verification Checklist

Before pushing to Render, verify:

1. **Syntax Check** ✅
   - Run: `python -m py_compile app.py`
   - Result: No errors

2. **Local Testing** (Optional but recommended)
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set environment variables
   set FLASK_ENV=development    # Windows
   export FLASK_ENV=development # Mac/Linux
   
   # Run locally
   python app.py
   # Visit http://localhost:5000
   ```

3. **File Structure** ✅
   - Procfile exists in root
   - requirements.txt has gunicorn
   - All templates in templates/ folder
   - All static files in static/ folder

4. **Git Configuration** ✅
   - .gitignore created
   - uploads/ will not be committed
   - .env will not be committed

## Important Notes

### Security
- **Never commit `.env` to Git** - Render will ignore it
- Use Render's environment variable settings for sensitive data (SECRET_KEY)
- In production, FLASK_ENV should be "production" (not "development")

### File Uploads
- Uploads folder is created at runtime in the `/tmp` directory on cloud platforms
- Files persist only during the current session
- For persistent storage, use a cloud storage service (AWS S3, etc.)

### Performance
- Free tier instances may have startup delay
- Use "Always On" in paid plans for production

### Debugging
- Check Render logs in dashboard for errors
- Logs show Flask startup messages and request information

## Production Checklist (Before Going Live)

- [ ] SECRET_KEY is set to a strong random value in Render
- [ ] FLASK_ENV is set to "production" in Render
- [ ] Procfile is in project root and committed
- [ ] requirements.txt includes gunicorn
- [ ] app.py uses `os.getenv()` for configuration
- [ ] No hardcoded localhost or debug=True in production code
- [ ] .env file is in .gitignore
- [ ] uploads/ folder is in .gitignore
- [ ] Custom domain configured (if applicable)
- [ ] SSL/HTTPS enabled (Render provides free SSL)

## Troubleshooting

### App Won't Start
- Check Procfile syntax: should be exactly `web: gunicorn app:app`
- Verify all dependencies in requirements.txt match imports in app.py
- Check app.py has `if __name__ == '__main__':` block

### Blank Page or 500 Error
- Check Render logs for Python errors
- Verify Flask routes are returning JSON or rendering templates correctly
- Ensure templates/ folder exists and index.html is there

### File Upload Issues
- Max file size is 16MB (configured in app.py)
- For production, implement cloud storage (S3, Azure Blob, etc.)
- Temp files are cleaned up automatically

### Environment Variable Issues
- Make sure SECRET_KEY is set in Render dashboard (Environment → Environment Variables)
- FLASK_ENV should be "production" for production deployments
- Verify variable names match exactly in app.py

## Next Steps

1. ✅ **Deployment files created** - Procfile, updated requirements.txt
2. ✅ **Configuration updated** - app.py uses environment variables
3. ✅ **Safety setup** - .gitignore and .env.example created
4. **Ready to deploy** - Push to GitHub and connect to Render

Your application is now **production-ready** for deployment on Render! 🚀
