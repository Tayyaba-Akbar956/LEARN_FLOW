/**
 * Code execution API client
 */

interface ExecuteCodeRequest {
  code: string
  language: string
  student_id: string
  session_id: string
}

interface ExecutionResult {
  stdout: string
  stderr: string
  exit_code: number
  execution_time_ms: number
  timed_out: boolean
  error_message?: string
}

interface CodeSubmission {
  id: string
  student_id: string
  session_id: string
  code: string
  language: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'timeout'
  result?: ExecutionResult
  submitted_at: string
  completed_at?: string
}

interface SandboxInfo {
  timeout_seconds: number
  memory_limit_mb: number
  network_enabled: boolean
  allowed_languages: string[]
}

class CodeService {
  private baseUrl: string

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseUrl = baseUrl
  }

  /**
   * Execute code in sandbox
   */
  async executeCode(request: ExecuteCodeRequest): Promise<CodeSubmission> {
    const response = await fetch(`${this.baseUrl}/api/code/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to execute code')
    }

    return response.json()
  }

  /**
   * Get execution history for a student
   */
  async getHistory(studentId: string, limit: number = 50): Promise<CodeSubmission[]> {
    const response = await fetch(
      `${this.baseUrl}/api/code/history?student_id=${studentId}&limit=${limit}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch execution history')
    }

    return response.json()
  }

  /**
   * Get sandbox configuration info
   */
  async getSandboxInfo(): Promise<SandboxInfo> {
    const response = await fetch(`${this.baseUrl}/api/code/sandbox/info`)

    if (!response.ok) {
      throw new Error('Failed to fetch sandbox info')
    }

    return response.json()
  }
}

export const codeService = new CodeService()
export type { ExecuteCodeRequest, ExecutionResult, CodeSubmission, SandboxInfo }
