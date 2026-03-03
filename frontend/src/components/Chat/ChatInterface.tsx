import React, { useState, useEffect, useRef } from 'react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import AgentIndicator from './AgentIndicator'

interface Message {
  id: string
  role: 'student' | 'agent' | 'teacher'
  content: string
  agent_type?: string
  created_at: string
}

interface ChatInterfaceProps {
  sessionId: number
  studentId: number
  currentCode?: string
  executionResult?: any
}

export default function ChatInterface({ sessionId, studentId, currentCode, executionResult }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Load chat history on mount
    loadChatHistory()

    // Setup WebSocket connection
    setupWebSocket()

    return () => {
      // Cleanup WebSocket on unmount
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [sessionId])

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`/api/chat/history?session_id=${sessionId}`)
      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages)
      }
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }

  const setupWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/chat/stream`)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'chunk') {
        // Append chunk to current agent message
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1]
          if (lastMessage && lastMessage.role === 'agent' && !lastMessage.id) {
            // Update streaming message
            return [
              ...prev.slice(0, -1),
              { ...lastMessage, content: lastMessage.content + data.content },
            ]
          } else {
            // Start new streaming message
            return [
              ...prev,
              {
                id: '',
                role: 'agent',
                content: data.content,
                created_at: new Date().toISOString(),
              },
            ]
          }
        })
      } else if (data.type === 'done') {
        setIsLoading(false)
        setCurrentAgent(null)
      } else if (data.type === 'error') {
        console.error('WebSocket error:', data.message)
        setIsLoading(false)
        setCurrentAgent(null)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsLoading(false)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    wsRef.current = ws
  }

  const handleSendMessage = async (
    content: string,
    code?: string,
    errorMessage?: string
  ) => {
    // Add student message to UI immediately
    const studentMessage: Message = {
      id: Date.now().toString(),
      role: 'student',
      content,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, studentMessage])
    setIsLoading(true)

    // Send via WebSocket with code context
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          session_id: sessionId,
          student_id: studentId,
          message: content,
          code: code || currentCode,
          error_message: errorMessage,
          execution_result: executionResult,
        })
      )
    } else {
      // Fallback to HTTP if WebSocket not available
      try {
        const response = await fetch('/api/chat/message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            student_id: studentId,
            message: content,
            code: code || currentCode,
            error_message: errorMessage,
            execution_result: executionResult,
          }),
        })

        if (response.ok) {
          const data = await response.json()
          setMessages((prev) => [...prev, data.agent_response])
          setCurrentAgent(data.agent_type)
        }
      } catch (error) {
        console.error('Failed to send message:', error)
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} />
      </div>

      {currentAgent && (
        <div className="border-t border-gray-200 px-4 py-2">
          <AgentIndicator agentType={currentAgent} />
        </div>
      )}

      <div className="border-t border-gray-200">
        <MessageInput onSend={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}
