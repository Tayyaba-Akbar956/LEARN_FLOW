import React from 'react'

interface ExecutionResult {
  stdout: string
  stderr: string
  exit_code: number
  execution_time_ms: number
  timed_out: boolean
  error_message?: string
}

interface ExecutionResultsProps {
  result: ExecutionResult | null
  isExecuting: boolean
}

export default function ExecutionResults({ result, isExecuting }: ExecutionResultsProps) {
  if (isExecuting) {
    return (
      <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
        <div className="flex items-center space-x-2">
          <svg
            className="animate-spin h-5 w-5 text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span className="text-blue-400">Executing code...</span>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg text-gray-500 text-center">
        <p>Click "Run" to execute your code</p>
        <p className="text-sm mt-1">Results will appear here</p>
      </div>
    )
  }

  const hasOutput = result.stdout || result.stderr
  const success = result.exit_code === 0 && !result.timed_out

  return (
    <div className="space-y-3">
      {/* Status header */}
      <div
        className={`flex items-center justify-between p-3 rounded-lg ${
          success
            ? 'bg-green-50 border border-green-200'
            : 'bg-red-50 border border-red-200'
        }`}
      >
        <div className="flex items-center space-x-2">
          {success ? (
            <>
              <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="text-green-800 font-medium">Success</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="text-red-800 font-medium">
                {result.timed_out ? 'Timeout' : 'Error'}
              </span>
            </>
          )}
        </div>
        <div className="text-sm text-gray-600">
          {result.execution_time_ms.toFixed(0)}ms
        </div>
      </div>

      {/* Output */}
      {hasOutput && (
        <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm overflow-auto max-h-96">
          {result.stdout && (
            <div className="mb-2">
              <div className="text-green-400 text-xs mb-1">STDOUT:</div>
              <pre className="whitespace-pre-wrap">{result.stdout}</pre>
            </div>
          )}
          {result.stderr && (
            <div>
              <div className="text-red-400 text-xs mb-1">STDERR:</div>
              <pre className="whitespace-pre-wrap text-red-300">{result.stderr}</pre>
            </div>
          )}
        </div>
      )}

      {/* Error message */}
      {result.error_message && (
        <div className="bg-red-50 border border-red-200 p-3 rounded-lg">
          <div className="text-red-800 text-sm font-medium mb-1">Error:</div>
          <div className="text-red-700 text-sm">{result.error_message}</div>
        </div>
      )}

      {/* Timeout message */}
      {result.timed_out && (
        <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
          <div className="text-yellow-800 text-sm">
            ⏱️ Code execution timed out after 5 seconds. Check for infinite loops or long-running operations.
          </div>
        </div>
      )}

      {/* No output message */}
      {!hasOutput && !result.error_message && success && (
        <div className="bg-gray-50 border border-gray-200 p-3 rounded-lg text-gray-600 text-sm text-center">
          Code executed successfully with no output
        </div>
      )}
    </div>
  )
}
