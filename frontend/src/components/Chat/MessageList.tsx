import React, { useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'student' | 'agent' | 'teacher'
  content: string
  agent_type?: string
  created_at: string
}

interface MessageListProps {
  messages: Message[]
}

export default function MessageList({ messages }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  }

  const getAgentName = (agentType?: string) => {
    const names: Record<string, string> = {
      concept_explainer: 'Concept Explainer',
      debugger: 'Debugger',
      hint_provider: 'Hint Provider',
    }
    return agentType ? names[agentType] || 'AI Tutor' : 'AI Tutor'
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm mt-2">Ask a question about Python to get started</p>
          </div>
        </div>
      )}

      {messages.map((message, index) => (
        <div
          key={message.id || index}
          className={`flex ${message.role === 'student' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[70%] rounded-lg px-4 py-2 ${
              message.role === 'student'
                ? 'bg-blue-500 text-white'
                : message.role === 'teacher'
                ? 'bg-green-100 text-green-900 border border-green-300'
                : 'bg-gray-100 text-gray-900'
            }`}
          >
            {message.role === 'agent' && (
              <div className="text-xs font-medium mb-1 opacity-70">
                {getAgentName(message.agent_type)}
              </div>
            )}
            {message.role === 'teacher' && (
              <div className="text-xs font-medium mb-1 flex items-center">
                <span className="mr-1">👨‍🏫</span>
                Teacher
              </div>
            )}
            <div className="whitespace-pre-wrap break-words">{message.content}</div>
            <div
              className={`text-xs mt-1 ${
                message.role === 'student' ? 'text-blue-100' : 'text-gray-500'
              }`}
            >
              {formatTime(message.created_at)}
            </div>
          </div>
        </div>
      ))}

      <div ref={messagesEndRef} />
    </div>
  )
}
