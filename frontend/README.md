# Enterprise RAG — Frontend

A modern React frontend for the Enterprise RAG backend. Built with Vite, TypeScript, Tailwind CSS, shadcn/ui components, TanStack Query, and React Router.

## Prerequisites

- Node.js 18+
- The Enterprise RAG backend running on `http://localhost:8000`

## Quick Start

```bash
# Install dependencies
npm install

# Start the dev server (with Vite proxy to backend)
npm run dev
```

The dev server starts on `http://localhost:5173` and proxies `/api` requests to `http://localhost:8000`.

## Connecting to the Backend

### Development (with Vite proxy — default)

The Vite dev server is configured with a proxy so you don't need CORS:

```
vite.config.ts → server.proxy: { '/api': { target: 'http://localhost:8000' } }
```

Just run the backend on port 8000 and `npm run dev` for the frontend.

### Production / Different Backend URL

Set the `VITE_API_URL` environment variable in `.env`:

```env
VITE_API_URL=https://your-backend.com
```

When `VITE_API_URL` is set, the API client will use this as the base URL directly (no proxy needed). The backend must enable CORS for your frontend domain.

### Changing the Backend URL

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

For production builds:

```bash
VITE_API_URL=https://api.yourcompany.com npm run build
```

## Build for Production

```bash
npm run build
```

Output is in `dist/`. The backend serves these static files at the root (see `app/main.py`).

## Project Structure

```
src/
├── api/              # Typed API client per resource (auth, knowledge, chat, analytics, health)
├── components/
│   ├── ui/           # shadcn/ui components (Button, Card, Dialog, Input, etc.)
│   ├── layout/       # AppLayout, Sidebar, ProtectedRoute
│   └── shared/       # PageHeader, LoadingState, EmptyState, ErrorState
├── context/          # AuthContext (login, register, logout, user state)
├── hooks/            # TanStack Query hooks for each resource
├── lib/              # Utilities (cn, formatBytes, api-client with interceptors)
├── pages/            # Route pages (Login, Register, Dashboard, KBs, Chat, Analytics)
├── routes/           # React Router configuration
├── types/            # TypeScript interfaces matching backend responses
├── App.tsx           # Root component with providers
├── main.tsx          # Entry point
└── index.css         # Tailwind CSS with custom theme
```

## Features

- **Authentication**: Login, register, JWT token management, auto-redirect on 401
- **Dashboard**: Summary cards and KB overview
- **Knowledge Bases**: CRUD, upload documents, view history, reindex, delete with confirmation
- **Chat**: Real-time Q&A with KB filtering, source citations, token/latency metadata
- **Analytics**: Query performance (p50/p95/p99), upload metrics, usage breakdown with period selector
- **Error Handling**: Global axios interceptor with toast notifications, retry on error states
- **Loading States**: Skeleton loaders, card skeletons, table skeletons
- **Empty States**: Friendly messages with action buttons for empty resources
- **Responsive**: Sidebar layout with scrollable content areas
