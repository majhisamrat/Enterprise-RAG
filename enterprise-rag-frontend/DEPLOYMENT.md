# Deployment Guide

Complete guide for deploying Enterprise RAG frontend to production.

## 🚀 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] No console errors or warnings
- [ ] Lighthouse scores: 90+ Performance, 95+ Accessibility
- [ ] Environment variables configured
- [ ] API endpoints verified
- [ ] SSL certificates ready
- [ ] CDN configured
- [ ] Analytics setup complete
- [ ] Error tracking (Sentry) configured
- [ ] Monitoring alerts configured

## 📦 Building for Production

### 1. Local Build

```bash
# Install dependencies
npm install

# Type checking
npm run type-check

# Build
npm run build

# Check bundle size
npm run build
# dist/ folder contains optimized files
```

### 2. Environment Variables

Create `.env.production`:
```
VITE_API_URL=https://api.enterprise-rag.com
VITE_GOOGLE_CLIENT_ID=your-production-google-client-id
VITE_SENTRY_DSN=your-sentry-dsn
```

## 🌐 Deployment Options

### Option 1: Vercel (Recommended)

Easiest deployment for React apps with built-in optimizations.

#### Setup

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Production deployment
vercel --prod
```

#### vercel.json Configuration

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "@api_url",
    "VITE_GOOGLE_CLIENT_ID": "@google_client_id"
  },
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, s-maxage=3600, stale-while-revalidate"
        }
      ]
    }
  ]
}
```

### Option 2: Docker

#### Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
RUN npm install -g serve
WORKDIR /app
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

#### Build and Run

```bash
# Build
docker build -t enterprise-rag-frontend .

# Run locally
docker run -p 3000:3000 enterprise-rag-frontend

# Push to registry
docker tag enterprise-rag-frontend your-registry/enterprise-rag-frontend:latest
docker push your-registry/enterprise-rag-frontend:latest
```

#### docker-compose.yml

```yaml
version: '3.8'
services:
  frontend:
    image: enterprise-rag-frontend:latest
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://api:8000
    depends_on:
      - api
  
  api:
    image: enterprise-rag-api:latest
    ports:
      - "8000:8000"
```

### Option 3: Nginx

#### nginx.conf

```nginx
server {
    listen 80;
    server_name enterprise-rag.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name enterprise-rag.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/enterprise-rag.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/enterprise-rag.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;
    gzip_vary on;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing
    location / {
        root /var/www/enterprise-rag/dist;
        try_files $uri /index.html;
        add_header Cache-Control "public, max-age=0, s-maxage=3600";
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Deployment Steps

```bash
# Build frontend
npm run build

# Copy to server
scp -r dist/* user@server:/var/www/enterprise-rag/dist/

# Reload Nginx
ssh user@server 'sudo systemctl reload nginx'
```

### Option 4: AWS (S3 + CloudFront)

#### Setup

```bash
# Build
npm run build

# Sync to S3
aws s3 sync dist/ s3://enterprise-rag-frontend/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

#### CloudFront Configuration

- Origin: S3 bucket
- Compress objects automatically: Yes
- Cache policy: Managed-Caching-Optimized
- Origin request policy: CORS-S3Origin
- Response headers policy: CORS-with-preflight

## 🔐 Security Headers

Set these headers in your deployment:

```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
Referrer-Policy: strict-origin-when-cross-origin
```

## 📊 Monitoring

### Setup Error Tracking (Sentry)

```bash
npm install @sentry/react
```

In `src/main.tsx`:
```tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

### Setup Analytics (Google Analytics)

```bash
npm install react-ga4
```

In `src/main.tsx`:
```tsx
import ReactGA from "react-ga4";

ReactGA.initialize(import.meta.env.VITE_GA_ID);
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Type checking
        run: npm run type-check
      
      - name: Build
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
      
      - name: Deploy to Vercel
        run: npx vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

## 🧪 Post-Deployment Testing

```bash
# Run smoke tests
npm run test

# Check performance
npm run build
npm run preview
# Open Lighthouse audit

# Health checks
curl https://enterprise-rag.com/health
```

## 📋 Rollback Procedure

### Vercel
```bash
vercel deployments
vercel rollback
```

### Docker
```bash
docker pull your-registry/enterprise-rag-frontend:previous-version
docker run -p 3000:3000 your-registry/enterprise-rag-frontend:previous-version
```

## 🎯 Performance Targets

- **Load time**: < 2s
- **First Contentful Paint**: < 1s
- **Lighthouse Performance**: 90+
- **Uptime**: 99.9%

## 📞 Support

For deployment issues:
1. Check error logs
2. Verify environment variables
3. Test API connectivity
4. Review deployment pipeline
5. Contact DevOps team

---

**Last Updated**: January 2024
