import React, { useState, useEffect } from 'react'
import { X, Bell, Mail, Webhook, ShieldCheck, Check, AlertCircle, Loader2 } from 'lucide-react'
import {
  getNotificationPreferences,
  updateNotificationPreferences,
} from '../api/notifications'

interface NotificationSettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

export const NotificationSettingsModal: React.FC<NotificationSettingsModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [inAppEnabled, setInAppEnabled] = useState(true)
  const [emailEnabled, setEmailEnabled] = useState(false)
  const [emailAddress, setEmailAddress] = useState('')
  const [webhookEnabled, setWebhookEnabled] = useState(false)
  const [webhookUrl, setWebhookUrl] = useState('')
  const [webhookSecret, setWebhookSecret] = useState('')
  const [hasSecret, setHasSecret] = useState(false)

  const [docEvents, setDocEvents] = useState(true)
  const [reminderEvents, setReminderEvents] = useState(true)
  const [queryAlerts, setQueryAlerts] = useState(true)

  useEffect(() => {
    if (isOpen) {
      loadPreferences()
    }
  }, [isOpen])

  const loadPreferences = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getNotificationPreferences()
      setInAppEnabled(data.in_app_enabled)
      setEmailEnabled(data.email_enabled)
      setEmailAddress(data.email_address || '')
      setWebhookEnabled(data.webhook_enabled)
      setWebhookUrl(data.webhook_url || '')
      setHasSecret(data.has_webhook_secret)
      setDocEvents(data.document_event_notifications)
      setReminderEvents(data.reminder_notifications)
      setQueryAlerts(data.query_alert_notifications)
    } catch (err: any) {
      setError(err?.message || 'Failed to load notification preferences')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSaving(true)
      setError(null)
      setSuccess(null)

      const payload: any = {
        in_app_enabled: inAppEnabled,
        email_enabled: emailEnabled,
        webhook_enabled: webhookEnabled,
        document_event_notifications: docEvents,
        reminder_notifications: reminderEvents,
        query_alert_notifications: queryAlerts,
        email_address: emailAddress.trim() ? emailAddress.trim() : null,
        webhook_url: webhookUrl.trim() ? webhookUrl.trim() : null,
      }

      if (webhookSecret.trim()) {
        payload.webhook_secret = webhookSecret.trim()
      }

      const updated = await updateNotificationPreferences(payload)
      setHasSecret(updated.has_webhook_secret)
      setWebhookSecret('')
      setSuccess('Preferences saved successfully')
      setTimeout(() => {
        setSuccess(null)
      }, 3000)
    } catch (err: any) {
      setError(err?.message || 'Failed to save preferences')
    } finally {
      setSaving(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Bell className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">Notification Preferences</h3>
              <p className="text-xs text-slate-400">Configure delivery channels and trigger categories</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="p-12 flex flex-col items-center justify-center text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
            <p className="text-sm">Loading notification settings...</p>
          </div>
        ) : (
          <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-6">
            {error && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start space-x-2 text-rose-400 text-xs">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {success && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-2 text-emerald-400 text-xs">
                <Check className="w-4 h-4 shrink-0" />
                <span>{success}</span>
              </div>
            )}

            <div className="space-y-4">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Delivery Channels
              </h4>

              <div className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                      <Bell className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-200">In-App Notification Center</p>
                      <p className="text-xs text-slate-400">Receive instant alerts within the top header bell</p>
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={inAppEnabled}
                    onChange={(e) => setInAppEnabled(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500"
                  />
                </div>

                <div className="pt-3 border-t border-slate-800/60 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400">
                        <Mail className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-200">Email Notifications</p>
                        <p className="text-xs text-slate-400">Deliver notifications via SMTP transport</p>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={emailEnabled}
                      onChange={(e) => setEmailEnabled(e.target.checked)}
                      className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500"
                    />
                  </div>
                  {emailEnabled && (
                    <div className="pl-11 pr-1">
                      <input
                        type="email"
                        placeholder="recipient@example.com"
                        value={emailAddress}
                        onChange={(e) => setEmailAddress(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-800/60 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                        <Webhook className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-200">Webhook Integration</p>
                        <p className="text-xs text-slate-400">POST JSON payloads with HMAC-SHA256 signature</p>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={webhookEnabled}
                      onChange={(e) => setWebhookEnabled(e.target.checked)}
                      className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500"
                    />
                  </div>
                  {webhookEnabled && (
                    <div className="pl-11 pr-1 space-y-2">
                      <input
                        type="url"
                        placeholder="https://api.yourdomain.com/webhooks/intellirag"
                        value={webhookUrl}
                        onChange={(e) => setWebhookUrl(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                      />
                      <div className="relative">
                        <input
                          type="password"
                          placeholder={hasSecret ? '••••••••  (configured - enter new to change)' : 'Webhook Signing Secret'}
                          value={webhookSecret}
                          onChange={(e) => setWebhookSecret(e.target.value)}
                          className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                        />
                        {hasSecret && (
                          <div className="absolute right-3 top-2.5 flex items-center space-x-1 text-[10px] text-emerald-400">
                            <ShieldCheck className="w-3.5 h-3.5" />
                            <span>Active</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Trigger Categories
              </h4>

              <div className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-3">
                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-sm font-medium text-slate-200">Document Processing Events</p>
                    <p className="text-xs text-slate-400">Uploads, successful text & table extractions, failures</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={docEvents}
                    onChange={(e) => setDocEvents(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500"
                  />
                </label>

                <div className="h-px bg-slate-800/60" />

                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-sm font-medium text-slate-200">Reminders & Deadlines</p>
                    <p className="text-xs text-slate-400">Due and overdue alerts for contracts, warranties, and renewals</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={reminderEvents}
                    onChange={(e) => setReminderEvents(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500"
                  />
                </label>

                <div className="h-px bg-slate-800/60" />

                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-sm font-medium text-slate-200">Query & Retrieval Alerts</p>
                    <p className="text-xs text-slate-400">High-volume searches, low confidence warnings</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={queryAlerts}
                    onChange={(e) => setQueryAlerts(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500"
                  />
                </label>
              </div>
            </div>

            <div className="pt-4 flex items-center justify-end space-x-3 border-t border-slate-800">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg shadow-sm transition-colors"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <span>Save Preferences</span>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
