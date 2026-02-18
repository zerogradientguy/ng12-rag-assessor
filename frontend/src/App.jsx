import React, { useState } from 'react'
import AssessmentTab from './components/AssessmentTab'
import ChatTab from './components/ChatTab'

export default function App() {
  const [activeTab, setActiveTab] = useState('assessment')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            🏥 NG12 Cancer Risk Assessor
          </h1>
          <p className="text-gray-600 mt-2">
            Clinical decision support powered by NICE NG12 guidelines
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 flex">
          <button
            onClick={() => setActiveTab('assessment')}
            className={`py-4 px-6 font-medium text-sm tab-inactive ${
              activeTab === 'assessment' ? 'tab-active' : ''
            }`}
          >
            📋 Patient Assessment
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`py-4 px-6 font-medium text-sm tab-inactive ${
              activeTab === 'chat' ? 'tab-active' : ''
            }`}
          >
            💬 Chat Assistant
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {activeTab === 'assessment' && <AssessmentTab />}
        {activeTab === 'chat' && <ChatTab />}
      </div>

      {/* Footer */}
      <div className="bg-gray-100 border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-4 text-center text-gray-600 text-sm">
          <p>NG12 Cancer Risk Assessor v1.0 | Powered by Groq API</p>
        </div>
      </div>
    </div>
  )
}
