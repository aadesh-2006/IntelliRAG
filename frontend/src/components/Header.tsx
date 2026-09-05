import React from 'react'
import { Layers, Terminal, Sparkles } from 'lucide-react'

export const Header: React.FC = () => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">IntelliRAG</span>
              <span className="px-2 py-0.5 text-[10px] uppercase font-semibold tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full">
                Module 2
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Multimodal AI Document Intelligence Platform</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <a
            href="http://localhost:8000/api/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1.5 text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>FastAPI Docs</span>
          </a>
          <div className="h-4 w-px bg-slate-800" />
          <div className="flex items-center space-x-1.5 text-xs text-slate-400">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Persistence Ready</span>
          </div>
        </div>
      </div>
    </header>
  )
}