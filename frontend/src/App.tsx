import { useEffect, useState } from 'react'
import './App.css'
import { fetchHealth, fetchStats, type HealthResponse, type StatsResponse } from './api/client'

const REFRESH_INTERVAL_MS = 5000

function formatPercent(ratio: number | null): string {
  return ratio === null ? '—' : `${(ratio * 100).toFixed(1)}%`
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function refresh() {
      try {
        const [healthData, statsData] = await Promise.all([fetchHealth(), fetchStats()])
        if (cancelled) return
        setHealth(healthData)
        setStats(statsData)
        setError(null)
      } catch (err) {
        if (cancelled) return
        setHealth(null)
        setError(err instanceof Error ? err.message : 'Failed to reach backend')
      }
    }

    refresh()
    const interval = setInterval(refresh, REFRESH_INTERVAL_MS)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  return (
    <main className="page">
      <h1>SRE Alert Testing</h1>
      <p className="subtitle">
        Backend:{' '}
        <span className={`badge ${health ? 'badge-up' : 'badge-down'}`}>
          {health ? `${health.service} is up` : 'unreachable'}
        </span>
      </p>

      {error && <p className="error">{error}</p>}

      {stats && (
        <table className="stats-table">
          <thead>
            <tr>
              <th>Endpoint</th>
              <th>Path</th>
              <th>Target uptime</th>
              <th>Observed uptime</th>
              <th>Requests</th>
            </tr>
          </thead>
          <tbody>
            {stats.endpoints.map((endpoint) => (
              <tr key={endpoint.name}>
                <td>{endpoint.name}</td>
                <td>
                  <code>{endpoint.path}</code>
                </td>
                <td>{formatPercent(endpoint.target_uptime)}</td>
                <td>{formatPercent(endpoint.observed_success_ratio)}</td>
                <td>{endpoint.total_requests}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  )
}

export default App
