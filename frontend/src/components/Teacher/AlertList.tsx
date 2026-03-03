import React from 'react'

interface Alert {
  id: number
  student_id: number
  priority: string
  status: string
  message: string
  created_at: string
}

interface AlertListProps {
  alerts: Alert[]
  onAlertClick: (alert: Alert) => void
  onAcknowledge: (alertId: number) => void
  onResolve: (alertId: number) => void
}

export default function AlertList({
  alerts,
  onAlertClick,
  onAcknowledge,
  onResolve
}: AlertListProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent':
        return 'bg-red-100 border-red-500 text-red-800'
      case 'high':
        return 'bg-orange-100 border-orange-500 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 border-yellow-500 text-yellow-800'
      case 'low':
        return 'bg-blue-100 border-blue-500 text-blue-800'
      default:
        return 'bg-gray-100 border-gray-500 text-gray-800'
    }
  }

  const getTimeAgo = (timestamp: string) => {
    const now = new Date()
    const created = new Date(timestamp)
    const diffMs = now.getTime() - created.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  if (alerts.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No pending alerts</p>
        <p className="text-sm mt-2">All students are doing well!</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`
            p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md
            ${getPriorityColor(alert.priority)}
          `}
          onClick={() => onAlertClick(alert)}
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 text-xs font-bold uppercase rounded">
                {alert.priority}
              </span>
              <span className="text-xs text-gray-600">
                {getTimeAgo(alert.created_at)}
              </span>
            </div>
            <div className="flex gap-2">
              {alert.status === 'pending' && (
                <>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onAcknowledge(alert.id)
                    }}
                    className="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Acknowledge
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onResolve(alert.id)
                    }}
                    className="px-3 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    Resolve
                  </button>
                </>
              )}
            </div>
          </div>

          <p className="text-sm font-medium text-gray-900">{alert.message}</p>

          <div className="mt-2 text-xs text-gray-600">
            Student ID: {alert.student_id} • Status: {alert.status}
          </div>
        </div>
      ))}
    </div>
  )
}
