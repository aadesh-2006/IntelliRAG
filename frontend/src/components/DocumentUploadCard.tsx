import React, { useState, useRef } from 'react'
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { uploadDocument, DocumentType } from '../api/documents'

interface DocumentUploadCardProps {
  onUploadSuccess: () => void
}

const DOCUMENT_TYPES: { value: DocumentType; label: string }[] = [
  { value: 'GENERAL', label: 'General Document' },
  { value: 'INVOICE', label: 'Financial Invoice' },
  { value: 'BALANCE_SHEET', label: 'Balance Sheet' },
  { value: 'P_AND_L', label: 'Profit & Loss Statement' },
  { value: 'CRICKET_BROCHURE', label: 'Cricket Tournament Brochure' },
]

export const DocumentUploadCard: React.FC<DocumentUploadCardProps> = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [documentType, setDocumentType] = useState<DocumentType>('GENERAL')
  const [isDragging, setIsDragging] = useState<boolean>(false)
  const [isUploading, setIsUploading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
      setError(null)
      setSuccessMsg(null)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0])
      setError(null)
      setSuccessMsg(null)
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) {
      setError('Please select a file to upload')
      return
    }

    setIsUploading(true)
    setError(null)
    setSuccessMsg(null)

    try {
      await uploadDocument(selectedFile, documentType)
      setSuccessMsg(`"${selectedFile.name}" uploaded successfully.`)
      setSelectedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      onUploadSuccess()
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to upload document')
      }
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 sm:p-8 backdrop-blur-sm shadow-xl shadow-slate-950/50">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
          <UploadCloud className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white tracking-tight">Upload Document</h3>
          <p className="text-xs text-slate-400">Securely store multimodal documents in the isolated storage pipeline</p>
        </div>
      </div>

      <form onSubmit={handleUpload} className="space-y-5">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
            isDragging
              ? 'border-indigo-500 bg-indigo-500/5 ring-4 ring-indigo-500/10'
              : 'border-slate-700/70 hover:border-slate-600 bg-slate-950/40 hover:bg-slate-950/60'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileChange}
            className="hidden"
            accept=".pdf,.txt,.csv,.docx,.json,.png,.jpg,.jpeg,.tiff,.bmp,.webp,.md"
          />

          <div className="flex flex-col items-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-slate-800/80 flex items-center justify-center text-slate-400">
              <FileText className="w-6 h-6" />
            </div>
            {selectedFile ? (
              <div>
                <p className="text-sm font-semibold text-indigo-400">{selectedFile.name}</p>
                <p className="text-xs text-slate-400 mt-0.5">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            ) : (
              <div>
                <p className="text-sm font-medium text-slate-300">
                  <span className="text-indigo-400 hover:underline">Click to browse</span> or drag & drop a document here
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Supported formats: PDF, DOCX, TXT, CSV, JSON, PNG, JPG, WEBP, TIFF, MD (Max 50MB)
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Document Classification
            </label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value as DocumentType)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 transition-colors"
            >
              {DOCUMENT_TYPES.map((dt) => (
                <option key={dt.value} value={dt.value} className="bg-slate-900 text-slate-200">
                  {dt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={isUploading || !selectedFile}
              className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold shadow-lg shadow-indigo-600/20 transition-all duration-200 flex items-center justify-center space-x-2"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <UploadCloud className="w-4 h-4" />
                  <span>Upload</span>
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="flex items-center space-x-2 p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="flex items-center space-x-2 p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 text-xs">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>{successMsg}</span>
          </div>
        )}
      </form>
    </div>
  )
}
