import React, { useState, useEffect } from 'react'
import CodeEditor from '@/components/Editor/CodeEditor'
import ExecutionResults from '@/components/Editor/ExecutionResults'
import RunButton from '@/components/Editor/RunButton'
import ChatInterface from '@/components/Chat/ChatInterface'
import { codeService, ExecutionResult } from '@/services/codeService'

const DEFAULT_CODE = `# Write your Python code here
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
`

export default function EditorPage() {
  const [code, setCode] = useState(DEFAULT_CODE)
  const [result, setResult] = useState<ExecutionResult | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [studentId] = useState('student-1') // TODO: Get from auth context
  const [sessionId] = useState('session-1') // TODO: Get from session context
  const [showChat, setShowChat] = useState(true)

  // Auto-save code to localStorage
  useEffect(() => {
    const timer = setTimeout(() => {
      localStorage.setItem('editor-code', code)
    }, 1000)
    return () => clearTimeout(timer)
  }, [code])

  // Load saved code on mount
  useEffect(() => {
    const savedCode = localStorage.getItem('editor-code')
    if (savedCode) {
      setCode(savedCode)
    }
  }, [])

  const handleRunCode = async () => {
    setIsExecuting(true)
    setResult(null)

    try {
      const submission = await codeService.executeCode({
        code,
        language: 'python',
        student_id: studentId,
        session_id: sessionId,
      })

      // Poll for result if status is pending/running
      if (submission.status === 'pending' || submission.status === 'running') {
        // Wait a bit and check result
        await new Promise(resolve => setTimeout(resolve, 500))
      }

      if (submission.result) {
        setResult(submission.result)
      } else {
        setResult({
          stdout: '',
          stderr: 'Execution failed',
          exit_code: 1,
          execution_time_ms: 0,
          timed_out: false,
          error_message: 'No result returned from sandbox',
        })
      }
    } catch (error) {
      setResult({
        stdout: '',
        stderr: error instanceof Error ? error.message : 'Unknown error',
        exit_code: 1,
        execution_time_ms: 0,
        timed_out: false,
        error_message: 'Failed to execute code',
      })
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Python Editor</h1>
          <button
            onClick={() => setShowChat(!showChat)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            {showChat ? 'Hide Chat' : 'Show Chat'}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor panel */}
        <div className="flex-1 flex flex-col p-6 overflow-auto">
          <div className="space-y-4">
            {/* Editor */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">
                  Code Editor
                </label>
                <RunButton
                  onClick={handleRunCode}
                  isExecuting={isExecuting}
                  disabled={!code.trim()}
                />
              </div>
              <CodeEditor
                value={code}
                onChange={setCode}
                language="python"
                height="500px"
              />
            </div>

            {/* Results */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Execution Results
              </label>
              <ExecutionResults result={result} isExecuting={isExecuting} />
            </div>
          </div>
        </div>

        {/* Chat panel */}
        {showChat && (
          <div className="w-96 border-l border-gray-200 bg-white flex flex-col">
            <div className="px-4 py-3 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">AI Tutor</h2>
              <p className="text-sm text-gray-500">
                Ask questions about your code
              </p>
            </div>
            <div className="flex-1 overflow-hidden">
              <ChatInterface
                studentId={studentId}
                sessionId={sessionId}
                currentCode={code}
                executionResult={result}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
