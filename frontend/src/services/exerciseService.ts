/**
 * Exercise API client for LearnFlow.
 */

interface GenerateExerciseRequest {
  student_id: number
  topic: string
  difficulty?: string
  session_id: number
}

interface GenerateExerciseResponse {
  exercise_id: number
  title: string
  instructions: string
  difficulty: string
  topic: string
  solution_template?: string
  expected_output?: string
  total_hints: number
}

interface SubmitSolutionRequest {
  student_id: number
  exercise_id: number
  session_id: number
  solution_code: string
  hints_used: number
  time_spent_seconds?: number
}

interface SubmitSolutionResponse {
  attempt_id: number
  is_correct: boolean
  test_results: any[]
  total_tests: number
  passed_tests: number
  feedback: string
  next_difficulty?: string
}

interface GetHintsResponse {
  hint: any
  has_more_hints: boolean
  total_hints_available: number
}

class ExerciseService {
  private baseUrl: string

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl
  }

  /**
   * Generate a new exercise for a student.
   */
  async generateExercise(data: GenerateExerciseRequest): Promise<GenerateExerciseResponse> {
    const response = await fetch(`${this.baseUrl}/api/exercises/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to generate exercise')
    }

    return response.json()
  }

  /**
   * Submit a solution for validation.
   */
  async submitSolution(data: SubmitSolutionRequest): Promise<SubmitSolutionResponse> {
    const response = await fetch(`${this.baseUrl}/api/exercises/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to submit solution')
    }

    return response.json()
  }

  /**
   * Get hints for an exercise.
   */
  async getHints(
    studentId: number,
    exerciseId: number,
    hintsAlreadyUsed: number
  ): Promise<GetHintsResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/exercises/hints?student_id=${studentId}&exercise_id=${exerciseId}&hints_already_used=${hintsAlreadyUsed}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get hints')
    }

    return response.json()
  }
}

// Export singleton instance
export const exerciseService = new ExerciseService()

export type {
  GenerateExerciseRequest,
  GenerateExerciseResponse,
  SubmitSolutionRequest,
  SubmitSolutionResponse,
  GetHintsResponse,
}
