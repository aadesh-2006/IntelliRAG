import React, { useState, useEffect, useCallback } from 'react'
import { Header } from './components/Header'
import { HeroSection } from './components/HeroSection'
import { StatusBadge } from './components/StatusBadge'
import { ArchitectureOverview } from './components/ArchitectureOverview'
import { Footer } from './components/Footer'
import { checkBackendHealth, HealthStatus } from './api/health'

export const App: React.FC = () => {
  const [status, setStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

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
    verifyHealth()
  }, [verifyHealth])

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
        <HeroSection />
        <div className="max-w-2xl mx-auto">
          <StatusBadge
            status={status}
            loading={loading}
            error={error}
            onRefresh={verifyHealth}
          />
        </div>
        <ArchitectureOverview />
      </main>
      <Footer />
    </div>
  )
}

export default App
