/**
 * Teacher API client for LearnFlow.
 */

interface Alert {
  id: number
  student_id: number
  priority: string
  status: string
  message: string
  student_context?: string
  created_at: string
}

interface StudentContext {
  student: any
  session: any
  recent_messages: any[]
  recent_code: any[]
  recent_exercises: any[]
  struggle_indicators: any
}

interface Metrics {
  students_online: number
  pending_alerts: number
  intervention_rate: number
  avg_response_time_seconds: number
}

class TeacherService {
  private baseUrl: string

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl
  }

  /**
   * Get alerts for a teacher.
   */
  async getAlerts(teacherId: number, status?: string, limit: number = 50): Promise<Alert[]> {
    const params = new URLSearchParams({
      teacher_id: teacherId.toString(),
      limit: limit.toString()
    })

    if (status) {
      params.append('status', status)
    }

    const response = await fetch(`${this.baseUrl}/api/teacher/alerts?${params}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get alerts')
    }

    return response.json()
  }

  /**
   * Acknowledge an alert.
   */
  async acknowledgeAlert(alertId: number, teacherId: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/teacher/alerts/acknowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alert_id: alertId, teacher_id: teacherId })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to acknowledge alert')
    }
  }

  /**
   * Resolve an alert.
   */
  async resolveAlert(
    alertId: number,
    teacherId: number,
    resolutionNotes?: string
  ): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/teacher/alerts/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        alert_id: alertId,
        teacher_id: teacherId,
        resolution_notes: resolutionNotes
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to resolve alert')
    }
  }

  /**
   * Get student context.
   */
  async getStudentContext(
    studentId: number,
    sessionId?: number
  ): Promise<StudentContext> {
    const params = new URLSearchParams({ student_id: studentId.toString() })

    if (sessionId) {
      params.append('session_id', sessionId.toString())
    }

    const response = await fetch(
      `${this.baseUrl}/api/teacher/student/${studentId}/context?${params}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get student context')
    }

    return response.json()
  }

  /**
   * Send message to student.
   */
  async sendMessage(
    teacherId: number,
    studentId: number,
    sessionId: number,
    message: string
  ): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/teacher/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        teacher_id: teacherId,
        student_id: studentId,
        session_id: sessionId,
        message: message
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to send message')
    }
  }

  /**
   * Get teacher metrics.
   */
  async getMetrics(teacherId: number): Promise<Metrics> {
    const response = await fetch(
      `${this.baseUrl}/api/teacher/metrics?teacher_id=${teacherId}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get metrics')
    }

    return response.json()
  }
}

// Export singleton instance
export const teacherService = new TeacherService()

export type { Alert, StudentContext, Metrics }
