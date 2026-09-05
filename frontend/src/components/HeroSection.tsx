import React from 'react'
import { Bot, FileSearch, ShieldCheck, Database } from 'lucide-react'

export const HeroSection: React.FC = () => {
  return (
    <div className="py-12 sm:py-16 text-center relative overflow-hidden">
      <div className="absolute inset-0 bg-radial from-indigo-500/10 via-transparent to-transparent pointer-events-none" />
      <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-indigo-300 mb-6">
        <Database className="w-3.5 h-3.5 text-indigo-400" />
        <span>Module 2: PostgreSQL, SQLAlchemy & pgvector Layer Established</span>
      </div>
      <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight">
        Multimodal AI Document Intelligence Platform
      </h1>
      <p className="mt-5 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
        IntelliRAG provides deep multimodal understanding, semantic retrieval, and structured information extraction across diverse document streams.
      </p>

      <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto text-left">
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-3">
            <FileSearch className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-semibold text-slate-200">Multimodal Intake</h4>
          <p className="text-xs text-slate-400 mt-1">
            Engineered for high-throughput PDF, OCR, and rich visual document processing pipelines.
          </p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 mb-3">
            <Bot className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-semibold text-slate-200">Precision RAG</h4>
          <p className="text-xs text-slate-400 mt-1">
            Hybrid dense-sparse vector search, pgvector indexing, and multimodal context augmentation.
          </p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-3">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-semibold text-slate-200">Enterprise Ready</h4>
          <p className="text-xs text-slate-400 mt-1">
            Modular architecture designed for strict schemas, observability, and reproducible evaluation.
          </p>
        </div>
      </div>
    </div>
  )
}