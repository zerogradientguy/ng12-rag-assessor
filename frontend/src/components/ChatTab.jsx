import React, { useState, useRef, useEffect } from 'react'

const API_BASE = ''  // Use relative paths; Vite proxy handles routing

// Generate UUID in browser
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

export default function ChatTab() {
  const [sessionId] = useState(() => generateUUID())
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)
    setError(null)

    // Add user message to UI immediately
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      citations: []
    }])

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: userMessage,
          top_k: 5
        }),
      })

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.statusText}`)
      }

      const data = await response.json()

      // Add assistant message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        citations: data.citations || []
      }])
    } catch (err) {
      setError(`Error: ${err.message}`)
      // Remove the user message if there was an error
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  const handleClearChat = async () => {
    if (confirm('Clear chat history?')) {
      try {
        await fetch(`${API_BASE}/chat/${sessionId}`, {
          method: 'DELETE',
        })
        setMessages([])
        setError(null)
      } catch (err) {
        setError(`Error clearing chat: ${err.message}`)
      }
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-300px)] space-y-4">
      {/* Chat Header */}
      <div className="bg-white rounded-lg shadow p-4 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gray-900">NG12 Assistant</h2>
          <p className="text-sm text-gray-600">Ask questions about cancer risk assessment</p>
        </div>
        <button
          onClick={handleClearChat}
          className="text-sm bg-gray-200 hover:bg-gray-300 text-gray-900 px-3 py-1 rounded transition"
        >
          Clear Chat
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 bg-white rounded-lg shadow overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center text-gray-500 text-center">
            <div>
              <p className="text-xl mb-2">👋 Welcome to the NG12 Assistant</p>
              <p>Ask questions about cancer risk assessment and clinical guidelines.</p>
            </div>
          </div>
        )}

        {messages.map((message, idx) => (
          <div
            key={idx}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-gray-100 text-gray-900 rounded-bl-none'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>

              {/* Citations for assistant messages */}
              {message.role === 'assistant' && message.citations && message.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-300 space-y-2">
                  <p className="text-xs font-semibold">Sources:</p>
                  {message.citations.map((citation, cidx) => (
                    <div key={cidx} className="bg-white text-gray-900 text-xs p-2 rounded mt-1">
                      <p className="font-medium">{citation.source} (Page {citation.page})</p>
                      <p className="mt-1 italic text-gray-700">{citation.excerpt}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg rounded-bl-none">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-900 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Input Area */}
      <form onSubmit={handleSendMessage} className="bg-white rounded-lg shadow p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-6 rounded-lg transition"
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
      </form>
    </div>
  )
}
