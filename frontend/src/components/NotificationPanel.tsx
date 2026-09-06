import React, { useState, useEffect, useRef } from 'react'
import {
  Bell,
  CheckCheck,
  Trash2,
  Settings,
  RefreshCw,
  AlertTriangle,
  Info,
  AlertCircle,
  FileText,
  Calendar,
  Loader2,
} from 'lucide-react'
import {
  NotificationItem,
  getNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  deleteNotification,
  processPendingNotifications,
} from '../api/notifications'
import { NotificationSettingsModal } from './NotificationSettingsModal'

interface NotificationPanelProps {
  isOpen: boolean
  onClose: () => void
  onUnreadCountChange?: (count: number) => void
}

export const NotificationPanel: React.FC<NotificationPanelProps> = ({
  isOpen,
  onClose,
  onUnreadCountChange,
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [filterUnread, setFilterUnread] = useState(false)
  const [severityFilter, setSeverityFilter] = useState('ALL')
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [retrying, setRetrying] = useState(false)
  const panelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      loadNotifications()
    }
  }, [isOpen, filterUnread, severityFilter])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        isOpen &&
        panelRef.current &&
        !panelRef.current.contains(e.target as Node) &&
        !settingsOpen
      ) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, settingsOpen, onClose])

  const loadNotifications = async () => {
    try {
      setLoading(true)
      const res = await getNotifications({
        unread: filterUnread ? true : undefined,
        severity: severityFilter,
        limit: 50,
      })
      setNotifications(res.items)
      setUnreadCount(res.unread_count)
      if (onUnreadCountChange) {
        onUnreadCountChange(res.unread_count)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await markNotificationAsRead(id)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read_at: new Date().toISOString() } : n))
      )
      const newCount = Math.max(0, unreadCount - 1)
      setUnreadCount(newCount)
      if (onUnreadCountChange) onUnreadCountChange(newCount)
    } catch (err) {
      console.error(err)
    }
  }

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsAsRead()
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, read_at: new Date().toISOString() }))
      )
      setUnreadCount(0)
      if (onUnreadCountChange) onUnreadCountChange(0)
    } catch (err) {
      console.error(err)
    }
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await deleteNotification(id)
      const target = notifications.find((n) => n.id === id)
      setNotifications((prev) => prev.filter((n) => n.id !== id))
      if (target && !target.read_at) {
        const newCount = Math.max(0, unreadCount - 1)
        setUnreadCount(newCount)
        if (onUnreadCountChange) onUnreadCountChange(newCount)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleProcessPending = async () => {
    try {
      setRetrying(true)
      await processPendingNotifications()
      await loadNotifications()
    } catch (err) {
      console.error(err)
    } finally {
      setRetrying(false)
    }
  }

  const getEventIcon = (type: string, severity: string) => {
    if (type.startsWith('DOCUMENT_')) {
      if (type === 'DOCUMENT_FAILED') return <AlertCircle className="w-4 h-4 text-rose-400" />
      return <FileText className="w-4 h-4 text-indigo-400" />
    }
    if (type.startsWith('REMINDER_')) {
      if (type === 'REMINDER_OVERDUE') return <AlertTriangle className="w-4 h-4 text-rose-400" />
      return <Calendar className="w-4 h-4 text-amber-400" />
    }
    if (severity === 'WARNING') return <AlertTriangle className="w-4 h-4 text-amber-400" />
    if (severity === 'ERROR' || severity === 'CRITICAL')
      return <AlertCircle className="w-4 h-4 text-rose-400" />
    return <Info className="w-4 h-4 text-cyan-400" />
  }

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      const diffHours = Math.floor(diffMins / 60)
      if (diffHours < 24) return `${diffHours}h ago`
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    } catch {
      return ''
    }
  }

  if (!isOpen) return null

  return (
    <>
      <div
        ref={panelRef}
        className="absolute right-0 mt-2 w-96 sm:w-[420px] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-200"
      >
        <div className="p-4 border-b border-slate-800 bg-slate-950/70 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bell className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Notifications</h3>
            {unreadCount > 0 && (
              <span className="px-1.5 py-0.5 text-[10px] font-bold bg-indigo-500 text-white rounded-full">
                {unreadCount}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-1">
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                title="Mark all as read"
                className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <CheckCheck className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={handleProcessPending}
              disabled={retrying}
              title="Retry pending deliveries"
              className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${retrying ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
            <button
              onClick={() => setSettingsOpen(true)}
              title="Notification Settings"
              className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="px-4 py-2 border-b border-slate-800/80 bg-slate-900/90 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setFilterUnread(false)}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                !filterUnread
                  ? 'bg-slate-800 text-white font-medium'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterUnread(true)}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                filterUnread
                  ? 'bg-slate-800 text-white font-medium'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Unread
            </button>
          </div>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700/80 rounded px-2 py-0.5 text-[11px] text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Severity</option>
            <option value="INFO">Info</option>
            <option value="WARNING">Warning</option>
            <option value="ERROR">Error</option>
          </select>
        </div>

        <div className="max-h-[380px] overflow-y-auto divide-y divide-slate-800/60">
          {loading ? (
            <div className="p-8 flex flex-col items-center justify-center text-slate-500">
              <Loader2 className="w-6 h-6 animate-spin text-indigo-500 mb-2" />
              <p className="text-xs">Loading notifications...</p>
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-slate-500">
              <Bell className="w-8 h-8 mx-auto mb-2 opacity-30" />
              <p className="text-xs">No notifications to display</p>
            </div>
          ) : (
            notifications.map((notif) => {
              const isUnread = !notif.read_at
              return (
                <div
                  key={notif.id}
                  onClick={(e) => isUnread && handleMarkRead(notif.id, e)}
                  className={`p-3.5 flex items-start space-x-3 transition-colors ${
                    isUnread ? 'bg-indigo-950/20 hover:bg-indigo-950/30' : 'hover:bg-slate-800/40'
                  }`}
                >
                  <div className="mt-0.5 shrink-0">
                    <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center">
                      {getEventIcon(notif.notification_type, notif.severity)}
                    </div>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between space-x-2">
                      <p
                        className={`text-xs truncate ${
                          isUnread ? 'font-semibold text-white' : 'font-medium text-slate-300'
                        }`}
                      >
                        {notif.title}
                      </p>
                      <span className="text-[10px] text-slate-500 shrink-0">
                        {formatTime(notif.created_at)}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">
                      {notif.message}
                    </p>

                    <div className="mt-2 flex items-center justify-between text-[10px]">
                      <div className="flex items-center space-x-1.5">
                        <span className="px-1.5 py-0.2 bg-slate-800 text-slate-400 rounded border border-slate-700/60 uppercase text-[9px] font-medium">
                          {notif.channel}
                        </span>
                        {notif.status === 'FAILED' && (
                          <span className="text-rose-400 font-medium">Delivery Failed</span>
                        )}
                      </div>

                      <div className="flex items-center space-x-1 opacity-80 hover:opacity-100">
                        {isUnread && (
                          <button
                            onClick={(e) => handleMarkRead(notif.id, e)}
                            title="Mark as read"
                            className="p-1 text-slate-400 hover:text-indigo-400 transition-colors"
                          >
                            <CheckCheck className="w-3.5 h-3.5" />
                          </button>
                        )}
                        <button
                          onClick={(e) => handleDelete(notif.id, e)}
                          title="Delete"
                          className="p-1 text-slate-400 hover:text-rose-400 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      <NotificationSettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </>
  )
}
