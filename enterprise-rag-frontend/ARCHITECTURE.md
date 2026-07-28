# Frontend Architecture

Complete architecture overview of Enterprise RAG Frontend.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser / Client                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │          React Application (SPA)                │   │
│  ├─────────────────────────────────────────────────┤   │
│  │                                                   │   │
│  │  ┌──────────────┐  ┌──────────────────┐        │   │
│  │  │   Router     │  │   Layout System  │        │   │
│  │  │  (react-    │  │  DashboardLayout │        │   │
│  │  │  router-dom)│  │   AuthLayout     │        │   │
│  │  └──────────────┘  └──────────────────┘        │   │
│  │                                                   │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │          Pages                           │  │   │
│  │  ├──────────────────────────────────────────┤  │   │
│  │  │ • Home          • Chat                   │  │   │
│  │  │ • Dashboard     • Blog                   │  │   │
│  │  │ • Documents     • Settings               │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │                                                   │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │        Reusable Components               │  │   │
│  │  ├──────────────────────────────────────────┤  │   │
│  │  │ UI (Button, Card, Input, Badge)          │  │   │
│  │  │ Chat (ChatWindow, ChatBubble, Input)     │  │   │
│  │  │ Blog (BlogCard, VennDiagram)             │  │   │
│  │  │ Upload (UploadBox, UploadProgress)       │  │   │
│  │  │ Dashboard (StatsCard, Charts)            │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │                                                   │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │        State Management (Zustand)        │  │   │
│  │  ├──────────────────────────────────────────┤  │   │
│  │  │ • authStore      • settingsStore         │  │   │
│  │  │ • chatStore      • documentStore         │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │                                                   │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │        Custom Hooks                      │  │   │
│  │  ├──────────────────────────────────────────┤  │   │
│  │  │ • useChat        • useDocuments          │  │   │
│  │  │ • useUpload      • useTheme              │  │   │
│  │  │ • useAuth        • useSettings           │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │                                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                       ↓                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │        API Layer (Axios)                       │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ • api/chat.ts      • api/documents.ts          │   │
│  │ • api/upload.ts    • api/health.ts             │   │
│  └─────────────────────────────────────────────────┘   │
│                       ↓                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │        Utilities & Services                    │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ • a11y (Accessibility)                        │   │
│  │ • performance (Metrics & Optimization)        │   │
│  │ • validation (Input Validation)               │   │
│  │ • formatting (Text & Date Formatting)         │   │
│  └─────────────────────────────────────────────────┘   │
│                       ↓                                  │
└─────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Backend API Server           │
        │  (http://localhost:8000)      │
        │                               │
        │  • /chat                      │
        │  • /documents                 │
        │  • /upload                    │
        │  • /health                    │
        └───────────────────────────────┘
```

## 📂 Component Hierarchy

```
App
├── Router
│   ├── Home (/)
│   │   ├── Header (Navigation)
│   │   ├── HeroSection
│   │   ├── FeaturesGrid
│   │   ├── StatsSection
│   │   └── Footer
│   │
│   ├── DashboardLayout
│   │   ├── Sidebar
│   │   │   ├── Logo
│   │   │   ├── NewChatButton
│   │   │   ├── Navigation
│   │   │   └── UserProfile
│   │   │
│   │   ├── Header
│   │   │   ├── MenuButton (Mobile)
│   │   │   ├── Title
│   │   │   └── FeedbackButton
│   │   │
│   │   └── Main Content
│   │       ├── Chat (/chat)
│   │       │   ├── UploadBox (when empty)
│   │       │   ├── ChatMessages
│   │       │   │   ├── ChatBubble (User)
│   │       │   │   └── ChatBubble (AI)
│   │       │   ├── TypingIndicator
│   │       │   └── ChatInput
│   │       │
│   │       ├── Dashboard (/dashboard)
│   │       │   ├── PageHeader
│   │       │   ├── StatsGrid
│   │       │   │   ├── StatCard
│   │       │   │   ├── StatCard
│   │       │   │   ├── StatCard
│   │       │   │   └── StatCard
│   │       │   ├── Charts
│   │       │   │   ├── LineChart (Queries)
│   │       │   │   └── PieChart (Document Types)
│   │       │   └── RecentDocuments
│   │       │       └── Table
│   │       │
│   │       ├── Blog (/blog)
│   │       │   ├── HeroSection
│   │       │   ├── OurStorySection
│   │       │   │   ├── VennDiagram
│   │       │   │   └── StoryText
│   │       │   ├── SearchBar
│   │       │   ├── CategoryFilter
│   │       │   └── BlogGrid
│   │       │       └── EnhancedBlogCard (×5+)
│   │       │
│   │       ├── Documents (/documents)
│   │       ├── Settings (/settings)
│   │       └── Analytics (/analytics)
│   │
│   ├── Login (/login)
│   └── NotFound (*）
```

## 🔄 Data Flow

```
User Action
    ↓
React Component
    ↓
Event Handler / Custom Hook
    ↓
State Update (Zustand Store)
    ↓
API Call (Axios)
    ↓
Backend
    ↓
Response
    ↓
State Update
    ↓
Component Re-render (with Animations)
    ↓
UI Update
```

## 🗂️ File Organization

### Components by Layer

```
components/
├── ui/                  ← Atomic: Buttons, Cards, Inputs
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Input.tsx
│   ├── Badge.tsx
│   └── index.ts
│
├── layout/              ← Layouts: Header, Sidebar
│   ├── Header.tsx
│   └── Sidebar.tsx
│
├── common/              ← Common: Loading, Error, Empty
│   ├── LoadingSpinner.tsx
│   ├── ErrorBoundary.tsx
│   └── EmptyState.tsx
│
├── chat/                ← Feature: Chat
│   ├── ChatWindow.tsx
│   ├── ChatBubble.tsx
│   ├── ChatInput.tsx
│   └── TypingIndicator.tsx
│
├── blog/                ← Feature: Blog
│   ├── EnhancedBlogCard.tsx
│   ├── VennDiagram.tsx
│   └── BlogGrid.tsx
│
├── upload/              ← Feature: Upload
│   ├── UploadBox.tsx
│   ├── UploadProgress.tsx
│   └── FileList.tsx
│
└── dashboard/           ← Feature: Dashboard
    ├── StatsCard.tsx
    ├── RecentDocuments.tsx
    ├── RetrievalChart.tsx
    └── ModelCard.tsx
```

## 🔌 State Management

### Zustand Stores

```
store/
├── authStore          ← Authentication state
│   ├── user
│   ├── isAuthenticated
│   ├── login()
│   └── logout()
│
├── chatStore          ← Chat state
│   ├── sessions[]
│   ├── activeSession
│   ├── isGenerating
│   ├── sendMessage()
│   └── createSession()
│
├── documentStore      ← Documents state
│   ├── documents[]
│   ├── loading
│   ├── deleteDocument()
│   └── reindexDocument()
│
└── settingsStore      ← Settings state
    ├── llmProvider
    ├── embeddingModel
    ├── updateSettings()
    └── resetSettings()
```

## 🎨 Styling Architecture

```
styles/
├── globals.css                  ← Global styles + Tailwind
│   ├── CSS Variables
│   ├── @tailwind directives
│   ├── Custom utility classes
│   └── Scrollbar styles
│
tailwind.config.js              ← Tailwind configuration
├── colors (brand colors)
├── fonts (Manrope, DM Mono)
├── animations (Framer Motion)
├── spacing scale
└── breakpoints

Component-level:
├── Inline Tailwind classes
├── Responsive modifiers (md:, lg:, xl:)
├── Hover/focus states
└── Dark mode support
```

## 🔌 API Integration

### Axios Configuration

```
api/
├── axios.ts                ← Axios instance
│   ├── baseURL
│   ├── interceptors
│   └── errorHandler
│
├── chat.ts                 ← Chat endpoints
│   └── askChat()
│
├── documents.ts            ← Document endpoints
│   ├── getDocuments()
│   ├── deleteDocument()
│   └── reindexDocument()
│
├── upload.ts               ← Upload endpoints
│   └── uploadDocument()
│
└── health.ts               ← Health check
    └── getHealth()
```

### API Request Flow

```
Component
    ↓
Custom Hook (useChat, useDocuments, etc.)
    ↓
Zustand Store
    ↓
API Function (axios)
    ↓
Backend Endpoint
    ↓
Response
    ↓
State Update
    ↓
Component Update
```

## 🎬 Animation System

### Framer Motion Implementation

```
Animations by Type:

1. Page Transitions
   - initial={{ opacity: 0 }}
   - animate={{ opacity: 1 }}
   - exit={{ opacity: 0 }}

2. Element Entrance
   - slideUp (y: -20 → 0)
   - fadeIn (opacity: 0 → 1)

3. Interactive Hover
   - whileHover={{ y: -4 }}
   - whileTap={{ scale: 0.95 }}

4. Container Stagger
   - staggerChildren for cascading effects

5. Gesture Animations
   - Drag
   - Pan
   - Scroll-triggered
```

## 📊 Data Flow Examples

### Upload Document Flow

```
User selects file
    ↓
UploadBox component
    ↓
handleFileUpload() hook
    ↓
useUpload() custom hook
    ↓
uploadDocument() API call (axios)
    ↓
documentStore.addDocument()
    ↓
Component re-renders
    ↓
UploadProgress shown
    ↓
Success message
```

### Chat Query Flow

```
User types message
    ↓
ChatInput component
    ↓
sendMessage() function
    ↓
useChat() custom hook
    ↓
chatStore.addMessage()
    ↓
askChat() API call
    ↓
streamResponse() handler
    ↓
ChatBubble renders response
    ↓
Scroll to bottom
```

## 🔐 Security Layers

```
Input Layer
├── HTML sanitization
├── XSS prevention
└── Input validation

API Layer
├── HTTPS/TLS
├── CORS headers
├── Authentication tokens
└── Rate limiting

Storage Layer
├── No sensitive data in localStorage
├── Secure token storage
└── HTTPOnly cookies

Output Layer
├── XSS prevention
├── Content-Security-Policy
└── CSRF tokens
```

## 📈 Performance Optimizations

```
Code Level
├── Code splitting (routes)
├── Lazy loading (components)
├── Memoization (useMemo, useCallback)
└── Debounce/Throttle (utilities)

Bundle Level
├── Tree shaking
├── CSS purging
├── Minification
└── Compression

Runtime Level
├── Virtual scrolling
├── Image lazy loading
├── Resource prefetching
└── Service workers (PWA)
```

## 🧪 Testing Architecture

```
tests/
├── unit/
│   ├── utils/
│   │   ├── formatting.test.ts
│   │   ├── validation.test.ts
│   │   └── performance.test.ts
│   │
│   └── stores/
│       ├── chatStore.test.ts
│       └── authStore.test.ts
│
├── integration/
│   ├── api.test.ts
│   └── components.test.tsx
│
└── e2e/
    ├── chat.e2e.ts
    ├── blog.e2e.ts
    └── upload.e2e.ts
```

## 🔄 Deployment Architecture

```
Development
    ↓
npm run dev
    ↓ (on git push)
GitHub Actions
    ↓
npm run type-check
npm run build
npm run test
    ↓ (if passing)
Deploy to Vercel/Docker/Static Host
    ↓
CDN Cache (Cloudflare/CloudFront)
    ↓
End Users
```

---

**Total Layers**: 7 (UI, Component, Logic, State, API, Backend, Infrastructure)
**Architectural Pattern**: Component-driven, hooks-based, store pattern
**State Management**: Centralized (Zustand)
**Data Flow**: Unidirectional (Redux-like)
**Styling**: Utility-first (Tailwind) + custom CSS
**Performance**: Optimized with code splitting and lazy loading
