import React from 'react'
import { useSearchParams, Link } from 'react-router-dom'

export default function DownloadPage() {
  const [searchParams] = useSearchParams()
  const url = searchParams.get('url')

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'Inter, system-ui' }}>
      <h1>Your 3D Video</h1>
      {url ? (
        <>
          <p>Download or preview below.</p>
          <video controls style={{ width: '100%', borderRadius: 8 }} src={url}></video>
          <div style={{ marginTop: 12 }}>
            <a href={url} download>Download MP4</a>
          </div>
        </>
      ) : (
        <p>No URL provided.</p>
      )}
      <div style={{ marginTop: 24 }}>
        <Link to="/">Back to Upload</Link>
      </div>
    </div>
  )
}