import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/context/AuthContext';
import {
  Zap, ArrowRight, CheckCircle2, ChevronRight, X, Sparkles,
  BookOpen, FileText, Layers, Share2, MousePointer, Copy, Download,
  Sliders, Grid, GitCommit, FileCode, Check, Globe, HelpCircle,
  ExternalLink, ArrowUpRight, LayoutDashboard, Brain
} from 'lucide-react';


// --- Sample Text Presets for Live Interactive Hero Demo ---
const HERO_TEXT_PRESETS = [
  {
    id: 'workflow',
    label: 'Document Workflow',
    text: 'Start with raw doc -> Have a doc? If yes: Copy paste into Enterprise RAG. If no: Type idea -> Spark auto-visuals -> Share with team.',
    nodes: [
      { id: '1', title: 'Start', type: 'start', label: 'Start' },
      { id: '2', title: 'Have a doc?', type: 'decision', label: 'Have a doc?' },
      { id: '3a', title: 'Copy Paste', type: 'action', label: 'Copy Paste' },
      { id: '3b', title: 'Type Idea', type: 'action', label: 'Type' },
      { id: '4', title: 'Spark Visuals', type: 'spark', label: 'Spark' },
      { id: '5', title: 'Share', type: 'end', label: 'Share' }
    ]
  },
  {
    id: 'rag',
    label: 'Enterprise RAG System',
    text: 'User query -> Query Router -> Hybrid Retrieval (Vector + BM25) -> Context Re-ranking -> LLM Synthesis -> Structured Response.',
    nodes: [
      { id: '1', title: 'User Query', type: 'start', label: 'User Query' },
      { id: '2', title: 'Router', type: 'decision', label: 'Query Router' },
      { id: '3a', title: 'Vector Search', type: 'action', label: 'Vector DB' },
      { id: '3b', title: 'BM25 Keyword', type: 'action', label: 'BM25 Index' },
      { id: '4', title: 'Re-ranker', type: 'spark', label: 'Re-ranking' },
      { id: '5', title: 'LLM Response', type: 'end', label: 'Synthesized Answer' }
    ]
  },
  {
    id: 'product',
    label: 'Feature Launch Strategy',
    text: 'User Research -> PRD Spec -> Enterprise RAG Visual Diagrams -> Team Review -> Engineering Build -> Launch.',
    nodes: [
      { id: '1', title: 'User Research', type: 'start', label: 'Research' },
      { id: '2', title: 'Write PRD', type: 'action', label: 'PRD Spec' },
      { id: '3a', title: 'Enterprise RAG Diagram', type: 'spark', label: 'Visual RAG' },
      { id: '4', title: 'Team Review', type: 'decision', label: 'Feedback' },
      { id: '5', title: 'Ship Feature', type: 'end', label: 'Launch' }
    ]
  }
];

// --- 4 Generated Blog Posts ---
interface BlogPost {
  id: string;
  title: string;
  category: string;
  readTime: string;
  date: string;
  author: {
    name: string;
    role: string;
    avatar: string;
  };
  excerpt: string;
  content: string[];
  tags: string[];
}

const BLOG_POSTS: BlogPost[] = [
  {
    id: 'visual-storytelling-docs',
    title: 'How Visual Storytelling Transforms Technical Documentation',
    category: 'Design & Docs',
    readTime: '4 min read',
    date: 'July 28, 2026',
    author: {
      name: 'Sarah Chen',
      role: 'Head of Product Experience',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80'
    },
    excerpt: 'Converting dense text into intuitive flowcharts and diagrams increases developer comprehension by over 80%. Here is how visual RAG changes user onboarding.',
    content: [
      'In today’s fast-moving software ecosystem, text-heavy documentation is one of the biggest bottlenecks to developer adoption. When engineers face 5,000 words of technical specifications without visual anchors, retention drops significantly.',
      '### Why Visual Context Matters',
      'Cognitive load theory shows that human brains process visual structures up to 60,000 times faster than raw text. By pairing text paragraphs with dynamically updated flowcharts, decision trees, and sequence diagrams, teams bridge the gap between abstract code logic and real-world execution.',
      '### Key Benefits of Auto-Generated Visuals',
      '1. Instant Clarity: New team members grasp microservice interactions in seconds rather than hours.\n2. Reduced Maintenance: When your specs update, visual diagrams refresh automatically without tedious manual vector edits.\n3. Better Cross-Functional Alignment: Product managers, QA testers, and software architects view the exact same source of truth.',
      '### Implementing Enterprise RAG in Your Workspace',
      'With Enterprise RAG, copying text from Notion, Google Docs, or markdown files instantly yields publication-ready visuals. Try pasting your system design spec into Enterprise RAG to see the transformation in real-time.'
    ],
    tags: ['Documentation', 'UX Design', 'Visual RAG', 'Productivity']
  },
  {
    id: 'ai-diagramming-architecture',
    title: 'Turning Raw Text into Flowcharts and Diagrams with AI',
    category: 'AI Tech & RAG',
    readTime: '6 min read',
    date: 'July 24, 2026',
    author: {
      name: 'Alex Rivera',
      role: 'Principal AI Architect',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80'
    },
    excerpt: 'Explore the technical architecture behind parsing natural language text into vector graphics, decision nodes, and aesthetic visual structures automatically.',
    content: [
      'Visual diagram generation has evolved beyond simple template pickers. Modern AI models analyze sentence grammar, entity relationships, and causal logic to synthesize dynamic diagram layouts.',
      '### Structural Parsing Engine',
      'When text is input into Enterprise RAG, our parser executes a three-phase pipeline:',
      '1. Entity & Action Extraction: Identifying key steps, conditions (if/else), parallel paths, and outcomes.\n2. Graph Topography Synthesis: Constructing directed acyclic graphs (DAGs) representing flow direction.\n3. Aesthetic Layout Engine: Applying color harmony, node spacing, and vector icons based on design tokens.',
      '### The Future of Visual Interfaces',
      'As AI agents assist in drafting technical docs and enterprise knowledge bases, text and visuals will no longer be separate static artifacts—they will exist as fluid, interconnected knowledge graphs.'
    ],
    tags: ['Artificial Intelligence', 'LLM Parsing', 'Diagramming', 'System Design']
  },
  {
    id: 'essential-visual-frameworks',
    title: '10 Essential Visual Frameworks Every Product Team Needs',
    category: 'Product Strategy',
    readTime: '5 min read',
    date: 'July 19, 2026',
    author: {
      name: 'Elena Rostova',
      role: 'VP of Product Design',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'
    },
    excerpt: 'From decision trees to Venn diagrams and mind maps: selecting the right visual format for your specs, roadmaps, and executive pitch decks.',
    content: [
      'Choosing the right visual framework determines whether your audience understands your vision instantly or leaves confused. Here are the top 4 visual patterns used by leading product teams:',
      '### 1. Process Flowcharts',
      'Ideal for user onboarding flows, API request cycles, and authentication logic. Clear directional arrows guide readers step-by-step.',
      '### 2. Venn Diagrams & Overlaps',
      'Perfect for showing shared features between product tiers, competitive positioning, or multi-disciplinary team responsibilities.',
      '### 3. Decision Trees (If / Else Logic)',
      'Essential for troubleshooting guides, customer support escalations, and feature flag routing.',
      '### 4. Concentric Mind Maps',
      'Best for brainstorming feature sets, organizing enterprise RAG knowledge collections, or mapping product architecture components.',
      'Enterprise RAG allows you to switch between all these visual frameworks with a single click, instantly transforming your text into any desired visual layout.'
    ],
    tags: ['Product Management', 'Frameworks', 'Design Systems', 'Workflows']
  },
  {
    id: 'notes-to-presentations-workflow',
    title: 'From Notes to Presentations: Streamlining Enterprise Workflows',
    category: 'Enterprise RAG',
    readTime: '3 min read',
    date: 'July 15, 2026',
    author: {
      name: 'Marcus Vance',
      role: 'Enterprise Solutions Director',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80'
    },
    excerpt: 'Learn how modern organizations convert messy meeting notes and specs into presentation-ready visuals in seconds without manual graphic design.',
    content: [
      'Enterprise teams waste hundreds of hours every week manually drawing shapes in PowerPoint or Figma just to explain simple processes to stakeholders.',
      '### The Zero-Graphic-Design Workflow',
      'By bringing Enterprise RAG into your document stack, team members simply type or paste their notes. Enterprise RAG turns bullet points into polished, interactive visual graphics automatically.',
      '### Integration Across Tools',
      'Whether your team uses Notion, Google Docs, Microsoft Word, or Slack, Enterprise RAG embeds seamlessly to convert text into high-resolution PNG, SVG, or interactive embed blocks.',
      'Start using Enterprise RAG today to turn your enterprise knowledge bases into visual, easy-to-read assets!'
    ],
    tags: ['Enterprise RAG', 'Automation', 'Presentations', 'Team Collaboration']
  }
];

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Hero section states
  const [selectedPreset, setSelectedPreset] = useState(HERO_TEXT_PRESETS[0]);
  const [activeStyle, setActiveStyle] = useState<'flowchart' | 'venn' | 'mindmap'>('flowchart');
  const [activeColorTheme, setActiveColorTheme] = useState<'cyan' | 'green' | 'coral'>('cyan');

  // "How it works" section state
  const [activeStep, setActiveStep] = useState(1);

  // Blog section state
  const [selectedBlog, setSelectedBlog] = useState<BlogPost | null>(null);

  // Pricing toggle state
  const [isAnnual, setIsAnnual] = useState(true);

  // Navigate to login or dashboard
  const handlePrimaryAction = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-[#ffffff] dot-grid-pattern text-slate-900 font-sans selection:bg-cyan-200 selection:text-slate-900 overflow-x-hidden">

      {/* ─── NAVBAR ─── */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/80 transition-all w-full">
        <div className="w-full px-6 sm:px-8 lg:px-12 h-20 flex items-center justify-between">


          {/* Logo (Far Left) */}
          <div className="flex-1 flex justify-start">
            <div
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              className="flex items-center gap-2.5 cursor-pointer group"
            >
              <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary via-blue-600 to-indigo-600 shadow-md shadow-primary/25 group-hover:scale-105 transition-transform">
                <Brain className="h-5.5 w-5.5 text-white" />
                <Sparkles className="absolute -top-1 -right-1 h-3.5 w-3.5 text-sky-300 animate-pulse" />
              </div>

              <span className="text-2xl font-black tracking-tight text-slate-900">
                Enterprise RAG
              </span>
            </div>
          </div>

          {/* Nav Links (Centered) */}
          <nav className="hidden lg:flex items-center justify-center space-x-10 text-base font-semibold text-slate-600">
            <a
              href="#visuals"
              className="relative text-slate-900 py-1 font-bold border-b-2 border-slate-900 transition-colors"
            >
              Visuals
            </a>
            <a
              href="#visuals"
              className="flex items-center gap-1.5 hover:text-slate-900 transition-colors"
            >
              Slides
              <span className="text-[10px] uppercase tracking-wider font-extrabold bg-slate-900 text-white px-1.5 py-0.5 rounded">
                BETA
              </span>
            </a>
            <a href="#pricing" className="hover:text-slate-900 transition-colors">
              Pricing
            </a>
            <a href="#blog" className="hover:text-slate-900 transition-colors">
              Blog
            </a>
            <a href="#how-it-works" className="hover:text-slate-900 transition-colors">
              About us
            </a>
          </nav>

          {/* Right Action CTAs (Far Right) */}
          <div className="flex-1 flex justify-end items-center space-x-4">
            {isAuthenticated ? (
              <button
                onClick={() => navigate('/dashboard')}
                className="bg-[#262626] hover:bg-black text-white text-base font-bold px-6 py-2.5 rounded-xl transition-all shadow-md hover:shadow-lg flex items-center gap-2 active:scale-95 whitespace-nowrap"
              >
                <LayoutDashboard className="w-4 h-4" />
                Go to Dashboard
              </button>
            ) : (
              <>
                <button
                  onClick={() => navigate('/login')}
                  className="text-base font-semibold text-slate-700 hover:text-slate-900 transition-colors px-3 py-2 whitespace-nowrap"
                >
                  Sign in
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="bg-[#262626] hover:bg-black text-white text-base font-bold px-6 py-2.5 rounded-xl transition-all shadow-md hover:shadow-lg flex items-center gap-2 active:scale-95 whitespace-nowrap"
                >
                  Get Enterprise RAG Free
                </button>
              </>
            )}
          </div>
        </div>
      </header>



      {/* ─── HERO SECTION ─── */}
      <section id="visuals" className="relative pt-12 pb-24 dot-grid-pattern overflow-hidden">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center text-center">

          {/* Feature Badge */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-6 flex items-center gap-2"
          >
            <div className="w-10 h-10 rounded-full bg-cyan-400 text-white flex items-center justify-center shadow-lg shadow-cyan-400/30 animate-pulse">
              <Zap className="w-5 h-5 fill-current text-white" />
            </div>
          </motion.div>

          {/* Feature-Focused Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 max-w-4xl leading-[1.15]"
          >
            <span className="napkin-highlight border border-cyan-200 shadow-sm mr-3">
              Transform Documents
            </span>
            <br className="hidden sm:inline" />
            <span className="napkin-highlight border border-cyan-200 shadow-sm">
              into Intelligent Conversations
            </span>
          </motion.h1>


          {/* Feature-Focused Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-6 text-xl sm:text-2xl text-slate-600 max-w-3xl font-medium leading-relaxed"
          >
            Enterprise RAG combines hybrid vector search, context re-ranking, AI chat synthesis, and instant text-to-diagram generation into one powerful workspace.
          </motion.p>

          {/* Quick Feature Highlights Pills */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.25 }}
            className="mt-5 flex flex-wrap justify-center items-center gap-3 text-xs sm:text-sm font-bold text-slate-700"
          >
            <span className="bg-cyan-50 text-cyan-800 border border-cyan-200 px-3 py-1.5 rounded-full shadow-sm">
              Hybrid Vector + BM25 Search
            </span>
            <span className="bg-purple-50 text-purple-800 border border-purple-200 px-3 py-1.5 rounded-full shadow-sm">
              Neural Re-ranking Engine
            </span>
            <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1.5 rounded-full shadow-sm">
              Floating AI Chat Assistant
            </span>
            <span className="bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1.5 rounded-full shadow-sm">
              Instant Text-to-Diagrams
            </span>
          </motion.div>


          {/* Interactive Text Presets Selector */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 flex flex-wrap justify-center gap-2.5"
          >
            <span className="text-sm font-bold text-slate-400 self-center mr-2">Try Preset Text:</span>
            {HERO_TEXT_PRESETS.map((preset) => (
              <button
                key={preset.id}
                onClick={() => setSelectedPreset(preset)}
                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all border ${selectedPreset.id === preset.id
                    ? 'bg-slate-900 text-white border-slate-900 shadow-md'
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                  }`}
              >
                {preset.label}
              </button>
            ))}
          </motion.div>

          {/* ─── LIVE INTERACTIVE CANVAS DEMO ─── */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-10 w-full max-w-5xl bg-white border border-slate-200 rounded-3xl shadow-2xl p-6 md:p-8 relative grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch"
          >
            {/* Floating Style & Layout Toolbar Palette */}
            <div className="lg:col-span-3 flex flex-col justify-between bg-slate-50 border border-slate-200/80 rounded-2xl p-4 space-y-4">
              <div>
                <div className="flex items-center justify-between mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">
                  <span>Diagram Types</span>
                  <Sliders className="w-3.5 h-3.5 text-slate-400" />
                </div>

                <div className="space-y-2">
                  <button
                    onClick={() => setActiveStyle('flowchart')}
                    className={`w-full flex items-center gap-3 p-3 rounded-xl border text-left transition-all ${activeStyle === 'flowchart'
                        ? 'bg-cyan-50 border-cyan-300 text-slate-900 font-bold shadow-sm'
                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'
                      }`}
                  >
                    <GitCommit className="w-5 h-5 text-cyan-600" />
                    <div>
                      <div className="text-sm">Flowchart</div>
                      <div className="text-[11px] text-slate-400">Step-by-step logic</div>
                    </div>
                  </button>

                  <button
                    onClick={() => setActiveStyle('venn')}
                    className={`w-full flex items-center gap-3 p-3 rounded-xl border text-left transition-all ${activeStyle === 'venn'
                        ? 'bg-cyan-50 border-cyan-300 text-slate-900 font-bold shadow-sm'
                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'
                      }`}
                  >
                    <Layers className="w-5 h-5 text-cyan-600" />
                    <div>
                      <div className="text-sm">Venn & Overlap</div>
                      <div className="text-[11px] text-slate-400">Shared concepts</div>
                    </div>
                  </button>

                  <button
                    onClick={() => setActiveStyle('mindmap')}
                    className={`w-full flex items-center gap-3 p-3 rounded-xl border text-left transition-all ${activeStyle === 'mindmap'
                        ? 'bg-cyan-50 border-cyan-300 text-slate-900 font-bold shadow-sm'
                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'
                      }`}
                  >
                    <Grid className="w-5 h-5 text-cyan-600" />
                    <div>
                      <div className="text-sm">Mind Map</div>
                      <div className="text-[11px] text-slate-400">Central topic tree</div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Theme Color Switcher */}
              <div className="pt-3 border-t border-slate-200">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Theme Preset
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setActiveColorTheme('cyan')}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-bold border transition-all ${activeColorTheme === 'cyan' ? 'bg-cyan-500 text-white border-cyan-600' : 'bg-slate-200 text-slate-700'
                      }`}
                  >
                    Cyan
                  </button>
                  <button
                    onClick={() => setActiveColorTheme('green')}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-bold border transition-all ${activeColorTheme === 'green' ? 'bg-emerald-500 text-white border-emerald-600' : 'bg-slate-200 text-slate-700'
                      }`}
                  >
                    Mint
                  </button>
                  <button
                    onClick={() => setActiveColorTheme('coral')}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-bold border transition-all ${activeColorTheme === 'coral' ? 'bg-rose-500 text-white border-rose-600' : 'bg-slate-200 text-slate-700'
                      }`}
                  >
                    Coral
                  </button>
                </div>
              </div>
            </div>

            {/* Central Visual Diagram Display */}
            <div className="lg:col-span-9 flex flex-col items-center justify-center p-6 bg-slate-50/50 rounded-2xl border border-slate-200/60 relative overflow-hidden min-h-[380px]">

              {/* Cursor overlay animation */}
              <motion.div
                animate={{ x: [0, 40, 0], y: [0, 30, 0] }}
                transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
                className="absolute top-12 left-12 z-20 pointer-events-none flex items-center gap-1 bg-slate-900 text-white text-xs px-2 py-1 rounded shadow-lg opacity-80"
              >
                <MousePointer className="w-3.5 h-3.5 fill-current text-cyan-300" />
                <span>STYLE</span>
              </motion.div>

              {/* Dynamic SVG Diagram Content */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={`${selectedPreset.id}-${activeStyle}-${activeColorTheme}`}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.3 }}
                  className="w-full flex flex-col items-center justify-center space-y-6"
                >
                  {/* Flowchart Diagram Representation */}
                  {activeStyle === 'flowchart' && (
                    <div className="flex flex-col items-center space-y-6 w-full max-w-xl">
                      {/* Node 1: Start */}
                      <div className="flex items-center gap-2 px-5 py-2.5 rounded-full border-2 border-slate-300 bg-white shadow-sm text-sm font-bold text-slate-800">
                        <Sparkles className="w-4 h-4 text-amber-500" />
                        <span>Start</span>
                      </div>

                      {/* Arrow Down */}
                      <div className="w-0.5 h-6 bg-slate-300 relative">
                        <div className="absolute -bottom-1 -left-[3px] border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-slate-400" />
                      </div>

                      {/* Node 2: Diamond Decision Box */}
                      <div className="relative p-6 bg-white border-2 border-rose-400 text-rose-600 font-extrabold text-sm rounded-2xl shadow-sm rotate-45 flex items-center justify-center w-28 h-28">
                        <span className="-rotate-45 text-center leading-tight">
                          {selectedPreset.nodes[1]?.title || 'Have doc?'}
                        </span>
                      </div>

                      {/* Branch Paths (Yes / No) */}
                      <div className="grid grid-cols-2 gap-12 w-full pt-4 relative">
                        <div className="flex flex-col items-center space-y-3">
                          <span className="text-xs font-extrabold text-slate-400 uppercase tracking-widest">Yes</span>
                          <div className={`px-4 py-3 rounded-xl border-2 border-dashed font-bold text-sm bg-white shadow-sm w-full text-center ${activeColorTheme === 'cyan' ? 'border-cyan-400 text-cyan-800 bg-cyan-50/50' :
                              activeColorTheme === 'green' ? 'border-emerald-400 text-emerald-800 bg-emerald-50/50' : 'border-rose-400 text-rose-800 bg-rose-50/50'
                            }`}>
                            <FileText className="w-4 h-4 inline mr-1.5 opacity-70" />
                            {selectedPreset.nodes[2]?.title || 'Copy Paste'}
                          </div>
                        </div>

                        <div className="flex flex-col items-center space-y-3">
                          <span className="text-xs font-extrabold text-slate-400 uppercase tracking-widest">No</span>
                          <div className={`px-4 py-3 rounded-xl border-2 border-dashed font-bold text-sm bg-white shadow-sm w-full text-center ${activeColorTheme === 'cyan' ? 'border-cyan-400 text-cyan-800 bg-cyan-50/50' :
                              activeColorTheme === 'green' ? 'border-emerald-400 text-emerald-800 bg-emerald-50/50' : 'border-rose-400 text-rose-800 bg-rose-50/50'
                            }`}>
                            <FileCode className="w-4 h-4 inline mr-1.5 opacity-70" />
                            {selectedPreset.nodes[3]?.title || 'Type Idea'}
                          </div>
                        </div>
                      </div>

                      {/* Merging into Spark Node */}
                      <div className="flex items-center gap-3 w-full justify-center pt-2">
                        <div className="px-6 py-3 rounded-xl border-2 border-cyan-400 bg-cyan-400 text-white font-black text-sm shadow-md flex items-center gap-2">
                          <Zap className="w-4 h-4 fill-current text-white" />
                          <span>Spark Visuals</span>
                        </div>
                        <ChevronRight className="w-5 h-5 text-slate-400" />
                        <div className="px-5 py-2.5 rounded-full border border-slate-300 bg-white font-bold text-sm text-slate-700 shadow-sm flex items-center gap-2">
                          <Share2 className="w-4 h-4 text-slate-500" />
                          <span>Share</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Venn Diagram Representation */}
                  {activeStyle === 'venn' && (
                    <div className="relative w-80 h-64 flex items-center justify-center">
                      <div className="absolute left-4 w-44 h-44 rounded-full bg-cyan-400/30 border-2 border-cyan-500 flex items-center justify-start pl-4 font-bold text-cyan-900 text-sm">
                        Raw Text
                      </div>
                      <div className="absolute right-4 w-44 h-44 rounded-full bg-emerald-400/30 border-2 border-emerald-500 flex items-center justify-end pr-4 font-bold text-emerald-900 text-sm">
                        Visual Graphics
                      </div>
                      <div className="z-10 bg-white/90 backdrop-blur px-3 py-1.5 rounded-lg border border-slate-300 font-extrabold text-xs text-slate-800 shadow-md">
                        Enterprise RAG Magic
                      </div>
                    </div>
                  )}

                  {/* Mindmap Representation */}
                  {activeStyle === 'mindmap' && (
                    <div className="flex flex-col items-center space-y-4">
                      <div className="px-6 py-3 rounded-2xl bg-slate-900 text-white font-bold text-base shadow-lg">
                        {selectedPreset.label}
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="p-3 bg-white rounded-xl border border-slate-200 text-xs font-bold text-slate-700 shadow-sm">
                          📄 Structured Parsing
                        </div>
                        <div className="p-3 bg-white rounded-xl border border-slate-200 text-xs font-bold text-slate-700 shadow-sm">
                          ⚡ Auto Formatting
                        </div>
                        <div className="p-3 bg-white rounded-xl border border-slate-200 text-xs font-bold text-slate-700 shadow-sm">
                          🎨 Color Themes
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>

              {/* Bottom Canvas CTA Button */}
              <div className="mt-6 pt-4 border-t border-slate-200/80 w-full flex items-center justify-between text-xs font-semibold text-slate-500">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  Auto-updated layout from text
                </span>
                <button
                  onClick={handlePrimaryAction}
                  className="text-slate-900 font-extrabold hover:underline flex items-center gap-1"
                >
                  Edit in Enterprise RAG Free
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

          </motion.div>
        </div>
      </section>


      {/* ─── HOW IT WORKS SECTION ─── */}
      <section id="how-it-works" className="py-20 bg-[#f2f8f3]/90 dot-grid-pattern relative overflow-hidden">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">

          {/* Section Header */}
          <div className="text-center mb-14">
            <h2 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight relative inline-block">
              <span className="relative z-10">How</span>
              <svg className="absolute -bottom-2 left-0 w-full h-3 text-slate-800" viewBox="0 0 100 20" preserveAspectRatio="none">
                <path d="M0 15 Q 50 0 100 15" stroke="currentColor" strokeWidth="4" fill="none" strokeLinecap="round" />
              </svg>
              {' '}it works
            </h2>
          </div>

          {/* Interactive Steps Card Container */}
          <div className="bg-white/80 backdrop-blur-md rounded-3xl border border-emerald-100 shadow-xl p-8 lg:p-12 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">

            {/* Left Side: Step Indicator & Description */}
            <div className="lg:col-span-6 space-y-6">

              {/* Step Pills Navigation */}
              <div className="flex items-center gap-2 mb-6">
                {[1, 2, 3, 4].map((stepNum) => (
                  <button
                    key={stepNum}
                    onClick={() => setActiveStep(stepNum)}
                    className={`w-3 h-3 rounded-full transition-all ${activeStep === stepNum
                        ? 'bg-emerald-500 w-8'
                        : 'bg-slate-300 hover:bg-slate-400'
                      }`}
                  />
                ))}
              </div>

              {/* Step Content */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeStep}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-9 h-9 rounded-full bg-slate-900 text-white font-extrabold flex items-center justify-center text-lg">
                      {activeStep}
                    </span>
                    <h3 className="text-3xl font-extrabold text-slate-900 leading-tight">
                      {activeStep === 1 && (
                        <>
                          Start by{' '}
                          <span className="napkin-green-highlight">Importing</span> or{' '}
                          <span className="napkin-green-highlight">Pasting</span> your text
                        </>
                      )}
                      {activeStep === 2 && (
                        <>
                          Choose from{' '}
                          <span className="napkin-green-highlight">Auto-Generated</span> visual layouts
                        </>
                      )}
                      {activeStep === 3 && (
                        <>
                          Customize{' '}
                          <span className="napkin-green-highlight">Colors & Icons</span> with 1-click
                        </>
                      )}
                      {activeStep === 4 && (
                        <>
                          <span className="napkin-green-highlight">Export & Share</span> PNG, SVG or Presentations
                        </>
                      )}
                    </h3>
                  </div>

                  <p className="text-lg text-slate-600 font-medium">
                    {activeStep === 1 && 'Forget prompting, Enterprise RAG works directly from your text notes, specs, or documents.'}
                    {activeStep === 2 && 'Enterprise RAG parses paragraphs into flowcharts, Venn diagrams, sequence maps, and mindmaps automatically.'}
                    {activeStep === 3 && 'Tailor your visual aesthetics with enterprise themes, custom font families, and high-res vector icons.'}
                    {activeStep === 4 && 'Copy high-resolution vector assets directly into Notion, Google Slides, Figma, or download as SVG.'}
                  </p>

                  <div className="pt-4">
                    <button
                      onClick={handlePrimaryAction}
                      className="bg-slate-900 hover:bg-black text-white px-6 py-3 rounded-xl font-bold transition-all shadow-md flex items-center gap-2"
                    >
                      Try Step {activeStep} in Enterprise RAG Free
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Right Side: Graphic showing documents flowing into Enterprise RAG */}
            <div className="lg:col-span-6 flex justify-center">
              <div className="relative w-full max-w-md bg-white border border-slate-200 rounded-3xl p-8 shadow-xl flex items-center justify-center">

                {/* Apps Diagram Circle */}
                <div className="relative w-full h-80 flex items-center justify-center">

                  {/* Central Notebook Paper Box */}
                  <div className="z-10 bg-white border-2 border-slate-200 rounded-2xl shadow-xl p-6 w-60 text-center space-y-3">
                    <div className="flex justify-center items-center gap-2 bg-slate-100 py-1.5 px-3 rounded-lg border border-slate-200 text-xs font-mono font-bold text-slate-700">
                      <span>⌘</span> + <span>V</span>
                    </div>
                    <div className="text-xs font-bold text-slate-500">
                      Paste text in Enterprise RAG
                    </div>
                    <div className="space-y-1.5 pt-2 border-t border-slate-100">
                      <div className="h-2 bg-slate-200 rounded-full w-full" />
                      <div className="h-2 bg-slate-200 rounded-full w-4/5" />
                      <div className="h-2 bg-cyan-200 rounded-full w-3/5" />
                    </div>
                  </div>

                  {/* App Icons Floating around with arrows */}
                  <div className="absolute top-2 left-6 bg-white p-3 rounded-xl border border-slate-200 shadow-md flex items-center gap-2 text-xs font-bold">
                    <span className="text-emerald-600 font-extrabold text-sm">N</span> Notion
                  </div>
                  <div className="absolute top-2 right-6 bg-white p-3 rounded-xl border border-slate-200 shadow-md flex items-center gap-2 text-xs font-bold">
                    <span className="text-blue-600 font-extrabold text-sm">G</span> Docs
                  </div>
                  <div className="absolute bottom-2 left-6 bg-white p-3 rounded-xl border border-slate-200 shadow-md flex items-center gap-2 text-xs font-bold">
                    <span className="text-blue-700 font-extrabold text-sm">W</span> Word
                  </div>
                  <div className="absolute bottom-2 right-6 bg-white p-3 rounded-xl border border-slate-200 shadow-md flex items-center gap-2 text-xs font-bold">
                    <span className="text-orange-600 font-extrabold text-sm">P</span> PowerPoint
                  </div>

                </div>
              </div>
            </div>

          </div>
        </div>
      </section>


      {/* ─── BLOG SECTION ─── */}
      <section id="blog" className="py-24 bg-white/70 dot-grid-pattern border-t border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

          {/* Section Header */}
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 space-y-4 md:space-y-0">
            <div>
              <span className="text-xs uppercase font-extrabold tracking-widest text-cyan-600 bg-cyan-50 px-3 py-1 rounded-full border border-cyan-200">
                Latest Insights
              </span>
              <h2 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight mt-3">
                Enterprise RAG Blog & Stories
              </h2>
              <p className="text-lg text-slate-600 font-medium mt-2 max-w-xl">
                Explore how visual RAG, automated diagramming, and text-to-graphics transform enterprise communication.
              </p>
            </div>

            <button
              onClick={handlePrimaryAction}
              className="text-slate-900 font-extrabold hover:underline flex items-center gap-2 text-base"
            >
              View all articles
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Blog Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {BLOG_POSTS.map((post) => (
              <motion.article
                key={post.id}
                whileHover={{ y: -6 }}
                transition={{ duration: 0.2 }}
                onClick={() => setSelectedBlog(post)}
                className="bg-white/90 backdrop-blur-sm border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-xl transition-all cursor-pointer flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-bold text-slate-400 mb-3">
                    <span className="text-cyan-700 bg-cyan-50 px-2.5 py-1 rounded-md border border-cyan-200">
                      {post.category}
                    </span>
                    <span>{post.readTime}</span>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 group-hover:text-cyan-600 transition-colors leading-snug mb-3">
                    {post.title}
                  </h3>

                  <p className="text-slate-600 text-sm line-clamp-3 leading-relaxed mb-6 font-medium">
                    {post.excerpt}
                  </p>
                </div>

                {/* Author footer */}
                <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <img
                      src={post.author.avatar}
                      alt={post.author.name}
                      className="w-8 h-8 rounded-full object-cover border border-slate-200"
                    />
                    <div>
                      <div className="text-xs font-bold text-slate-800">{post.author.name}</div>
                      <div className="text-[10px] text-slate-400 font-medium">{post.date}</div>
                    </div>
                  </div>

                  <span className="text-slate-400 group-hover:text-slate-900 transition-colors">
                    <ArrowUpRight className="w-4 h-4" />
                  </span>
                </div>
              </motion.article>
            ))}
          </div>

        </div>
      </section>


      {/* ─── BLOG ARTICLE MODAL READER ─── */}
      <AnimatePresence>
        {selectedBlog && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-8 relative"
            >
              {/* Close Button */}
              <button
                onClick={() => setSelectedBlog(null)}
                className="absolute top-6 right-6 p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Modal Header */}
              <div className="mb-6 space-y-3">
                <span className="text-xs font-bold uppercase tracking-wider text-cyan-700 bg-cyan-50 px-3 py-1 rounded-full border border-cyan-200">
                  {selectedBlog.category}
                </span>
                <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 leading-tight">
                  {selectedBlog.title}
                </h2>
                <div className="flex items-center gap-4 text-sm font-semibold text-slate-500 pt-2 border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2">
                    <img src={selectedBlog.author.avatar} alt={selectedBlog.author.name} className="w-7 h-7 rounded-full" />
                    <span>{selectedBlog.author.name} ({selectedBlog.author.role})</span>
                  </div>
                  <span>•</span>
                  <span>{selectedBlog.date}</span>
                  <span>•</span>
                  <span>{selectedBlog.readTime}</span>
                </div>
              </div>

              {/* Article Content */}
              <div className="prose prose-slate max-w-none text-slate-700 space-y-4 font-medium leading-relaxed">
                {selectedBlog.content.map((paragraph, index) => (
                  <p key={index} className="text-base leading-relaxed">
                    {paragraph}
                  </p>
                ))}
              </div>

              {/* Tags */}
              <div className="mt-8 pt-6 border-t border-slate-100 flex flex-wrap gap-2">
                {selectedBlog.tags.map((tag) => (
                  <span key={tag} className="text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-lg">
                    #{tag}
                  </span>
                ))}
              </div>

              {/* CTA Inside Modal */}
              <div className="mt-8 p-6 bg-slate-900 text-white rounded-2xl flex items-center justify-between">
                <div>
                  <h4 className="text-lg font-bold">Try turning your text into visuals now</h4>
                  <p className="text-xs text-slate-300 font-medium">Free plan includes unlimited visual exports.</p>
                </div>
                <button
                  onClick={handlePrimaryAction}
                  className="bg-white text-slate-900 px-5 py-2.5 rounded-xl font-extrabold text-sm hover:bg-slate-100 transition-all shadow-md"
                >
                  Get Enterprise RAG Free
                </button>
              </div>

            </motion.div>
          </div>
        )}
      </AnimatePresence>


      {/* ─── PRICING SECTION ─── */}
      <section id="pricing" className="py-24 bg-slate-50/70 dot-grid-pattern border-t border-slate-200/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">

          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
              Simple, transparent pricing
            </h2>
            <p className="text-lg text-slate-600 font-medium mt-3">
              Start free today. Upgrade as your team grows.
            </p>

            {/* Monthly / Annual Toggle */}
            <div className="mt-8 flex items-center justify-center gap-4">
              <span className={`text-sm font-bold ${!isAnnual ? 'text-slate-900' : 'text-slate-500'}`}>Monthly</span>
              <button
                onClick={() => setIsAnnual(!isAnnual)}
                className="w-14 h-8 bg-slate-900 rounded-full p-1 transition-colors relative"
              >
                <div className={`w-6 h-6 bg-white rounded-full transition-transform shadow-md ${isAnnual ? 'translate-x-6' : 'translate-x-0'}`} />
              </button>
              <span className={`text-sm font-bold ${isAnnual ? 'text-slate-900' : 'text-slate-500'}`}>
                Annual <span className="text-xs bg-emerald-100 text-emerald-800 font-extrabold px-2 py-0.5 rounded-full ml-1">Save 20%</span>
              </span>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">

            {/* Free Tier */}
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl border border-slate-200 p-8 shadow-sm flex flex-col justify-between">
              <div>
                <h3 className="text-2xl font-bold text-slate-900">Starter Free</h3>
                <p className="text-sm text-slate-500 font-medium mt-1">For individuals trying out text-to-visuals.</p>
                <div className="my-6">
                  <span className="text-4xl font-extrabold text-slate-900">$0</span>
                  <span className="text-slate-500 font-medium text-sm"> / forever</span>
                </div>
                <ul className="space-y-3 text-sm font-medium text-slate-600 mb-8">
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> Unlimited text-to-visual generations</li>
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> Standard diagram styles & flowcharts</li>
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> PNG & SVG image exports</li>
                </ul>
              </div>
              <button
                onClick={handlePrimaryAction}
                className="w-full bg-slate-900 hover:bg-black text-white font-extrabold py-3.5 rounded-xl transition-all shadow-md"
              >
                Get Enterprise RAG Free
              </button>
            </div>

            {/* Pro Tier */}
            <div className="bg-white/95 backdrop-blur-sm rounded-3xl border-2 border-cyan-400 p-8 shadow-xl relative flex flex-col justify-between">
              <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-cyan-400 text-white font-extrabold text-xs px-4 py-1 rounded-full uppercase tracking-wider shadow">
                Most Popular
              </span>
              <div>
                <h3 className="text-2xl font-bold text-slate-900">Pro Creator</h3>
                <p className="text-sm text-slate-500 font-medium mt-1">For creators & professionals presenting daily.</p>
                <div className="my-6">
                  <span className="text-4xl font-extrabold text-slate-900">{isAnnual ? '$12' : '$15'}</span>
                  <span className="text-slate-500 font-medium text-sm"> / month</span>
                </div>
                <ul className="space-y-3 text-sm font-medium text-slate-600 mb-8">
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> Everything in Starter</li>
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> Premium color themes & custom fonts</li>
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> High-res vector SVG & PDF export</li>
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> 1-Click Notion & Google Slides sync</li>
                </ul>
              </div>
              <button
                onClick={handlePrimaryAction}
                className="w-full bg-cyan-500 hover:bg-cyan-600 text-white font-extrabold py-3.5 rounded-xl transition-all shadow-md"
              >
                Start Pro Free Trial
              </button>
            </div>

            {/* Enterprise Tier */}
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl border border-slate-200 p-8 shadow-sm flex flex-col justify-between">
              <div>
                <h3 className="text-2xl font-bold text-slate-900">Enterprise</h3>
                <p className="text-sm text-slate-500 font-medium mt-1">For teams building visual RAG & specs.</p>
                <div className="my-6">
                  <span className="text-4xl font-extrabold text-slate-900">$29</span>
                  <span className="text-slate-500 font-medium text-sm"> / user / mo</span>
                </div>
                <ul className="space-y-3 text-sm font-medium text-slate-600 mb-8">
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> Everything in Pro</li>
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> Custom enterprise brand tokens</li>
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> Collaborative workspace & SSO</li>
                  <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" /> Dedicated account manager</li>
                </ul>
              </div>
              <button
                onClick={handlePrimaryAction}
                className="w-full bg-slate-100 hover:bg-slate-200 text-slate-900 font-extrabold py-3.5 rounded-xl transition-all"
              >
                Contact Sales
              </button>
            </div>

          </div>
        </div>
      </section>


      {/* ─── TRY ENTERPRISE RAG CTA SECTION ─── */}
      <section className="py-24 bg-white/70 dot-grid-pattern relative overflow-hidden text-center border-t border-slate-100">

        {/* Background Geometric Faint Diagrams */}
        <div className="absolute inset-0 pointer-events-none opacity-5 flex items-center justify-between px-10">
          <div className="w-64 h-64 border-4 border-slate-900 rounded-full" />
          <div className="w-64 h-64 border-4 border-slate-900 rotate-45" />
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

          {/* Swirly Arrow Doodle */}
          <div className="flex justify-center mb-6">
            <svg className="w-16 h-16 text-slate-800 animate-bounce" viewBox="0 0 100 100" fill="none">
              <path d="M30 10 Q 70 30 40 60 T 50 85" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
              <path d="M40 80 L 50 90 L 60 80" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>

          <h2 className="text-5xl sm:text-6xl font-black text-slate-900 tracking-tight">
            Try Enterprise RAG!
          </h2>

          <p className="mt-4 text-xl text-slate-600 font-medium max-w-xl mx-auto">
            Get started instantly, no download required.
          </p>

          <div className="mt-8">
            <button
              onClick={handlePrimaryAction}
              className="bg-[#383838] hover:bg-black text-white text-xl font-bold px-10 py-4 rounded-2xl transition-all shadow-xl hover:shadow-2xl active:scale-95 inline-flex items-center gap-3"
            >
              Get Enterprise RAG Free
            </button>
          </div>

        </div>
      </section>


      {/* ─── FOOTER ─── */}
      <footer className="bg-[#2b2b2b] text-slate-300 py-16 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-10 items-start">

            {/* Logo Column */}
            <div className="md:col-span-2 space-y-4">
              <div className="flex items-center gap-2.5 text-white">
                <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary via-blue-600 to-indigo-600 shadow-md">
                  <Brain className="h-5 w-5 text-white" />
                  <Sparkles className="absolute -top-1 -right-1 h-3.5 w-3.5 text-sky-300 animate-pulse" />
                </div>
                <span className="text-2xl font-black tracking-tight">Enterprise RAG</span>
              </div>

              <p className="text-xs text-slate-400 font-medium">
                © 2026 Enterprise RAG. All rights reserved.
              </p>
            </div>

            {/* Product Column */}
            <div>
              <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Product</h4>
              <ul className="space-y-2.5 text-xs font-semibold text-slate-400">
                <li><a href="#how-it-works" className="hover:text-white transition-colors">How it works</a></li>
                <li><a href="#visuals" className="hover:text-white transition-colors">Use Cases</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#blog" className="hover:text-white transition-colors">Help Center</a></li>
              </ul>
            </div>

            {/* Company Column */}
            <div>
              <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Company</h4>
              <ul className="space-y-2.5 text-xs font-semibold text-slate-400">
                <li><a href="#how-it-works" className="hover:text-white transition-colors">About us</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#blog" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">Contact Us</a></li>
              </ul>
            </div>

            {/* Privacy Column */}
            <div>
              <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Privacy</h4>
              <ul className="space-y-2.5 text-xs font-semibold text-slate-400">
                <li><a href="#how-it-works" className="hover:text-white transition-colors">Terms and Conditions</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">Privacy Policy</a></li>
              </ul>
            </div>

          </div>

          {/* Social Icons & Language Dropdown */}
          <div className="mt-12 pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-4 text-slate-400">
              <a href="#" className="hover:text-white text-xs font-bold">LinkedIn</a>
              <a href="#" className="hover:text-white text-xs font-bold">X / Twitter</a>
              <a href="#" className="hover:text-white text-xs font-bold">YouTube</a>
              <a href="#" className="hover:text-white text-xs font-bold">Instagram</a>
              <a href="#" className="hover:text-white text-xs font-bold">TikTok</a>
            </div>

            <div className="flex items-center gap-2 bg-slate-800 text-slate-300 text-xs px-3 py-1.5 rounded-lg font-semibold border border-slate-700">
              <Globe className="w-3.5 h-3.5" />
              <span>English</span>
            </div>
          </div>
        </div>
      </footer>

    </div>
  );
}
