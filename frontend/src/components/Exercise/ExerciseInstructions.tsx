import React from 'react'

interface ExerciseInstructionsProps {
  title: string
  instructions: string
  difficulty: string
  topic: string
  expectedOutput?: string
}

export default function ExerciseInstructions({
  title,
  instructions,
  difficulty,
  topic,
  expectedOutput
}: ExerciseInstructionsProps) {
  const difficultyColors = {
    beginner: 'text-green-600',
    intermediate: 'text-yellow-600',
    advanced: 'text-red-600'
  }

  const difficultyColor = difficultyColors[difficulty as keyof typeof difficultyColors] || difficultyColors.beginner

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
        <div className="flex items-center gap-3 text-sm">
          <span className={`font-semibold ${difficultyColor}`}>
            {difficulty.toUpperCase()}
          </span>
          <span className="text-gray-400">•</span>
          <span className="text-gray-600">Topic: {topic}</span>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Instructions</h3>
        <div className="text-gray-800 whitespace-pre-wrap leading-relaxed">
          {instructions}
        </div>
      </div>

      {expectedOutput && (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Expected Output</h3>
          <div className="text-gray-800 text-sm whitespace-pre-wrap font-mono">
            {expectedOutput}
          </div>
        </div>
      )}
    </div>
  )
}
