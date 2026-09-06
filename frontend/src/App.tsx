import React, { useState, useEffect, useCallback } from 'react'
import { Header } from './components/Header'
import { HeroSection } from './components/HeroSection'
import { StatusBadge } from './components/StatusBadge'
import { ArchitectureOverview } from './components/ArchitectureOverview'
import { Footer } from './components/Footer'
import { AuthCard } from './components/AuthCard'
import { DocumentUploadCard } from './components/DocumentUploadCard'
import { DocumentList } from './components/DocumentList'
import { SemanticSearchCard } from './components/SemanticSearchCard'
import { RAGQueryCard } from './components/RAGQueryCard'
import { DashboardOverview } from './components/DashboardOverview'
import { ChatInterface } from './components/ChatInterface'
import { AuthProvider, useAuth } from './context/AuthContext'
import { checkBackendHealth, HealthStatus } from './api/health'
import { ShieldCheck, UserCheck, Lock, LayoutDashboard, Files, MessageSquare, Bot, Search, Layers } from 'lucide-react'

type TabType = 'dashboard' | 'documents' | 'chat' | 'rag' | 'search' | 'roadmap'

export const AppContent: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [status, setStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0)

  const verifyHealth = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await checkBackendHealth()
      setStatus(data)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to connect to backend server')
      }
      setStatus(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (isAuthenticated) {
      verifyHealth()
    }
  }, [isAuthenticated, verifyHealth])

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-slate-100">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-10 h-10 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-slate-400 font-medium">Verifying authentication session...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <HeroSection />

        {!isAuthenticated ? (
          <div className="space-y-8">
            <div className="max-w-md mx-auto text-center">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300 mb-3">
                <Lock className="w-3.5 h-3.5 text-rose-400" />
                <span>Protected Application Boundary</span>
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Authentication Required
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Please sign in or create an account to access the IntelliRAG protected application shell.
              </p>
            </div>
            <AuthCard />
          </div>
        ) : (
          <div className="space-y-8 animate-fade-in">
            <div className="bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-slate-950 border border-indigo-900/40 rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center space-x-3.5">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
                  <UserCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold text-white">Authenticated Workspace</span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Active
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    User: <span className="text-slate-200 font-mono">{user?.email}</span>
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2 text-xs text-indigo-300 bg-indigo-950/60 border border-indigo-800/40 px-3.5 py-1.5 rounded-lg">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                <span>JWT Security Boundary Active</span>
              </div>
            </div>

            <div className="flex items-center overflow-x-auto border-b border-slate-800 pb-2 gap-2 scrollbar-none">
              <button
                type="button"
                onClick={() => setActiveTab('dashboard')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                  activeTab === 'dashboard'
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/20'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('documents')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                  activeTab === 'documents'
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/20'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
                }`}
              >
                <Files className="w-4 h-4" />
                <span>Document Vault</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('chat')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                  activeTab === 'chat'
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/20'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span>Assistant Chat</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('rag')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                  activeTab === 'rag'
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/20'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
                }`}
              >
                <Bot className="w-4 h-4" />
                <span>RAG Query</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('search')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                  activeTab === 'search'
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/20'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
                }`}
              >
                <Search className="w-4 h-4" />
                <span>Semantic Search</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('roadmap')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
                  activeTab === 'roadmap'
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/20'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>Architecture Roadmap</span>
              </button>
            </div>

            {activeTab === 'dashboard' && (
              <DashboardOverview
                onNavigateTab={(tab) => setActiveTab(tab)}
                refreshTrigger={refreshTrigger}
              />
            )}

            {activeTab === 'documents' && (
              <div className="space-y-8 animate-fade-in">
                <DocumentUploadCard onUploadSuccess={handleUploadSuccess} />
                <DocumentList refreshTrigger={refreshTrigger} />
              </div>
            )}

            {activeTab === 'chat' && (
              <div className="animate-fade-in">
                <ChatInterface refreshTrigger={refreshTrigger} />
              </div>
            )}

            {activeTab === 'rag' && (
              <div className="animate-fade-in">
                <RAGQueryCard refreshTrigger={refreshTrigger} />
              </div>
            )}

            {activeTab === 'search' && (
              <div className="animate-fade-in">
                <SemanticSearchCard refreshTrigger={refreshTrigger} />
              </div>
            )}

            {activeTab === 'roadmap' && (
              <div className="space-y-8 animate-fade-in">
                <div className="max-w-2xl mx-auto">
                  <StatusBadge
                    status={status}
                    loading={loading}
                    error={error}
                    onRefresh={verifyHealth}
                  />
                </div>
                <ArchitectureOverview />
              </div>
            )}
          </div>
        )}
      </main>
      <Footer />
    </div>
  )
}

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App