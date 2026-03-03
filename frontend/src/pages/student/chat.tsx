import React from 'react'
import ChatInterface from '@/components/Chat/ChatInterface'

export default function StudentChatPage() {
  // TODO: Get sessionId and studentId from auth context or route params
  const sessionId = 1 // Placeholder
  const studentId = 1 // Placeholder

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Python Tutor Chat</h1>
          <p className="text-gray-600 mt-2">
            Ask questions, get help debugging, or request hints for exercises
          </p>
        </div>

        <div className="h-[calc(100vh-200px)]">
          <ChatInterface sessionId={sessionId} studentId={studentId} />
        </div>

        <div className="mt-4 text-sm text-gray-500 text-center">
          <p>
            💡 Tip: The AI tutor uses the Socratic method - it guides you to discover answers
            rather than giving them directly
          </p>
        </div>
      </div>
    </div>
  )
}
