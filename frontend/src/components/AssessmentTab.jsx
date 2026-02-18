import React, { useState, useEffect } from 'react'

const API_BASE = ''  // Use relative paths; Vite proxy handles routing

const RISK_COLORS = {
  'Routine GP Screening': 'bg-green-100 border-green-400 text-green-900',
  'Urgent Referral': 'bg-yellow-100 border-yellow-400 text-yellow-900',
  'Same-Day Referral': 'bg-red-100 border-red-400 text-red-900'
}

export default function AssessmentTab() {
  const [patients, setPatients] = useState([])
  const [selectedPatientId, setSelectedPatientId] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Load patients on mount
  useEffect(() => {
    fetchPatients()
  }, [])

  const fetchPatients = async () => {
    try {
      const response = await fetch(`${API_BASE}/patients`)
      if (!response.ok) throw new Error('Failed to fetch patients')
      const data = await response.json()
      setPatients(data)
      if (data.length > 0) {
        setSelectedPatientId(data[0].patient_id)
      }
    } catch (err) {
      setError(`Error loading patients: ${err.message}`)
    }
  }

  const handleAssess = async () => {
    if (!selectedPatientId) {
      setError('Please select a patient')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ patient_id: selectedPatientId }),
      })

      if (!response.ok) {
        throw new Error(`Assessment failed: ${response.statusText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Patient Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Select Patient</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patient ID
            </label>
            <select
              value={selectedPatientId}
              onChange={(e) => setSelectedPatientId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">-- Select a patient --</option>
              {patients.map((patient) => (
                <option key={patient.patient_id} value={patient.patient_id}>
                  {patient.name} ({patient.patient_id}) - Age {patient.age}
                </option>
              ))}
            </select>
          </div>

          {selectedPatientId && patients.find(p => p.patient_id === selectedPatientId) && (
            <div className="bg-gray-50 p-4 rounded-lg">
              {(() => {
                const patient = patients.find(p => p.patient_id === selectedPatientId)
                return (
                  <>
                    <div className="text-sm text-gray-700">
                      <p><strong>Symptoms:</strong> {patient.symptoms.join(', ')}</p>
                    </div>
                  </>
                )
              })()}
            </div>
          )}

          <button
            onClick={handleAssess}
            disabled={loading || !selectedPatientId}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition"
          >
            {loading ? '⏳ Assessing...' : '🔍 Assess Patient'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-900 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="assessment-result">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Assessment Result</h2>

          {/* Patient Info */}
          <div className="mb-6 pb-6 border-b border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Patient:</span>
                <p className="text-gray-900">{result.patient_name} ({result.patient_id})</p>
              </div>
              <div>
                <span className="font-medium text-gray-700">Age:</span>
                <p className="text-gray-900">{result.age}</p>
              </div>
              <div className="col-span-2">
                <span className="font-medium text-gray-700">Symptoms:</span>
                <p className="text-gray-900">{result.symptoms.join(', ')}</p>
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="mb-6 pb-6 border-b border-gray-200">
            <h3 className="font-bold text-gray-900 mb-3">Recommendation</h3>
            <div className={`border-2 rounded-lg p-4 ${RISK_COLORS[result.recommendation] || 'bg-gray-100'}`}>
              <p className="text-lg font-bold">{result.recommendation}</p>
            </div>
          </div>

          {/* Reasoning */}
          <div className="mb-6 pb-6 border-b border-gray-200">
            <h3 className="font-bold text-gray-900 mb-2">Clinical Reasoning</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{result.reasoning}</p>
          </div>

          {/* Citations */}
          {result.citations && result.citations.length > 0 && (
            <div>
              <h3 className="font-bold text-gray-900 mb-3">Guidelines References</h3>
              <div className="space-y-3">
                {result.citations.map((citation, idx) => (
                  <div key={idx} className="citation-card">
                    <p className="text-sm font-medium text-gray-900">
                      {citation.source} - Page {citation.page}
                    </p>
                    <p className="text-sm text-gray-700 mt-2">{citation.excerpt}</p>
                    <p className="text-xs text-gray-500 mt-1">Chunk ID: {citation.chunk_id}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
