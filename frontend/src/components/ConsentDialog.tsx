'use client'

import { useState, useEffect } from 'react'
import { consentManager } from '@/lib/auth'

interface ConsentDialogProps {
  onConsent: (consented: boolean) => void
}

export function ConsentDialog({ onConsent }: ConsentDialogProps) {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    // Check if user has already consented
    const hasConsented = consentManager.hasConsented()
    if (!hasConsented) {
      setIsOpen(true)
    }
  }, [])

  const handleAccept = () => {
    consentManager.setConsent(true)
    setIsOpen(false)
    onConsent(true)
  }

  const handleDecline = () => {
    consentManager.setConsent(false)
    setIsOpen(false)
    onConsent(false)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="max-w-2xl rounded-lg bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-2xl font-bold text-gray-900">
          Session Monitoring Consent
        </h2>

        <div className="mb-6 space-y-4 text-gray-700">
          <p>
            LearnFlow uses AI-powered session monitoring to provide personalized learning experiences
            and detect when you might need additional help.
          </p>

          <div className="rounded-md bg-blue-50 p-4">
            <h3 className="mb-2 font-semibold text-blue-900">What we monitor:</h3>
            <ul className="list-inside list-disc space-y-1 text-sm text-blue-800">
              <li>Your code submissions and exercise attempts</li>
              <li>Chat conversations with AI tutors</li>
              <li>Time spent on exercises and struggle indicators</li>
              <li>Progress and mastery levels across topics</li>
            </ul>
          </div>

          <div className="rounded-md bg-green-50 p-4">
            <h3 className="mb-2 font-semibold text-green-900">How we use this data:</h3>
            <ul className="list-inside list-disc space-y-1 text-sm text-green-800">
              <li>Adapt exercise difficulty to your skill level</li>
              <li>Detect when you're struggling and alert teachers</li>
              <li>Provide personalized hints and guidance</li>
              <li>Track your learning progress over time</li>
            </ul>
          </div>

          <div className="rounded-md bg-purple-50 p-4">
            <h3 className="mb-2 font-semibold text-purple-900">Your privacy:</h3>
            <ul className="list-inside list-disc space-y-1 text-sm text-purple-800">
              <li>Data is encrypted and stored securely</li>
              <li>Only you and your assigned teachers can view your data</li>
              <li>Data is automatically deleted after 1 year</li>
              <li>You can request data deletion at any time</li>
            </ul>
          </div>

          <p className="text-sm">
            By clicking "Accept", you consent to session monitoring as described above.
            You can withdraw consent at any time in your account settings.
          </p>

          <p className="text-sm">
            For more information, please read our{' '}
            <a
              href="/privacy-policy"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 underline hover:text-blue-800"
            >
              Privacy Policy
            </a>
            .
          </p>
        </div>

        <div className="flex justify-end space-x-4">
          <button
            onClick={handleDecline}
            className="rounded-md border border-gray-300 px-6 py-2 text-gray-700 hover:bg-gray-50"
          >
            Decline
          </button>
          <button
            onClick={handleAccept}
            className="rounded-md bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  )
}
