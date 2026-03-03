import React from 'react'

interface DifficultyIndicatorProps {
  currentDifficulty: string
  performanceScore?: number
}

export default function DifficultyIndicator({
  currentDifficulty,
  performanceScore
}: DifficultyIndicatorProps) {
  const difficulties = ['beginner', 'intermediate', 'advanced']
  const currentIndex = difficulties.indexOf(currentDifficulty.toLowerCase())

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-500'
      case 'intermediate':
        return 'bg-yellow-500'
      case 'advanced':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Current Difficulty</h3>

      <div className="flex items-center gap-2 mb-4">
        {difficulties.map((difficulty, index) => (
          <div
            key={difficulty}
            className={`
              flex-1 h-2 rounded-full transition-all
              ${index <= currentIndex ? getDifficultyColor(difficulty) : 'bg-gray-200'}
            `}
          />
        ))}
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-gray-900 capitalize">
          {currentDifficulty}
        </span>

        {performanceScore !== undefined && (
          <span className="text-gray-600">
            Performance: {Math.round(performanceScore * 100)}%
          </span>
        )}
      </div>

      <div className="mt-3 text-xs text-gray-500">
        {currentIndex === 0 && 'Keep practicing to unlock intermediate exercises'}
        {currentIndex === 1 && 'Great progress! Advanced exercises coming soon'}
        {currentIndex === 2 && 'You\'re at the highest difficulty level!'}
      </div>
    </div>
  )
}
