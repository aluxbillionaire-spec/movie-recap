# Movie Recap Service - Frontend

A professional, modern React frontend for the Movie Recap Service. Built with TypeScript, Tailwind CSS, and modern development practices.

## 🚀 Features

### 🎨 Modern UI/UX
- **Clean, Professional Design** - Minimalist interface with intuitive navigation
- **Responsive Layout** - Works seamlessly on desktop, tablet, and mobile
- **Dark/Light Mode** - User preference with system detection
- **Accessible** - WCAG 2.1 AA compliant with proper ARIA labels

### 🔐 Authentication & Security
- **JWT-based Authentication** - Secure token-based auth with refresh tokens
- **Protected Routes** - Route-level security with role-based access
- **Form Validation** - Client-side validation with server-side verification
- **CSRF Protection** - Built-in CSRF token handling

### 📊 Dashboard & Analytics
- **Real-time Stats** - Live project and job statistics
- **Interactive Charts** - Beautiful charts using Recharts
- **Progress Tracking** - Real-time job progress with WebSocket updates
- **Quick Actions** - One-click access to common tasks

### 🎬 Project Management
- **Project Creation** - Intuitive project setup with configuration options
- **Project Gallery** - Grid/list view with search and filtering
- **Bulk Operations** - Multi-select actions for efficiency
- **Status Tracking** - Visual status indicators and progress bars

### 📁 File Management
- **Drag & Drop Upload** - Modern file upload with progress tracking
- **Preview Support** - Video and document preview before processing
- **Bulk Upload** - Multiple file upload with queue management
- **File Organization** - Categorization and tagging system

### ⚡ Performance
- **Lazy Loading** - Code splitting and route-based lazy loading
- **Optimized Bundles** - Tree shaking and bundle optimization
- **Caching Strategy** - Smart caching with React Query
- **Fast Builds** - Vite for lightning-fast development builds

## 🛠️ Tech Stack

### Core Framework
- **React 18** - Latest React with concurrent features
- **TypeScript** - Full type safety and enhanced DX
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing with nested routes

### State Management
- **Zustand** - Lightweight state management
- **React Query** - Server state management and caching
- **React Hook Form** - Performant form handling

### Styling & UI
- **Tailwind CSS** - Utility-first CSS framework
- **Headless UI** - Accessible UI components
- **Framer Motion** - Smooth animations and transitions
- **Lucide React** - Beautiful SVG icons

### Development Tools
- **ESLint** - Code linting with TypeScript support
- **Prettier** - Code formatting
- **Vitest** - Fast unit testing
- **Storybook** - Component development and documentation

## 📦 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # Base UI components
│   │   ├── forms/         # Form components
│   │   ├── layouts/       # Layout components
│   │   └── features/      # Feature-specific components
│   ├── pages/             # Page components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API service layers
│   ├── stores/            # Zustand stores
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   └── styles/            # Global styles and themes
├── tests/                 # Test files
└── docs/                  # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm 9+ or yarn 3+
- Backend service running on port 8000

### Installation

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start development server**
```bash
npm run dev
```

4. **Open in browser**
```
http://localhost:3000
```

### Available Scripts

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm run test         # Run unit tests
npm run test:ui      # Run tests with UI
npm run test:coverage # Generate coverage report

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors
npm run type-check   # TypeScript type checking

# Storybook
npm run storybook    # Start Storybook dev server
npm run build-storybook # Build Storybook
```

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000

# Application
VITE_APP_NAME="Movie Recap Service"
VITE_ENVIRONMENT=development

# Features
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true

# File Upload
VITE_MAX_FILE_SIZE=5368709120  # 5GB
VITE_ALLOWED_VIDEO_TYPES=video/mp4,video/avi
VITE_ALLOWED_SCRIPT_TYPES=text/plain,application/pdf

# WebSocket
VITE_WS_URL=ws://localhost:8000/ws
```

### Tailwind Configuration

The project uses a custom Tailwind configuration with:
- Extended color palette for brand consistency
- Custom spacing and sizing utilities
- Animation and transition presets
- Component-specific utility classes

### API Integration

The frontend integrates with the backend through:
- **REST API** - Full CRUD operations for all resources
- **WebSocket** - Real-time updates for job progress
- **File Upload** - Chunked upload with progress tracking
- **Authentication** - JWT tokens with automatic refresh

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px  
- **Desktop**: 1024px - 1280px
- **Large**: > 1280px

### Mobile Features
- Touch-optimized interfaces
- Swipe gestures for navigation
- Mobile-specific layouts
- Optimized performance for slower connections

## 🧪 Testing

### Unit Tests
```bash
npm run test
```

### Component Testing
```bash
npm run test:ui
```

### E2E Testing
```bash
npm run test:e2e
```

### Coverage Reports
```bash
npm run test:coverage
```

## 🚀 Deployment

### Docker Deployment

1. **Build Docker image**
```bash
docker build -t movie-recap-frontend .
```

2. **Run container**
```bash
docker run -p 80:80 movie-recap-frontend
```

### Production Build

1. **Build for production**
```bash
npm run build
```

2. **Serve static files**
```bash
npm run preview
```

### Environment Setup

For production deployment:

1. Set production environment variables
2. Configure proper API endpoints
3. Enable analytics and monitoring
4. Set up CDN for static assets
5. Configure caching headers

## 🔒 Security

### Implemented Security Measures

- **Content Security Policy** - Prevents XSS attacks
- **CSRF Protection** - Token-based CSRF prevention
- **Input Sanitization** - All user inputs are sanitized
- **Secure Headers** - Security headers in nginx config
- **Authentication** - JWT with secure storage
- **Route Protection** - Protected routes with auth guards

### Security Best Practices

- Never store sensitive data in localStorage
- Always validate and sanitize user inputs
- Use HTTPS in production
- Implement proper error handling
- Regular security audits and updates

## 📊 Performance

### Optimization Techniques

- **Code Splitting** - Route-based and component-based splitting
- **Lazy Loading** - Images and components loaded on demand
- **Bundle Optimization** - Tree shaking and dead code elimination
- **Caching Strategy** - Smart caching with React Query
- **Image Optimization** - WebP format with fallbacks

### Performance Metrics

Target performance metrics:
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Time to Interactive**: < 3.5s
- **Cumulative Layout Shift**: < 0.1

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#3B82F6)
- **Secondary**: Gray (#6B7280)
- **Success**: Green (#10B981)
- **Warning**: Amber (#F59E0B)
- **Error**: Red (#EF4444)

### Typography
- **Font Family**: Inter (Primary), JetBrains Mono (Code)
- **Font Sizes**: 12px - 72px with responsive scaling
- **Line Heights**: Optimized for readability

### Components
- Consistent spacing and sizing
- Accessible color contrasts
- Hover and focus states
- Loading and error states

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make changes and test**
```bash
npm run test
npm run lint
npm run type-check
```

4. **Commit changes**
```bash
git commit -m 'Add amazing feature'
```

5. **Push to branch**
```bash
git push origin feature/amazing-feature
```

6. **Create Pull Request**

### Code Standards

- Use TypeScript for all new code
- Follow ESLint configuration
- Write tests for new features
- Update documentation
- Use semantic commit messages

## 📚 Documentation

- **Component Documentation**: Available in Storybook
- **API Documentation**: OpenAPI specs at `/docs`
- **Architecture Guide**: See `docs/architecture.md`
- **Deployment Guide**: See `docs/deployment.md`

## 🐛 Troubleshooting

### Common Issues

1. **Build Errors**
   - Check Node.js version (18+)
   - Clear node_modules and reinstall
   - Verify environment variables

2. **API Connection Issues**
   - Check backend server is running
   - Verify API endpoints in .env
   - Check CORS configuration

3. **Authentication Issues**
   - Clear browser storage
   - Check JWT token expiration
   - Verify backend auth configuration

### Debug Mode

Enable debug mode with:
```bash
VITE_ENABLE_DEBUG=true npm run dev
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **React Team** - For the amazing framework
- **Vercel** - For Vite and excellent DX
- **Tailwind CSS** - For the utility-first CSS framework
- **Lucide** - For beautiful icons
- **Contributors** - Everyone who helped build this project

---

**Built with ❤️ for creating amazing movie recaps**