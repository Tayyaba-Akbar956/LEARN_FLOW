/**
 * Chat API client with WebSocket support for LearnFlow.
 */

interface ChatMessage {
  session_id: number
  student_id: number
  message: string
  code?: string
  error_message?: string
}

interface ChatResponse {
  student_message: any
  agent_response: any
  agent_type: string
  routing_confidence: number
}

interface ChatHistoryResponse {
  messages: any[]
  total: number
  session_id: number
}

class ChatService {
  private baseUrl: string
  private ws: WebSocket | null = null

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl
  }

  /**
   * Send a message via HTTP POST.
   */
  async sendMessage(data: ChatMessage): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to send message')
    }

    return response.json()
  }

  /**
   * Get chat history for a session.
   */
  async getChatHistory(
    sessionId: number,
    limit: number = 50,
    offset: number = 0
  ): Promise<ChatHistoryResponse> {
    const params = new URLSearchParams({
      session_id: sessionId.toString(),
      limit: limit.toString(),
      offset: offset.toString(),
    })

    const response = await fetch(`${this.baseUrl}/api/chat/history?${params}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get chat history')
    }

    return response.json()
  }

  /**
   * Connect to WebSocket for streaming responses.
   */
  connectWebSocket(
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}${this.baseUrl}/api/chat/stream`

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      if (onClose) onClose()
      this.ws = null
    }

    return this.ws
  }

  /**
   * Send a message via WebSocket.
   */
  sendWebSocketMessage(data: ChatMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected')
    }

    this.ws.send(JSON.stringify(data))
  }

  /**
   * Close WebSocket connection.
   */
  closeWebSocket(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * Check if WebSocket is connected.
   */
  isWebSocketConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// Export singleton instance
export const chatService = new ChatService()

export default chatService
