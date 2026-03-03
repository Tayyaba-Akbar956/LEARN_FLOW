import React, { useState } from 'react'

interface TestResult {
  description: string
  input: any
  expected_output: any
  actual_output: any
  passed: boolean
  error?: string
}

interface SubmitSolutionProps {
  exerciseId: number
  studentId: number
  sessionId: number
  solutionCode: string
  hintsUsed: number
  timeSpentSeconds: number
  onSubmitComplete: (result: any) => void
}

export default function SubmitSolution({
  exerciseId,
  studentId,
  sessionId,
  solutionCode,
  hintsUsed,
  timeSpentSeconds,
  onSubmitComplete
}: SubmitSolutionProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleSubmit = async () => {
    if (!solutionCode.trim() || isSubmitting) return

    setIsSubmitting(true)
    setResult(null)

    try {
      const response = await fetch('/api/exercises/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          student_id: studentId,
          exercise_id: exerciseId,
          session_id: sessionId,
          solution_code: solutionCode,
          hints_used: hintsUsed,
          time_spent_seconds: timeSpentSeconds
        })
      })

      if (!response.ok) {
        throw new Error('Failed to submit solution')
      }

      const data = await response.json()
      setResult(data)
      onSubmitComplete(data)
    } catch (err) {
      console.error('Submit error:', err)
      setResult({
        is_correct: false,
        feedback: 'Failed to submit solution. Please try again.'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-4">
      <button
        onClick={handleSubmit}
        disabled={!solutionCode.trim() || isSubmitting}
        className={`
          w-full px-6 py-3 rounded-lg font-semibold transition-all
          ${solutionCode.trim() && !isSubmitting
            ? 'bg-green-500 text-white hover:bg-green-600'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }
        `}
      >
        {isSubmitting ? 'Submitting...' : 'Submit Solution'}
      </button>

      {result && (
        <div className={`
          p-4 rounded-lg border-2
          ${result.is_correct ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'}
        `}>
          <div className="flex items-center gap-2 mb-2">
            <span className={`text-lg font-bold ${result.is_correct ? 'text-green-700' : 'text-red-700'}`}>
              {result.is_correct ? '✓ Correct!' : '✗ Incorrect'}
            </span>
            <span className="text-sm text-gray-600">
              ({result.passed_tests}/{result.total_tests} tests passed)
            </span>
          </div>

          <p className="text-gray-800 mb-3">{result.feedback}</p>

          {result.test_results && result.test_results.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-gray-700">Test Results:</h4>
              {result.test_results.map((test: TestResult, index: number) => (
                <div
                  key={index}
                  className={`
                    p-3 rounded border text-sm
                    ${test.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}
                  `}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={test.passed ? 'text-green-600' : 'text-red-600'}>
                      {test.passed ? '✓' : '✗'}
                    </span>
                    <span className="font-medium text-gray-700">{test.description}</span>
                  </div>
                  {!test.passed && (
                    <div className="ml-6 text-xs text-gray-600 space-y-1">
                      <div>Expected: <code className="bg-white px-1 py-0.5 rounded">{JSON.stringify(test.expected_output)}</code></div>
                      <div>Got: <code className="bg-white px-1 py-0.5 rounded">{JSON.stringify(test.actual_output)}</code></div>
                      {test.error && <div className="text-red-600">Error: {test.error}</div>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {result.next_difficulty && (
            <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
              Next exercise difficulty: <strong>{result.next_difficulty}</strong>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
