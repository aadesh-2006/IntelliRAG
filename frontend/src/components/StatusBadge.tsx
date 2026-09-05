import React from 'react'
import { Activity, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'
import { HealthStatus } from '../api/health'

interface StatusBadgeProps {
  status: HealthStatus | null
  loading: boolean
  error: string | null
  onRefresh: () => void
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  loading,
  error,
  onRefresh,
}) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/40">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold text-slate-200 text-sm tracking-wide uppercase">
            Backend API Health Status
          </h3>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Checking...' : 'Recheck'}</span>
        </button>
      </div>

      {loading && !status && !error && (
        <div className="flex items-center space-x-3 py-2 text-slate-400">
          <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm">Connecting to backend at /api/health...</span>
        </div>
      )}

      {error && (
        <div className="bg-rose-950/40 border border-rose-800/60 rounded-lg p-3.5 text-rose-200">
          <div className="flex items-start space-x-2.5">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold">Backend Unreachable</p>
              <p className="text-xs text-rose-300/80 mt-1 font-mono break-all">{error}</p>
            </div>
          </div>
        </div>
      )}

      {status && (
        <div className="space-y-3">
          <div className="flex items-center justify-between bg-emerald-950/40 border border-emerald-800/50 rounded-lg p-3 text-emerald-200">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span className="text-sm font-medium">FastAPI Service Connected</span>
            </div>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-900/80 text-emerald-300 uppercase tracking-wider">
              {status.status}
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2.5 pt-1">
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3">
              <p className="text-xs text-slate-400">Service</p>
              <p className="text-sm font-medium text-slate-200 truncate mt-0.5">{status.service}</p>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3">
              <p className="text-xs text-slate-400">Version</p>
              <p className="text-sm font-medium text-slate-200 mt-0.5">{status.version}</p>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3">
              <p className="text-xs text-slate-400">Environment</p>
              <p className="text-sm font-medium text-slate-200 capitalize mt-0.5">{status.environment}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
