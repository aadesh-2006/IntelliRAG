import React from 'react'
import { Layout, Database, KeyRound, FolderGit2, Check } from 'lucide-react'

export const ArchitectureOverview: React.FC = () => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-white tracking-tight">System Architecture & Roadmap</h3>
        <p className="text-sm text-slate-400 mt-1">
          Current implementation status across the planned platform phases.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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
      </div>
    </div>
  )
}