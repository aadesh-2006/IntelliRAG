import React, { useState, useEffect } from 'react'
import { Layers, Terminal, Sparkles, User as UserIcon, LogOut, LogIn, Bell } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { AuthModal } from './AuthModal'
import { NotificationPanel } from './NotificationPanel'
import { getUnreadCount } from '../api/notifications'

export const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [notificationPanelOpen, setNotificationPanelOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    if (isAuthenticated) {
      fetchUnread()
      const interval = setInterval(fetchUnread, 30000)
      return () => clearInterval(interval)
    } else {
      setUnreadCount(0)
    }
  }, [isAuthenticated])

  const fetchUnread = async () => {
    try {
      const res = await getUnreadCount()
      setUnreadCount(res.unread_count)
    } catch {}
  }

  const openAuth = (mode: 'login' | 'register') => {
    setAuthMode(mode)
    setAuthModalOpen(true)
  }

  return (
    <>
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-white tracking-tight">IntelliRAG</span>
                <span className="px-2 py-0.5 text-[10px] uppercase font-semibold tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full">
                  Module 12
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Multimodal AI Document Intelligence Platform</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 sm:space-x-4">
            <a
              href="http://localhost:8000/api/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center space-x-1.5 text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors"
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>FastAPI Docs</span>
            </a>
            <div className="hidden sm:block h-4 w-px bg-slate-800" />
            <div className="hidden sm:flex items-center space-x-1.5 text-xs text-slate-400">
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              <span>Multi-Channel Notifications</span>
            </div>

            {isAuthenticated && user ? (
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <button
                    onClick={() => setNotificationPanelOpen(!notificationPanelOpen)}
                    title="Notifications"
                    className="relative p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
                  >
                    <Bell className="w-4 h-4" />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 flex h-4 min-w-[16px] px-1 items-center justify-center rounded-full bg-indigo-600 text-[9px] font-bold text-white shadow-lg ring-2 ring-slate-950">
                        {unreadCount > 99 ? '99+' : unreadCount}
                      </span>
                    )}
                  </button>

                  <NotificationPanel
                    isOpen={notificationPanelOpen}
                    onClose={() => setNotificationPanelOpen(false)}
                    onUnreadCountChange={(count) => setUnreadCount(count)}
                  />
                </div>

                <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5">
                  <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                    <UserIcon className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs font-medium text-slate-200 max-w-[140px] truncate">
                    {user.email}
                  </span>
                  <button
                    onClick={logout}
                    title="Sign out"
                    className="text-slate-400 hover:text-rose-400 p-1 rounded transition-colors ml-1"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => openAuth('login')}
                  className="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors"
                >
                  <LogIn className="w-3.5 h-3.5" />
                  <span>Sign In</span>
                </button>
                <button
                  onClick={() => openAuth('register')}
                  className="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg shadow-sm transition-colors"
                >
                  <span>Register</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        defaultMode={authMode}
      />
    </>
  )
}