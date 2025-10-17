import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function UploadForm() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle') // idle|uploading|processing|done|error
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setMessage('Please select an MP4 file')
      return
    }
    setStatus('uploading')
    setMessage('Uploading...')
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData
      })
      if (!res.ok) {
        throw new Error(`Upload failed: ${res.status}`)
      }
      setStatus('processing')
      const data = await res.json()
      setStatus('done')
      navigate(`/download?url=${encodeURIComponent(data.download_url)}`)
    } catch (err) {
      console.error(err)
      setStatus('error')
      setMessage(err.message || 'Error processing video')
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'Inter, system-ui' }}>
      <h1>AI 2D→3D Video Prototype</h1>
      <p>Upload an 8-second MP4 and get a 3D recomposed video.</p>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="video/mp4"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <div style={{ marginTop: 12 }}>
          <button type="submit" disabled={status === 'uploading' || status === 'processing'}>
            {status === 'uploading' ? 'Uploading...' : status === 'processing' ? 'Processing...' : 'Upload'}
          </button>
        </div>
      </form>
      {status !== 'idle' && (
        <div style={{ marginTop: 16 }}>
          <progress max="100" value={status === 'uploading' ? 33 : status === 'processing' ? 66 : status === 'done' ? 100 : 0}></progress>
          <div style={{ marginTop: 8 }}>{message}</div>
        </div>
      )}
    </div>
  )
}