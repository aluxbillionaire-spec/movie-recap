#!/bin/bash

# Cloudflare Pages Deployment Script
# This script helps you deploy your Movie Recap Service to Cloudflare Pages

set -e

echo "🚀 Movie Recap Service - Cloudflare Pages Deployment"
echo "=================================================="

# Check if Git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Initializing..."
    git init
    git add .
    git commit -m "Initial commit for Cloudflare Pages deployment"
fi

# Check if frontend build works
echo "🔨 Testing frontend build..."
cd frontend
npm ci
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful!"
    echo "📁 Build output located in: frontend/dist/"
    echo "📊 Build stats:"
    ls -la dist/
else
    echo "❌ Frontend build failed!"
    exit 1
fi

cd ..

echo ""
echo "🌐 DEPLOYMENT CONFIGURATION"
echo "=========================="
echo "✅ Repository URL: https://github.com/<your-username>/<your-repo>"
echo "✅ Branch: main"
echo "✅ Build Command: cd frontend && npm ci && npm run build"
echo "✅ Publish Directory: frontend/dist"
echo "✅ Node.js Version: 18+"
echo ""

echo "📋 NEXT STEPS:"
echo "=============="
echo "1. Push your code to GitHub:"
echo "   git remote add origin https://github.com/<username>/<repo>"
echo "   git push -u origin main"
echo ""
echo "2. Go to Cloudflare Dashboard:"
echo "   https://dash.cloudflare.com/pages"
echo ""
echo "3. Click 'Create a project' → 'Connect to Git'"
echo ""
echo "4. Select your repository and configure:"
echo "   - Framework preset: None"
echo "   - Build command: cd frontend && npm ci && npm run build"
echo "   - Build output directory: frontend/dist"
echo ""
echo "5. Deploy and get your URL:"
echo "   https://<project-name>.pages.dev"
echo ""
echo "6. (Optional) Add custom domain and SSL"
echo ""

echo "🔧 CLOUDFLARE WORKER (Optional):"
echo "================================"
echo "If you need dynamic API endpoints:"
echo "1. Install Wrangler CLI: npm install -g wrangler"
echo "2. Login: wrangler login"
echo "3. Deploy worker: cd cloudflare && wrangler deploy worker.js"
echo ""

echo "✨ Your Movie Recap Service is ready for global deployment!"
echo "📚 See CLOUDFLARE_DEPLOYMENT.md for detailed instructions"