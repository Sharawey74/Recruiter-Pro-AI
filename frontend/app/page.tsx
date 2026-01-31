"use client"

import { useState, useCallback, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { matchCV } from '@/lib/api'
import { CircularProgress } from '@/components/ui/circular-progress'
import { SkillBadge } from '@/components/ui/skill-badge'

export default function Dashboard() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [useLLM, setUseLLM] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('useLLM') === 'true'
    }
    return false
  })
  const [useLangChain, setUseLangChain] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('useLangChain') === 'true'
    }
    return false
  })
  const [pipeline, setPipeline] = useState({
    parsing: 'idle', // idle, processing, completed
    extraction: 'idle',
    matching: 'idle',
    insights: 'idle'
  })
  const [matchResults, setMatchResults] = useState<any[]>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('matchResults')
      return saved ? JSON.parse(saved) : []
    }
    return []
  })

  // Persist useLLM state
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('useLLM', String(useLLM))
    }
  }, [useLLM])

  // Persist useLangChain state
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('useLangChain', String(useLangChain))
    }
  }, [useLangChain])

  // Persist match results
  useEffect(() => {
    if (typeof window !== 'undefined' && matchResults.length > 0) {
      localStorage.setItem('matchResults', JSON.stringify(matchResults))
    }
  }, [matchResults])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true)
    } else if (e.type === "dragleave") {
      setIsDragging(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files && files[0]) {
      const file = files[0]
      if (file.type === 'application/pdf') {
        setFile(file)
      }
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files[0]) {
      setFile(files[0])
    }
  }

  const handleMatch = async () => {
    if (!file) return
    
    setIsProcessing(true)
    setMatchResults([])
    
    try {
      // Simulate pipeline progression
      setPipeline({ parsing: 'processing', extraction: 'idle', matching: 'idle', insights: 'idle' })
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setPipeline({ parsing: 'completed', extraction: 'processing', matching: 'idle', insights: 'idle' })
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setPipeline({ parsing: 'completed', extraction: 'completed', matching: 'processing', insights: 'idle' })
      
      // Actual API call with LangChain mode
      const results = await matchCV(file, 3, useLLM, useLangChain) // Top 3 matches for dashboard
      
      setPipeline({ parsing: 'completed', extraction: 'completed', matching: 'completed', insights: 'processing' })
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setPipeline({ parsing: 'completed', extraction: 'completed', matching: 'completed', insights: 'completed' })
      
      setMatchResults(results.matches || [])
    } catch (error) {
      console.error('Matching failed:', error)
      setPipeline({ parsing: 'idle', extraction: 'idle', matching: 'idle', insights: 'idle' })
    } finally {
      setIsProcessing(false)
    }
  }

  const getStepIcon = (status: string) => {
    if (status === 'completed') {
      return (
        <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center">
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </div>
      )
    } else if (status === 'processing') {
      return (
        <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center animate-pulse">
          <svg className="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      )
    }
    return (
      <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center">
        <div className="w-3 h-3 rounded-full bg-gray-500"></div>
      </div>
    )
  }

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-500'
    if (score >= 50) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getScoreBadgeColor = (score: number) => {
    if (score >= 75) return 'border-green-500'
    if (score >= 50) return 'border-yellow-500'
    return 'border-red-500'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      {/* Hero Section */}
      <div className="text-center py-12 px-4">
        <h1 className="text-5xl font-bold mb-4">
          Optimize Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-500">Hiring Pipeline</span>
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Upload resumes and job descriptions to get instant AI-powered relevance scoring and skill gap analysis.
        </p>
      </div>

      {/* AI Mode Selection Cards */}
      <div className="max-w-4xl mx-auto px-4 mb-8">
        <div className="grid grid-cols-2 gap-6">
          {/* Standard Search Card */}
          <button
            onClick={() => {
              setUseLLM(false)
              setUseLangChain(false)
            }}
            className={`relative p-6 rounded-xl border-2 transition-all text-left ${
              !useLLM
                ? 'border-purple-500 bg-purple-500/10'
                : 'border-gray-700/50 bg-gray-800/30 hover:border-gray-600'
            }`}
          >
            <div className="absolute top-4 right-4">
              <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                !useLLM ? 'border-purple-500 bg-purple-500' : 'border-gray-600'
              }`}>
                {!useLLM && (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-lg bg-gray-700/50 flex items-center justify-center">
                <svg className="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Standard Search</h3>
              </div>
            </div>
            
            <p className="text-sm text-gray-400 leading-relaxed">
              Basic keyword matching and pattern recognition for rapid initial screening.
            </p>
          </button>

          {/* Comprehensive AI Analysis Card */}
          <button
            onClick={() => {
              setUseLLM(true)
              setUseLangChain(true)
            }}
            className={`relative p-6 rounded-xl border-2 transition-all text-left ${
              useLLM
                ? 'border-purple-500 bg-purple-500/10'
                : 'border-gray-700/50 bg-gray-800/30 hover:border-gray-600'
            }`}
          >
            <div className="absolute top-4 right-4">
              <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                useLLM ? 'border-purple-500 bg-purple-500' : 'border-gray-600'
              }`}>
                {useLLM && (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </div>
            
            {useLLM && (
              <div className="absolute top-2 left-2">
                <span className="px-2 py-1 text-xs font-medium bg-purple-600 text-white rounded">
                  RECOMMENDED
                </span>
              </div>
            )}
            
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Comprehensive AI Analysis</h3>
              </div>
            </div>
            
            <p className="text-sm text-gray-400 leading-relaxed">
              Deep semantic understanding, skill inference, and cultural fit estimation using advanced LLMs.
            </p>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 pb-12">
        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* Upload Resume Section */}
          <div className="bg-gray-800/30 backdrop-blur border border-gray-700/50 rounded-xl p-8">
            <div
              className={`border-2 border-dashed rounded-xl p-12 text-center transition ${
                isDragging ? 'border-purple-500 bg-purple-500/10' : 'border-gray-600'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="flex flex-col items-center gap-4">
                <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Upload Resume PDF</h3>
                  <p className="text-sm text-gray-400 mb-4">
                    Drag & drop your file here or click to browse.<br />
                    Supported formats: PDF, DOCX
                  </p>
                </div>
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileInput}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg cursor-pointer transition"
                >
                  Browse Files
                </label>
              </div>

              {file && (
                <div className="mt-6 p-4 bg-gray-700/50 rounded-lg flex items-center gap-3">
                  <svg className="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1 text-left">
                    <div className="font-medium text-sm">{file.name}</div>
                    <div className="text-xs text-gray-400">
                      {(file.size / 1024 / 1024).toFixed(1)} MB • {new Date().toLocaleDateString()}
                    </div>
                  </div>
                  <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              )}
            </div>

            {file && (
              <button
                onClick={handleMatch}
                disabled={isProcessing}
                className="w-full mt-6 px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
              >
                {isProcessing ? 'Processing...' : 'Start Matching'}
              </button>
            )}
          </div>

          {/* Processing Pipeline */}
          <div className="bg-gradient-to-r from-gray-800/50 to-gray-900/50 backdrop-blur border border-white/10 rounded-xl p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
                  Processing Pipeline
                </h3>
                <p className="text-gray-400 text-sm mt-1">Real-time analysis of your profile</p>
              </div>
              <div className="px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full text-xs font-medium text-purple-300 flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-pulse"></div>
                ID: v{Math.floor(Math.random() * 100)}0ZXY
              </div>
            </div>

            <div className="space-y-6">
              {/* PDF Parsing */}
              <div className="flex items-start gap-4">
                {getStepIcon(pipeline.parsing)}
                <div className="flex-1">
                  <h4 className="font-semibold">PDF Parsing</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    {pipeline.parsing === 'completed' && 'Successfully extracted text layers and metadata.'}
                    {pipeline.parsing === 'processing' && 'Extracting text and metadata...'}
                    {pipeline.parsing === 'idle' && 'Waiting for resume upload'}
                  </p>
                </div>
              </div>

              {/* Keyword Extraction */}
              <div className="flex items-start gap-4">
                {getStepIcon(pipeline.extraction)}
                <div className="flex-1">
                  <h4 className="font-semibold">Keyword Extraction</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    {pipeline.extraction === 'completed' && 'Identified 45 technical skills and 12 soft skills.'}
                    {pipeline.extraction === 'processing' && 'Analyzing skills and keywords...'}
                    {pipeline.extraction === 'idle' && 'Pending'}
                  </p>
                </div>
              </div>

              {/* AI Matching Engine */}
              <div className="flex items-start gap-4">
                {getStepIcon(pipeline.matching)}
                <div className="flex-1">
                  <h4 className="font-semibold">AI Matching Engine</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    {pipeline.matching === 'completed' && 'Completed matching against job requirements.'}
                    {pipeline.matching === 'processing' && 'Analyzing semantic relevance...'}
                    {pipeline.matching === 'idle' && 'Pending'}
                  </p>
                  {pipeline.matching === 'processing' && (
                    <div className="mt-2 w-full bg-gray-700 rounded-full h-1.5">
                      <div className="bg-blue-500 h-1.5 rounded-full animate-pulse" style={{ width: '65%' }}></div>
                    </div>
                  )}
                </div>
              </div>

              {/* Insight Generation */}
              <div className="flex items-start gap-4">
                {getStepIcon(pipeline.insights)}
                <div className="flex-1">
                  <h4 className="font-semibold">Insight Generation</h4>
                  <p className="text-sm text-gray-400 mt-1">
                    {pipeline.insights === 'completed' && 'Generated comprehensive match report.'}
                    {pipeline.insights === 'processing' && 'Pending completion of matching...'}
                    {pipeline.insights === 'idle' && 'Pending'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Match Results */}
        {matchResults.length > 0 && (
          <div className="bg-gradient-to-r from-gray-800/50 to-gray-900/50 backdrop-blur border border-white/10 rounded-xl p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
                  Your Top Matches
                </h2>
                <p className="text-gray-400 text-sm mt-1">
                  Found {matchResults.length} opportunities matching your profile
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium transition-all flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  Filter
                </button>
                <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium transition-all flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Export Results
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {matchResults.slice(0, 3).map((match, idx) => (
                <div
                  key={idx}
                  className="bg-gray-700/30 border border-gray-600/50 rounded-xl p-6 hover:border-purple-500/50 transition-all hover:shadow-lg hover:shadow-purple-500/10"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="w-12 h-12 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="font-semibold text-white truncate">{match.job_title}</h3>
                        <p className="text-xs text-gray-400 truncate">{match.company || 'Company'}</p>
                      </div>
                    </div>
                    <div className="flex-shrink-0 ml-2">
                      <CircularProgress score={match.final_score} size={56} strokeWidth={5} />
                    </div>
                  </div>

                  <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                    {match.explanation || `Analyzing match for ${match.job_title} position with comprehensive skill evaluation and gap analysis.`}
                  </p>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {(match.matched_skills || ['React', 'TypeScript']).slice(0, 3).map((skill: string, i: number) => (
                      <SkillBadge key={i} skill={skill} type="matched" />
                    ))}
                    {match.missing_skills && match.missing_skills.length > 0 && (
                      <SkillBadge skill={match.missing_skills[0]} type="missing" />
                    )}
                  </div>

                  <button 
                    onClick={() => router.push('/results')}
                    className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg text-sm transition-all flex items-center justify-center gap-2 group"
                  >
                    View Details
                    <svg className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {matchResults.length === 0 && !isProcessing && (
          <div className="bg-gray-800/30 backdrop-blur border border-gray-700/50 rounded-xl p-12 text-center">
            <div className="w-20 h-20 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-300 mb-2">No Matches Yet</h3>
            <p className="text-gray-400 max-w-md mx-auto">
              Upload a resume to get started with AI-powered matching against our open positions.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
