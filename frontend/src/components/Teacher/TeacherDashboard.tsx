import React, { useState, useEffect } from 'react'
import AlertList from '@/components/Teacher/AlertList'
import MetricsPanel from '@/components/Teacher/MetricsPanel'
import StudentContext from '@/components/Teacher/StudentContext'
import InterventionForm from '@/components/Teacher/InterventionForm'

interface Alert {
  id: number
  student_id: number
  priority: string
  status: string
  message: string
  created_at: string
}

interface TeacherDashboardProps {
  teacherId: number
}

export default function TeacherDashboard({ teacherId }: TeacherDashboardProps) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [metrics, setMetrics] = useState({
    students_online: 0,
    pending_alerts: 0,
    intervention_rate: 0,
    avg_response_time_seconds: 0
  })
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [studentContext, setStudentContext] = useState<any>(null)
  const [showInterventionForm, setShowInterventionForm] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()

    // Poll for new alerts every 10 seconds
    const interval = setInterval(loadDashboardData, 10000)

    return () => clearInterval(interval)
  }, [teacherId])

  const loadDashboardData = async () => {
    try {
      // Load alerts
      const alertsResponse = await fetch(`/api/teacher/alerts?teacher_id=${teacherId}`)
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json()
        setAlerts(alertsData)
      }

      // Load metrics
      const metricsResponse = await fetch(`/api/teacher/metrics?teacher_id=${teacherId}`)
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json()
        setMetrics(metricsData)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAlertClick = async (alert: Alert) => {
    setSelectedAlert(alert)

    // Load student context
    try {
      const response = await fetch(`/api/teacher/student/${alert.student_id}/context`)
      if (response.ok) {
        const context = await response.json()
        setStudentContext(context)
      }
    } catch (error) {
      console.error('Failed to load student context:', error)
    }
  }

  const handleAcknowledge = async (alertId: number) => {
    try {
      const response = await fetch('/api/teacher/alerts/acknowledge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId, teacher_id: teacherId })
      })

      if (response.ok) {
        loadDashboardData()
      }
    } catch (error) {
      console.error('Failed to acknowledge alert:', error)
    }
  }

  const handleResolve = async (alertId: number) => {
    try {
      const response = await fetch('/api/teacher/alerts/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId, teacher_id: teacherId })
      })

      if (response.ok) {
        loadDashboardData()
        setSelectedAlert(null)
        setStudentContext(null)
      }
    } catch (error) {
      console.error('Failed to resolve alert:', error)
    }
  }

  const handleSendMessage = async (message: string) => {
    if (!selectedAlert || !studentContext) return

    try {
      const response = await fetch('/api/teacher/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          teacher_id: teacherId,
          student_id: selectedAlert.student_id,
          session_id: studentContext.session.id,
          message: message
        })
      })

      if (response.ok) {
        setShowInterventionForm(false)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      throw error
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Teacher Dashboard</h1>
          <p className="text-gray-600">Monitor student progress and respond to struggle alerts</p>
        </div>

        {/* Metrics Panel */}
        <div className="mb-6">
          <MetricsPanel metrics={metrics} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Alerts List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Pending Alerts ({alerts.length})
              </h2>
              <AlertList
                alerts={alerts}
                onAlertClick={handleAlertClick}
                onAcknowledge={handleAcknowledge}
                onResolve={handleResolve}
              />
            </div>
          </div>

          {/* Student Context */}
          <div className="lg:col-span-2">
            {selectedAlert && studentContext ? (
              <div className="space-y-4">
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900">
                      Student Context
                    </h2>
                    <button
                      onClick={() => {
                        setSelectedAlert(null)
                        setStudentContext(null)
                        setShowInterventionForm(false)
                      }}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      ✕
                    </button>
                  </div>

                  <StudentContext context={studentContext} />

                  <div className="mt-4">
                    {!showInterventionForm ? (
                      <button
                        onClick={() => setShowInterventionForm(true)}
                        className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                      >
                        Send Message to Student
                      </button>
                    ) : (
                      <InterventionForm
                        studentId={selectedAlert.student_id}
                        sessionId={studentContext.session.id}
                        teacherId={teacherId}
                        onSend={handleSendMessage}
                        onClose={() => setShowInterventionForm(false)}
                      />
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <p className="text-gray-500">Select an alert to view student context</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
