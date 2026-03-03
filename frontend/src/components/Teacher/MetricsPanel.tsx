import React from 'react'

interface MetricsPanelProps {
  metrics: {
    students_online: number
    pending_alerts: number
    intervention_rate: number
    avg_response_time_seconds: number
  }
}

export default function MetricsPanel({ metrics }: MetricsPanelProps) {
  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-600">Students Online</h3>
          <span className="text-2xl">👥</span>
        </div>
        <div className="text-3xl font-bold text-gray-900">{metrics.students_online}</div>
        <div className="text-xs text-gray-500 mt-1">Currently active</div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-600">Pending Alerts</h3>
          <span className="text-2xl">🔔</span>
        </div>
        <div className="text-3xl font-bold text-red-600">{metrics.pending_alerts}</div>
        <div className="text-xs text-gray-500 mt-1">Require attention</div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-600">Intervention Rate</h3>
          <span className="text-2xl">📊</span>
        </div>
        <div className="text-3xl font-bold text-blue-600">
          {(metrics.intervention_rate * 100).toFixed(0)}%
        </div>
        <div className="text-xs text-gray-500 mt-1">Last 7 days</div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-600">Avg Response Time</h3>
          <span className="text-2xl">⏱️</span>
        </div>
        <div className="text-3xl font-bold text-green-600">
          {formatTime(metrics.avg_response_time_seconds)}
        </div>
        <div className="text-xs text-gray-500 mt-1">Time to acknowledge</div>
      </div>
    </div>
  )
}
