import React from 'react'

interface AgentIndicatorProps {
  agentType: string
}

export default function AgentIndicator({ agentType }: AgentIndicatorProps) {
  const agentInfo: Record<string, { name: string; icon: string; color: string; description: string }> = {
    concept_explainer: {
      name: 'Concept Explainer',
      icon: '💡',
      color: 'bg-purple-100 text-purple-800 border-purple-300',
      description: 'Explaining concepts through guided discovery',
    },
    debugger: {
      name: 'Debugger',
      icon: '🔍',
      color: 'bg-red-100 text-red-800 border-red-300',
      description: 'Helping you debug through progressive hints',
    },
    hint_provider: {
      name: 'Hint Provider',
      icon: '💭',
      color: 'bg-blue-100 text-blue-800 border-blue-300',
      description: 'Providing hints without giving away the solution',
    },
  }

  const agent = agentInfo[agentType] || {
    name: 'AI Tutor',
    icon: '🤖',
    color: 'bg-gray-100 text-gray-800 border-gray-300',
    description: 'Helping you learn Python',
  }

  return (
    <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg border ${agent.color}`}>
      <span className="text-xl">{agent.icon}</span>
      <div className="flex-1">
        <div className="font-medium text-sm">{agent.name}</div>
        <div className="text-xs opacity-75">{agent.description}</div>
      </div>
      <div className="flex space-x-1">
        <span className="w-2 h-2 bg-current rounded-full animate-pulse" />
        <span className="w-2 h-2 bg-current rounded-full animate-pulse delay-75" />
        <span className="w-2 h-2 bg-current rounded-full animate-pulse delay-150" />
      </div>
    </div>
  )
}
