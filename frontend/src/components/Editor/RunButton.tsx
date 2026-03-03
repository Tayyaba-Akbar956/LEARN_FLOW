import React from 'react'

interface RunButtonProps {
  onClick: () => void
  isExecuting: boolean
  disabled?: boolean
}

export default function RunButton({ onClick, isExecuting, disabled = false }: RunButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || isExecuting}
      aria-label="Run Python Code"
      className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${disabled || isExecuting
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
          : 'bg-green-500 text-white hover:bg-green-600 active:bg-green-700'
        }`}
    >
      {isExecuting ? (
        <>
          <svg
            className="animate-spin h-5 w-5"
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
          <span>Running...</span>
        </>
      ) : (
        <>
          <svg
            className="w-5 h-5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
              clipRule="evenodd"
            />
          </svg>
          <span>Run Code</span>
        </>
      )}
    </button>
  )
}
