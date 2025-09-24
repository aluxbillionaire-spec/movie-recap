# Cloudflare Pages Deployment Commands

## 🚀 Required Deploy Commands

### Step 1: Prepare Your Repository
```bash
# Initialize Git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial deployment to Cloudflare Pages"

# Create GitHub repository first at github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
git branch -M main
git push -u origin main
```

### Step 2: Test Build Locally (Verify Everything Works)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm ci

# Test the build command that Cloudflare will use
npm run build

# Verify build output
ls dist/
```

### Step 3: Cloudflare Pages Setup Commands

**Manual Setup (Recommended):**
1. Go to https://dash.cloudflare.com/pages
2. Click "Create a project" → "Connect to Git"
3. Select your GitHub repository
4. Use these **exact settings**:

```
Framework preset: None
Build command: cd frontend && npm ci && npm run build
Build output directory: frontend/dist
Root directory: (leave empty)
Environment variables:
  NODE_VERSION=18
```

**Alternative: Wrangler CLI Method:**
```bash
# Install Wrangler CLI globally
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy Pages project
wrangler pages project create movie-recap-service

# Deploy from your built frontend
cd frontend
npm run build
wrangler pages deploy dist --project-name=movie-recap-service
```

### Step 4: Deploy Optional Cloudflare Worker
```bash
# Navigate to worker directory
cd ../cloudflare

# Deploy the worker
wrangler deploy worker.js --name movie-recap-worker

# Set up worker route (optional)
wrangler route add "your-domain.com/api/*" movie-recap-worker
```

### Step 5: Verify Deployment
```bash
# Test your deployed site (replace with your actual URL)
curl -I https://movie-recap-service.pages.dev

# Test SPA routing
curl -I https://movie-recap-service.pages.dev/dashboard

# Test API endpoints (if worker deployed)
curl https://movie-recap-service.pages.dev/api/health
```

## 🔧 Automated Deploy Script

Run the deployment script I created for you:

**Windows:**
```cmd
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

## ⚡ Quick One-Command Deploy

If you want to deploy everything in one go:

```bash
# Build and prepare for deployment
cd frontend && npm ci && npm run build && cd .. && git add . && git commit -m "Deploy to Cloudflare Pages" && git push origin main
```

## 🎯 Essential Commands Summary

**Minimum required commands:**
1. `cd frontend && npm ci && npm run build` - Build the frontend
2. `git add . && git commit -m "Deploy" && git push` - Push to GitHub
3. Set up Cloudflare Pages with build command: `cd frontend && npm ci && npm run build`
4. Set publish directory: `frontend/dist`

**Your site will be live at:** `https://YOUR_PROJECT_NAME.pages.dev`

## 🆘 If Build Fails

**Debug build issues:**
```bash
cd frontend
npm ci
npm run build --verbose
```

**Check build output:**
```bash
ls -la frontend/dist/
```

**Common fixes:**
- Ensure Node.js 18+ in Cloudflare environment variables
- Verify build command is exactly: `cd frontend && npm ci && npm run build`
- Check that `frontend/dist/` contains `index.html`