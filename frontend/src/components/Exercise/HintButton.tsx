import React, { useState } from 'react'

interface HintButtonProps {
  exerciseId: number
  studentId: number
  hintsUsed: number
  totalHints: number
  onHintReceived: (hint: any) => void
}

export default function HintButton({
  exerciseId,
  studentId,
  hintsUsed,
  totalHints,
  onHintReceived
}: HintButtonProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const hasMoreHints = hintsUsed < totalHints

  const requestHint = async () => {
    if (!hasMoreHints || isLoading) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `/api/exercises/hints?student_id=${studentId}&exercise_id=${exerciseId}&hints_already_used=${hintsUsed}`
      )

      if (!response.ok) {
        throw new Error('Failed to get hint')
      }

      const data = await response.json()

      if (data.hint) {
        onHintReceived(data.hint)
      } else {
        setError('No more hints available')
      }
    } catch (err) {
      setError('Failed to load hint')
      console.error('Hint request error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <button
        onClick={requestHint}
        disabled={!hasMoreHints || isLoading}
        className={`
          px-4 py-2 rounded-lg font-medium transition-all
          ${hasMoreHints && !isLoading
            ? 'bg-blue-500 text-white hover:bg-blue-600'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }
        `}
      >
        {isLoading ? 'Loading...' : `Get Hint (${hintsUsed}/${totalHints} used)`}
      </button>

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      {!hasMoreHints && (
        <p className="text-sm text-gray-500">All hints used</p>
      )}
    </div>
  )
}
