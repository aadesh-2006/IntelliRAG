import React, { useState } from 'react'
import { Lock, Mail, AlertCircle, ArrowRight, ShieldCheck, KeyRound } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export const AuthCard: React.FC = () => {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { login, register } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      if (mode === 'login') {
        await login(email, password)
      } else {
        await register(email, password)
      }
      setEmail('')
      setPassword('')
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Authentication request failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md mx-auto bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl p-6 sm:p-8 backdrop-blur">
      <div className="flex items-center space-x-2 text-indigo-400 mb-2">
        <ShieldCheck className="w-5 h-5" />
        <span className="text-xs font-semibold uppercase tracking-wider">
          Authentication Gate
        </span>
      </div>

      <h2 className="text-2xl font-bold text-white tracking-tight">
        {mode === 'login' ? 'Sign in to IntelliRAG' : 'Create Workspace Account'}
      </h2>
      <p className="text-xs text-slate-400 mt-1 mb-6">
        {mode === 'login'
          ? 'Enter your credentials to unlock the protected application shell.'
          : 'Register your secure identity for document intelligence access.'}
      </p>

      <div className="flex bg-slate-950 p-1 rounded-lg mb-6 border border-slate-800">
        <button
          type="button"
          onClick={() => {
            setMode('login')
            setError(null)
          }}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all ${
            mode === 'login'
              ? 'bg-indigo-600 text-white shadow'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Sign In
        </button>
        <button
          type="button"
          onClick={() => {
            setMode('register')
            setError(null)
          }}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all ${
            mode === 'register'
              ? 'bg-indigo-600 text-white shadow'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Register
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-rose-950/40 border border-rose-800/60 rounded-lg flex items-start space-x-2.5 text-rose-200 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Email Address
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="analyst@intellirag.ai"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3.5 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3.5 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            />
          </div>
          {mode === 'register' && (
            <p className="text-[11px] text-slate-500 mt-1">Minimum 8 characters.</p>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 inline-flex items-center justify-center space-x-2 py-2.5 px-4 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white text-sm font-semibold rounded-lg shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-50"
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <KeyRound className="w-4 h-4" />
              <span>{mode === 'login' ? 'Authenticate' : 'Complete Registration'}</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  )
}