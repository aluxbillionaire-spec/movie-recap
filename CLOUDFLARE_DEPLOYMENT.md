# Cloudflare Pages Deployment Guide

This guide will help you deploy your Movie Recap Service frontend to Cloudflare Pages with automatic HTTPS and optional Workers for dynamic functionality.

## 📋 Prerequisites

- Cloudflare account (free tier is sufficient)
- GitHub account and repository
- Node.js 18+ and npm installed locally

## 🚀 Quick Deployment Summary

**Inputs for this deployment:**
- **REPO_URL**: `https://github.com/<your-username>/<your-repo-name>`
- **BRANCH**: `main`
- **BUILD_COMMAND**: `cd frontend && npm ci && npm run build`
- **PUBLISH_DIR**: `frontend/dist`
- **ADD_WORKER**: `true` (for API endpoints)
- **CUSTOM_DOMAIN**: Optional (e.g., `your-domain.com`)

## 📁 Project Structure

```
movie-recap-service/
├── frontend/           # React + Vite frontend
│   ├── dist/          # Build output (auto-generated)
│   ├── src/           # Source code
│   ├── package.json   # Dependencies
│   └── vite.config.ts # Vite configuration
├── backend/           # Python FastAPI backend (not deployed to Pages)
├── _headers           # Cloudflare headers configuration
├── _redirects         # Cloudflare redirects configuration
└── cloudflare/        # Worker scripts and configuration
```

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Initialize Git Repository** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Create GitHub Repository**:
   - Go to GitHub.com
   - Create a new repository
   - Push your code:
```bash
git remote add origin https://github.com/<username>/<repo-name>
git branch -M main
git push -u origin main
```

### Step 2: Configure Cloudflare Pages

1. **Sign in to Cloudflare Dashboard**:
   - Go to [dash.cloudflare.com](https://dash.cloudflare.com)
   - Sign up for free account if needed

2. **Create Pages Project**:
   - Navigate to Pages in left sidebar
   - Click "Create a project"
   - Choose "Connect to Git"
   - Select your GitHub repository

3. **Configure Build Settings**:
   ```
   Framework preset: None (Custom)
   Build command: cd frontend && npm ci && npm run build
   Build output directory: frontend/dist
   Root directory: / (leave empty for root)
   ```

4. **Environment Variables** (if needed):
   ```
   NODE_VERSION=18
   NPM_VERSION=9
   ```

### Step 3: Custom Build Configuration

The frontend is configured with Vite and will build to `frontend/dist`. The build includes:
- Code splitting for optimal loading
- Tree shaking for smaller bundles
- Source maps for debugging
- Asset optimization

### Step 4: Deploy and Verify

1. **Initial Deployment**:
   - Click "Save and Deploy"
   - Wait for build to complete (usually 2-3 minutes)
   - Get your site URL: `https://<project-name>.pages.dev`

2. **Verify HTTPS**:
```bash
curl -I https://<project-name>.pages.dev
```

Expected response:
```
HTTP/2 200
cf-ray: ...
cf-cache-status: DYNAMIC
strict-transport-security: max-age=31536000; includeSubDomains; preload
```

### Step 5: Custom Domain (Optional)

1. **Add Custom Domain**:
   - In Pages project settings → Custom domains
   - Add your domain (e.g., `movierecap.yourdomain.com`)

2. **Update DNS Records**:
   - Add CNAME record pointing to your Pages URL
   - Or use Cloudflare nameservers for full management

3. **SSL Certificate**:
   - Automatic provisioning (usually takes 5-15 minutes)
   - Universal SSL included in free plan

### Step 6: Cloudflare Worker for API (Optional)

If you need dynamic functionality, deploy a Worker:

1. **Install Wrangler CLI**:
```bash
npm install -g wrangler
wrangler login
```

2. **Create Worker**:
```bash
wrangler init movie-recap-worker
```

3. **Configure Worker Routes**:
   - Route: `movierecap.yourdomain.com/api/*`
   - Or use Pages Functions (recommended)

## 🔍 Verification Steps

### Test Frontend Deployment

1. **Basic Functionality**:
```bash
curl -I https://<project-name>.pages.dev
# Should return 200 OK with HTML content
```

2. **Asset Loading**:
```bash
curl -I https://<project-name>.pages.dev/assets/index-[hash].js
# Should return 200 OK with JavaScript content-type
```

3. **SPA Routing**:
```bash
curl -I https://<project-name>.pages.dev/dashboard
# Should return 200 OK (redirected to index.html)
```

### Test Custom Domain (if configured)

```bash
curl -I https://your-custom-domain.com
# Should return 200 OK with proper SSL headers
```

### Test Worker Endpoints (if configured)

```bash
curl https://<project-name>.pages.dev/api/health
# Should return JSON response from Worker
```

## 📊 Performance Optimization

### Headers Configuration (`_headers`)
```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/api/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: Content-Type, Authorization
```

### Redirects Configuration (`_redirects`)
```
# SPA routing
/*    /index.html   200

# API routing to Worker
/api/*    /api/:splat    200
```

## 🔐 Security Features

### Automatic HTTPS
- Free SSL/TLS certificates
- HTTP to HTTPS redirects
- HSTS headers
- Modern TLS protocols only

### DDoS Protection
- Built-in Cloudflare protection
- Rate limiting available
- Bot management included

### Headers Security
- CSP (Content Security Policy)
- XSS protection
- CSRF protection
- Clickjacking prevention

## 📈 Monitoring and Analytics

### Pages Analytics
- Page views and unique visitors
- Geographic distribution
- Performance metrics
- Core Web Vitals

### Worker Analytics (if using Workers)
- Request count and duration
- Error rates
- CPU time usage
- Memory usage

## 🚨 Troubleshooting

### Build Failures

1. **Node.js Version Issues**:
   - Set `NODE_VERSION=18` in environment variables
   - Ensure `package.json` has correct engines field

2. **Build Command Issues**:
   - Verify build command: `cd frontend && npm ci && npm run build`
   - Check build output directory: `frontend/dist`

3. **Dependency Issues**:
   - Use `npm ci` instead of `npm install` for reproducible builds
   - Lock file should be committed to repository

### SSL Certificate Issues

1. **Certificate Provisioning Delays**:
   - Can take up to 24 hours for custom domains
   - Verify DNS records are correct
   - Check domain ownership

2. **Mixed Content Warnings**:
   - Ensure all assets use HTTPS URLs
   - Update API endpoints to use HTTPS

### Performance Issues

1. **Slow Loading**:
   - Enable asset optimization in Pages settings
   - Use Cloudflare CDN for global distribution
   - Implement code splitting in build

2. **Large Bundle Sizes**:
   - Review Vite build configuration
   - Enable tree shaking
   - Use dynamic imports for large components

## 💰 Cost Considerations

### Cloudflare Pages (Free Tier)
- ✅ 500 builds per month
- ✅ Unlimited requests and bandwidth
- ✅ Custom domains with SSL
- ✅ Global CDN
- ✅ DDoS protection

### Cloudflare Workers (Free Tier)
- ✅ 100,000 requests per day
- ✅ 10ms CPU time per request
- ⚠️ Paid plans for higher limits

### Recommended Approach
- Use Pages for static frontend (completely free)
- Use Workers sparingly for critical dynamic features only
- Consider external APIs for heavy backend processing

## 🎯 Production Checklist

- [ ] Repository is public or properly configured for deployment
- [ ] Build command works locally: `cd frontend && npm run build`
- [ ] Environment variables configured in Cloudflare Pages
- [ ] Custom domain configured (if required)
- [ ] SSL certificate provisioned and working
- [ ] Headers and redirects configured
- [ ] Performance optimizations enabled
- [ ] Analytics and monitoring set up
- [ ] Security headers implemented
- [ ] Error pages customized
- [ ] SEO meta tags included

## 🔗 Useful Links

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [Pages Functions Documentation](https://developers.cloudflare.com/pages/functions/)

---

**Next Steps**: Follow the deployment steps above, and your Movie Recap Service will be live on Cloudflare's global network with automatic HTTPS!