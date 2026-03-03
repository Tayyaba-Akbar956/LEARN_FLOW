'use client'

import React, { useState, useEffect } from 'react'
import ExerciseCard from '@/components/Exercise/ExerciseCard'
import ExerciseInstructions from '@/components/Exercise/ExerciseInstructions'
import HintButton from '@/components/Exercise/HintButton'
import SubmitSolution from '@/components/Exercise/SubmitSolution'
import DifficultyIndicator from '@/components/Exercise/DifficultyIndicator'
import CodeEditor from '@/components/Editor/CodeEditor'
import { exerciseService } from '@/services/exerciseService'

interface Exercise {
  exercise_id: number
  title: string
  instructions: string
  difficulty: string
  topic: string
  solution_template?: string
  expected_output?: string
  total_hints: number
}

interface Hint {
  id: number
  level: string
  sequence: number
  content: string
}

export default function ExercisesPage() {
  const [studentId] = useState(1) // TODO: Get from auth context
  const [sessionId] = useState(1) // TODO: Get from session context
  const [currentExercise, setCurrentExercise] = useState<Exercise | null>(null)
  const [solutionCode, setSolutionCode] = useState('')
  const [hints, setHints] = useState<Hint[]>([])
  const [hintsUsed, setHintsUsed] = useState(0)
  const [startTime, setStartTime] = useState<number>(Date.now())
  const [isGenerating, setIsGenerating] = useState(false)
  const [topic, setTopic] = useState('loops')
  const [performanceScore, setPerformanceScore] = useState<number | undefined>(undefined)

  const topics = ['loops', 'functions', 'lists', 'dictionaries', 'classes', 'file-io']

  const generateNewExercise = async (selectedTopic?: string) => {
    setIsGenerating(true)
    setHints([])
    setHintsUsed(0)
    setStartTime(Date.now())

    try {
      const exercise = await exerciseService.generateExercise({
        student_id: studentId,
        topic: selectedTopic || topic,
        session_id: sessionId
      })

      setCurrentExercise(exercise)
      setSolutionCode(exercise.solution_template || '# Write your solution here\n')
    } catch (error) {
      console.error('Failed to generate exercise:', error)
      alert('Failed to generate exercise. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleHintReceived = (hint: Hint) => {
    setHints([...hints, hint])
    setHintsUsed(hintsUsed + 1)
  }

  const handleSubmitComplete = (result: any) => {
    if (result.is_correct) {
      // Calculate performance score based on hints used and time
      const timeSpent = (Date.now() - startTime) / 1000
      const timeScore = timeSpent < 300 ? 1.0 : timeSpent < 600 ? 0.7 : 0.3
      const hintScore = Math.max(0, 1.0 - (hintsUsed * 0.25))
      const score = (1.0 * 0.5) + (timeScore * 0.25) + (hintScore * 0.25)
      setPerformanceScore(score)
    }
  }

  useEffect(() => {
    // Generate initial exercise on mount
    generateNewExercise()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Practice Exercises</h1>
          <p className="text-gray-600">
            Complete exercises to improve your Python skills. Difficulty adapts based on your performance.
          </p>
        </div>

        {/* Topic Selection */}
        <div className="mb-6 bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Select Topic</h2>
          <div className="flex flex-wrap gap-2">
            {topics.map((t) => (
              <button
                key={t}
                onClick={() => {
                  setTopic(t)
                  generateNewExercise(t)
                }}
                className={`
                  px-4 py-2 rounded-lg font-medium transition-all
                  ${topic === t
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                {t.replace('-', ' ')}
              </button>
            ))}
          </div>
        </div>

        {isGenerating ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-600">Generating personalized exercise...</p>
            </div>
          </div>
        ) : currentExercise ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Instructions and Hints */}
            <div className="lg:col-span-1 space-y-6">
              <ExerciseInstructions
                title={currentExercise.title}
                instructions={currentExercise.instructions}
                difficulty={currentExercise.difficulty}
                topic={currentExercise.topic}
                expectedOutput={currentExercise.expected_output}
              />

              <DifficultyIndicator
                currentDifficulty={currentExercise.difficulty}
                performanceScore={performanceScore}
              />

              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Need Help?</h3>
                <HintButton
                  exerciseId={currentExercise.exercise_id}
                  studentId={studentId}
                  hintsUsed={hintsUsed}
                  totalHints={currentExercise.total_hints}
                  onHintReceived={handleHintReceived}
                />

                {hints.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {hints.map((hint, index) => (
                      <div
                        key={hint.id}
                        className="p-3 bg-blue-50 border border-blue-200 rounded-lg"
                      >
                        <div className="text-xs font-semibold text-blue-600 mb-1">
                          Hint {index + 1} ({hint.level})
                        </div>
                        <div className="text-sm text-gray-800">{hint.content}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={() => generateNewExercise()}
                className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
              >
                Generate New Exercise
              </button>
            </div>

            {/* Right Column - Code Editor and Submit */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Your Solution</h3>
                <CodeEditor
                  value={solutionCode}
                  onChange={setSolutionCode}
                  language="python"
                  height="400px"
                />
              </div>

              <SubmitSolution
                exerciseId={currentExercise.exercise_id}
                studentId={studentId}
                sessionId={sessionId}
                solutionCode={solutionCode}
                hintsUsed={hintsUsed}
                timeSpentSeconds={(Date.now() - startTime) / 1000}
                onSubmitComplete={handleSubmitComplete}
              />
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-600">No exercise loaded. Click a topic to get started.</p>
          </div>
        )}
      </div>
    </div>
  )
}
