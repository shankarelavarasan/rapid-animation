import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import UploadForm from './upload_form.jsx'
import DownloadPage from './download_page.jsx'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadForm />} />
        <Route path="/download" element={<DownloadPage />} />
      </Routes>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')).render(<App />)