import React, { useState } from 'react'

interface InterventionFormProps {
  studentId: number
  sessionId: number
  teacherId: number
  onSend: (message: string) => void
  onClose: () => void
}

export default function InterventionForm({
  studentId,
  sessionId,
  teacherId,
  onSend,
  onClose
}: InterventionFormProps) {
  const [message, setMessage] = useState('')
  const [isSending, setIsSending] = useState(false)

  const handleSend = async () => {
    if (!message.trim() || isSending) return

    setIsSending(true)
    try {
      await onSend(message)
      setMessage('')
      onClose()
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Send Message to Student</h3>

      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message to the student..."
        className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        rows={4}
      />

      <div className="flex gap-2 mt-3">
        <button
          onClick={handleSend}
          disabled={!message.trim() || isSending}
          className={`
            flex-1 px-4 py-2 rounded-lg font-medium transition-all
            ${message.trim() && !isSending
              ? 'bg-blue-500 text-white hover:bg-blue-600'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {isSending ? 'Sending...' : 'Send Message'}
        </button>
        <button
          onClick={onClose}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
        >
          Cancel
        </button>
      </div>

      <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
        <strong>Tip:</strong> Your message will appear in the student's chat interface with a clear indication that it's from a human teacher.
      </div>
    </div>
  )
}
