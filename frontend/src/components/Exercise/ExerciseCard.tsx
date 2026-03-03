import React from 'react'

interface ExerciseCardProps {
  exerciseId: number
  title: string
  difficulty: string
  topic: string
  isActive: boolean
  onSelect: () => void
}

export default function ExerciseCard({
  exerciseId,
  title,
  difficulty,
  topic,
  isActive,
  onSelect
}: ExerciseCardProps) {
  const difficultyColors = {
    beginner: 'bg-green-100 text-green-800 border-green-300',
    intermediate: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    advanced: 'bg-red-100 text-red-800 border-red-300'
  }

  const difficultyColor = difficultyColors[difficulty as keyof typeof difficultyColors] || difficultyColors.beginner

  return (
    <div
      onClick={onSelect}
      className={`
        p-4 rounded-lg border-2 cursor-pointer transition-all
        ${isActive ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'}
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <span className={`px-2 py-1 text-xs font-medium rounded ${difficultyColor}`}>
          {difficulty}
        </span>
      </div>

      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className="px-2 py-1 bg-gray-100 rounded text-xs">
          {topic}
        </span>
        <span className="text-xs text-gray-400">
          #{exerciseId}
        </span>
      </div>
    </div>
  )
}
