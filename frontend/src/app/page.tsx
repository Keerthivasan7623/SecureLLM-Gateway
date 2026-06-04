"use client"

import { useState, useRef, useEffect } from "react"
import { Shield, ShieldAlert, ShieldCheck, Send, Settings, Activity, Server, AlertTriangle } from "lucide-react"

type Message = {
  id: string
  role: "user" | "ai" | "system"
  content: string
  timestamp: string
  status?: "ALLOWED" | "WARN" | "BLOCKED" | "BLOCKED_OUTPUT" | "PENDING" | "ERROR"
  overall_score?: number
  category_scores?: Record<string, number>
  provider?: string
}

export default function GuardrailGateway() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [apiKey, setApiKey] = useState(process.env.NEXT_PUBLIC_GEMINI_API_KEY || "")
  const [provider, setProvider] = useState("gemini")
  const [showSettings, setShowSettings] = useState(false)
  const [loading, setLoading] = useState(false)
  const [sessionStats, setSessionStats] = useState({ total: 0, allowed: 0, blocked: 0, avgRisk: 0 })
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || !apiKey) {
        if (!apiKey) alert("Please enter an API Key in settings first.")
        return
    }

    const newMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString(),
      status: "PENDING"
    }

    setMessages(prev => [...prev, newMessage])
    setInput("")
    setLoading(true)

    try {
      // Connect to FastAPI backend
      const res = await fetch("http://localhost:8000/api/v1/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: newMessage.content,
          provider: provider,
          api_key: apiKey
        })
      })
      
      const data = await res.json()
      
      // Update the user message with the scan result
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id ? { 
            ...msg, 
            status: data.decision, 
            overall_score: data.overall_score, 
            category_scores: data.category_scores,
            provider: provider 
        } : msg
      ))

      // Update session stats
      setSessionStats(prev => {
        const newTotal = prev.total + 1
        const newBlocked = data.decision === "BLOCK" ? prev.blocked + 1 : prev.blocked
        const newAllowed = data.decision !== "BLOCK" ? prev.allowed + 1 : prev.allowed
        const newAvg = ((prev.avgRisk * prev.total) + (data.overall_score || 0)) / newTotal
        return { total: newTotal, allowed: newAllowed, blocked: newBlocked, avgRisk: Math.round(newAvg) }
      })

      // Add AI response or Block response
      const responseMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: data.decision === "BLOCK" ? "system" : "ai",
        content: data.decision === "BLOCK" ? `BLOCKED: ${data.message || "Threat Detected"}` : data.llm_response,
        timestamp: new Date().toLocaleTimeString(),
        status: data.status,
      }

      setMessages(prev => [...prev, responseMsg])

    } catch (error) {
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id ? { ...msg, status: "ERROR" } : msg
      ))
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: "system",
        content: "Network error connecting to Guardrail Gateway.",
        timestamp: new Date().toLocaleTimeString(),
        status: "ERROR"
      }])
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score?: number) => {
    if (score === undefined) return "text-gray-400"
    if (score <= 30) return "text-emerald-500"
    if (score <= 60) return "text-yellow-500"
    return "text-rose-500"
  }

  const getScoreBarColor = (score: number) => {
    if (score <= 30) return "bg-emerald-500"
    if (score <= 60) return "bg-yellow-500"
    return "bg-rose-500"
  }

  // Get the latest scan result for the dashboard
  const latestUserMsg = [...messages].reverse().find(m => m.role === "user" && m.overall_score !== undefined)
  const latestScores = latestUserMsg?.category_scores || {
    prompt_injection: 0, jailbreak: 0, cyber_abuse: 0, fraud: 0, privacy: 0, harmful: 0, ai_abuse: 0
  }
  const currentRisk = latestUserMsg?.overall_score || 0

  return (
    <div className="min-h-screen bg-[#050505] text-gray-100 font-sans flex flex-col h-screen overflow-hidden">
      
      {/* Header */}
      <header className="border-b border-white/10 bg-white/5 backdrop-blur-md px-6 py-4 flex justify-between items-center z-10">
        <div className="flex items-center gap-3">
          <Shield className="text-emerald-500 w-6 h-6" />
          <h1 className="font-semibold text-lg tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            AI Guardrail Gateway <span className="text-xs text-emerald-500 font-mono ml-2 border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 rounded-full">v2.4</span>
          </h1>
        </div>
        <button 
          onClick={() => setShowSettings(!showSettings)}
          className="p-2 hover:bg-white/10 rounded-full transition-colors"
          aria-label="Settings"
        >
          <Settings className="w-5 h-5 text-gray-400" />
        </button>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Sidebar - Dashboard */}
        <div className="w-80 border-r border-white/10 bg-[#0a0a0a] flex flex-col overflow-y-auto hidden md:flex">
          <div className="p-6 border-b border-white/10">
            <h2 className="text-sm font-medium text-gray-400 flex items-center gap-2 mb-4">
              <Activity className="w-4 h-4" /> Live Risk Assessment
            </h2>
            
            {/* Overall Score Gauge */}
            <div className="flex flex-col items-center justify-center p-6 bg-white/5 rounded-2xl border border-white/5 mb-6 relative overflow-hidden">
              <div className="text-5xl font-light tracking-tighter mb-1 relative z-10">
                <span className={getScoreColor(currentRisk)}>{currentRisk}</span>
                <span className="text-lg text-gray-500">/100</span>
              </div>
              <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold z-10">Overall Risk Score</div>
              
              {/* Background glow based on score */}
              <div className={`absolute -bottom-10 w-full h-20 blur-3xl opacity-20 ${currentRisk > 60 ? 'bg-rose-500' : currentRisk > 30 ? 'bg-yellow-500' : 'bg-emerald-500'}`}></div>
            </div>

            {/* Session Analytics */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                <div className="text-2xl font-light">{sessionStats.total}</div>
                <div className="text-xs text-gray-500">Total Scans</div>
              </div>
              <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                <div className="text-2xl font-light text-rose-500">{sessionStats.blocked}</div>
                <div className="text-xs text-gray-500">Blocked Threats</div>
              </div>
            </div>

            {/* Category Bars */}
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Threat Vectors</h3>
            <div className="space-y-4">
              {Object.entries(latestScores).map(([category, score]) => (
                <div key={category}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-300 capitalize">{category.replace('_', ' ')}</span>
                    <span className="text-gray-500">{score}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${getScoreBarColor(score)}`}
                      style={{ width: `${score}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center - Chat Interface */}
        <div className="flex-1 flex flex-col relative bg-[#111]">
          
          {/* Settings Overlay */}
          {showSettings && (
            <div className="absolute top-0 w-full bg-blue-900/20 backdrop-blur-xl border-b border-blue-500/20 p-6 z-20 shadow-2xl">
              <div className="max-w-2xl mx-auto flex flex-col sm:flex-row gap-4 items-end">
                <div className="flex-1 w-full">
                  <label className="block text-xs text-blue-300 mb-1 uppercase tracking-wider font-semibold">LLM Provider</label>
                  <select 
                    className="w-full bg-black/40 border border-blue-500/30 text-white rounded-lg p-2.5 outline-none focus:border-blue-500 transition-colors"
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                  >
                    <option value="openai">OpenAI (GPT-4o Mini)</option>
                    <option value="gemini">Google (Gemini 1.5)</option>
                  </select>
                </div>
                <div className="flex-1 w-full">
                  <label className="block text-xs text-blue-300 mb-1 uppercase tracking-wider font-semibold">API Key</label>
                  <input 
                    type="password" 
                    className="w-full bg-black/40 border border-blue-500/30 text-white rounded-lg p-2.5 outline-none focus:border-blue-500 transition-colors"
                    placeholder="sk-..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                  />
                </div>
                <button 
                  onClick={() => setShowSettings(false)}
                  className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-lg font-medium transition-colors h-[42px] whitespace-nowrap"
                >
                  Save & Connect
                </button>
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 pb-32">
            <div className="max-w-3xl mx-auto space-y-6">
              
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-[50vh] text-center opacity-50">
                  <ShieldCheck className="w-16 h-16 mb-4 text-emerald-500" />
                  <h2 className="text-xl font-medium text-white mb-2">Zero-Trust AI Gateway Active</h2>
                  <p className="max-w-md text-sm">Every prompt is analyzed by the 4-stage ML engine before reaching the provider. Set your API key and send a message to begin.</p>
                </div>
              )}

              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl p-4 ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-br-sm shadow-lg shadow-blue-900/20' 
                      : msg.role === 'system'
                      ? 'bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-bl-sm'
                      : 'bg-white/5 border border-white/10 text-gray-200 rounded-bl-sm'
                  }`}>
                    
                    {/* User Prompt Guardrail Badge */}
                    {msg.role === 'user' && msg.status && msg.status !== 'PENDING' && (
                      <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/20 text-xs font-mono">
                        {msg.status === 'ALLOW' ? <ShieldCheck className="w-3 h-3 text-emerald-300" /> : <AlertTriangle className="w-3 h-3 text-rose-300" />}
                        <span className="opacity-80">Score: {msg.overall_score}</span>
                        <span className="opacity-50">|</span>
                        <span className="opacity-80 capitalize">{msg.provider}</span>
                      </div>
                    )}

                    {/* Message Content */}
                    <div className="leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                    
                    <div className="text-[10px] opacity-40 mt-2 flex justify-between">
                      <span>{msg.timestamp}</span>
                      {msg.status === 'PENDING' && <span className="animate-pulse flex items-center gap-1"><Server className="w-3 h-3"/> Scanning...</span>}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white/5 border border-white/10 rounded-2xl rounded-bl-sm p-4 text-sm text-gray-400 flex items-center gap-2 animate-pulse">
                    <ShieldAlert className="w-4 h-4 text-yellow-500" /> Inspecting payload & waiting for AI...
                  </div>
                </div>
              )}
              
              <div ref={chatEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="absolute bottom-0 w-full bg-gradient-to-t from-[#111] via-[#111] to-transparent pt-10 pb-6 px-4">
            <div className="max-w-3xl mx-auto relative">
              <textarea
                className="w-full bg-[#1a1a1a] border border-white/10 rounded-2xl py-4 pl-4 pr-14 text-white focus:outline-none focus:border-blue-500/50 resize-none shadow-2xl shadow-black"
                placeholder="Type a prompt to test the guardrail..."
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
                style={{ minHeight: '56px', maxHeight: '150px' }}
              />
              <button 
                className={"absolute right-2 top-2 p-2 rounded-xl transition-colors " + (input.trim() ? "bg-blue-600 hover:bg-blue-500 text-white" : "bg-white/5 text-gray-500 cursor-not-allowed")}
                onClick={handleSend}
                disabled={!input.trim() || loading}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <div className="text-center mt-2 text-[10px] text-gray-500">
              Secured by AI Guardrail Gateway v2.4 • Zero-Trust Engine Active
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
