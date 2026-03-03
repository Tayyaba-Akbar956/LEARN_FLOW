import React from 'react'

interface StudentContextProps {
  context: {
    student: any
    session: any
    recent_messages: any[]
    recent_code: any[]
    recent_exercises: any[]
    struggle_indicators: any
  }
}

export default function StudentContext({ context }: StudentContextProps) {
  const { student, session, recent_messages, recent_code, recent_exercises, struggle_indicators } = context

  return (
    <div className="space-y-6">
      {/* Student Info */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Student Information</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Name:</span>
            <span className="ml-2 font-medium">{student.name}</span>
          </div>
          <div>
            <span className="text-gray-600">Email:</span>
            <span className="ml-2 font-medium">{student.email}</span>
          </div>
          <div>
            <span className="text-gray-600">Session Status:</span>
            <span className="ml-2 font-medium">{session.is_active ? 'Active' : 'Ended'}</span>
          </div>
          <div>
            <span className="text-gray-600">Session Started:</span>
            <span className="ml-2 font-medium">
              {new Date(session.started_at).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Struggle Indicators */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Struggle Indicators</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {(struggle_indicators.failure_rate * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-600">Failure Rate</div>
          </div>
          <div className="p-3 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {struggle_indicators.avg_hints_used.toFixed(1)}
            </div>
            <div className="text-xs text-gray-600">Avg Hints Used</div>
          </div>
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {struggle_indicators.total_attempts}
            </div>
            <div className="text-xs text-gray-600">Total Attempts</div>
          </div>
          <div className="p-3 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {(struggle_indicators.avg_time_seconds / 60).toFixed(1)}m
            </div>
            <div className="text-xs text-gray-600">Avg Time per Exercise</div>
          </div>
        </div>
      </div>

      {/* Recent Chat Messages */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Chat Messages</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {recent_messages.length === 0 ? (
            <p className="text-sm text-gray-500">No recent messages</p>
          ) : (
            recent_messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-2 rounded text-sm ${
                  msg.role === 'student' ? 'bg-blue-50' : 'bg-gray-50'
                }`}
              >
                <div className="font-semibold text-xs text-gray-600 mb-1">
                  {msg.role === 'student' ? 'Student' : msg.role === 'teacher' ? 'Teacher' : 'AI Agent'}
                </div>
                <div className="text-gray-800">{msg.content}</div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Code Submissions */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Code</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {recent_code.length === 0 ? (
            <p className="text-sm text-gray-500">No recent code submissions</p>
          ) : (
            recent_code.map((code, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-600">
                    {new Date(code.submitted_at).toLocaleString()}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    code.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {code.status}
                  </span>
                </div>
                <pre className="text-xs bg-white p-2 rounded overflow-x-auto">
                  {code.code.substring(0, 200)}
                  {code.code.length > 200 && '...'}
                </pre>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Exercises */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Exercises</h3>
        <div className="space-y-2">
          {recent_exercises.length === 0 ? (
            <p className="text-sm text-gray-500">No recent exercises</p>
          ) : (
            recent_exercises.map((exercise, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Exercise #{exercise.exercise_id}</div>
                    <div className="text-xs text-gray-600">
                      Hints: {exercise.hints_used} • Time: {(exercise.time_spent_seconds / 60).toFixed(1)}m
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded ${
                    exercise.is_correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {exercise.is_correct ? 'Correct' : 'Incorrect'}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
