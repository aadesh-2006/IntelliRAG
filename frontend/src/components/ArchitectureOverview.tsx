import React from 'react'
import { Layout, Database, KeyRound, FolderGit2, ScanText, Layers, GitFork, Check, Trophy, Clock, BarChart3 } from 'lucide-react'

export const ArchitectureOverview: React.FC = () => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-white tracking-tight">System Architecture & Roadmap</h3>
        <p className="text-sm text-slate-400 mt-1">
          Current implementation status across the planned platform phases.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Layout className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 1 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Frontend Foundation</h4>
          <p className="text-xs text-slate-400 mt-1">React, TypeScript, Vite, Tailwind CSS, API client layer.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Database className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 2 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Persistence & pgvector</h4>
          <p className="text-xs text-slate-400 mt-1">PostgreSQL, SQLAlchemy 2.x, Alembic, pgvector, Users/Docs/Chunks models.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <KeyRound className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 3 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Authentication & Security</h4>
          <p className="text-xs text-slate-400 mt-1">JWT access tokens, bcrypt password hashing, /register, /login, /me endpoints.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <FolderGit2 className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 4 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Document Management</h4>
          <p className="text-xs text-slate-400 mt-1">Streaming storage, user-scoped document vault, metadata tracking, and downloads.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <ScanText className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 5 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Multimodal Document AI</h4>
          <p className="text-xs text-slate-400 mt-1">PDF layout parsing, table extraction, OCR image vision, and normalized AST blocks.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Layers className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 6 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Chunking & Embeddings</h4>
          <p className="text-xs text-slate-400 mt-1">Structure-aware chunking, 768-dim CPU vector embeddings, and pgvector persistence.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <GitFork className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 7 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Intelligent Query Router</h4>
          <p className="text-xs text-slate-400 mt-1">Intent routing across SQL (structured parameterized data), RAG (grounded semantic retrieval), and HYBRID execution paths.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <BarChart3 className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 8 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">AI Analytics Engine</h4>
          <p className="text-xs text-slate-400 mt-1">Natural-language analytics understanding, safe parameterized aggregations, date intelligence, and LLM explanation.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Check className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 9 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Workspace Dashboard</h4>
          <p className="text-xs text-slate-400 mt-1">Operational KPIs, ingestion &amp; chunk metrics, type distributions, lifecycle monitors, and quick workflows.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Check className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 10 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Conversational Chat Interface</h4>
          <p className="text-xs text-slate-400 mt-1">Persistent multi-turn conversation sessions, bounded chat context, inline/card citation sources, and retrieval grounding signals.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Check className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 11 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Reminder Engine</h4>
          <p className="text-xs text-slate-400 mt-1">Context-aware date extraction, warranty/expiry tracking, renewal alerts, lead-time scheduling, and document date scanning.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Check className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 12 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Notification System</h4>
          <p className="text-xs text-slate-400 mt-1">Multi-channel alert delivery (In-App, Email, Webhooks), idempotent event dispatching, retry worker, and user preference management.</p>
        </div>

        <div className="border border-indigo-500/40 bg-indigo-950/20 rounded-xl p-4 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Trophy className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-3 h-3" />
              <span>Module 13 Completed</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">Cricket Scorecard AI</h4>
          <p className="text-xs text-slate-400 mt-1">Scorecard detection, innings &amp; performance extraction, validation rules, statistics aggregation, and match summaries.</p>
        </div>

        <div className="border border-slate-800 bg-slate-950/40 rounded-xl p-4 relative overflow-hidden opacity-75">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 rounded-lg bg-slate-800 text-slate-400">
              <Clock className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
              <Clock className="w-3 h-3" />
              <span>Module 14 Planned</span>
            </span>
          </div>
          <h4 className="text-sm font-bold text-slate-100">End-to-End Integration</h4>
          <p className="text-xs text-slate-400 mt-1">Unified orchestration connecting ingestion, storage, search, synthesis, and full UI workflows.</p>
        </div>
      </div>
    </div>
  )
}
