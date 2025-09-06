import { useEffect, useMemo, useRef, useState } from 'react'
import { Plus, Send, Image as ImageIcon, Trash2, Loader2, Paperclip } from 'lucide-react'
import { 
  createConversation, listConversations, deleteConversationApi, 
  getConversationHistory, sendMessageStream, uploadImageWithMessage
} from '../../services/api'
import type { ConversationListDTO, MessageHistoryDTO } from '../../types'
import ReactMarkdown from "react-markdown"


type LocalMsg = {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  attachments?: { name: string }[]
}

export default function ChatApp() {
  const [conversations, setConversations] = useState<ConversationListDTO[]>([])
  const [currentConvId, setCurrentConvId] = useState<string | null>(null)
  const [messages, setMessages] = useState<LocalMsg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [uploading, setUploading] = useState(false)
  // Image history functionality removed as endpoint doesn't exist in backend

  const fileRef = useRef<HTMLInputElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const currentStreamRef = useRef<{ abort: () => void } | null>(null)

  // Load conversations on mount
  useEffect(() => {
    (async () => {
      const list = await listConversations()
      setConversations(list)
      if (list.length > 0) {
        setCurrentConvId(list[0].conv_id)
      } else {
        // create a first conversation
        setCreating(true)
        const conv = await createConversation('Eco Assistant')
        setCreating(false)
        setConversations([{ conv_id: conv.conv_id, title: conv.title, updated_at: conv.created_at }])
        setCurrentConvId(conv.conv_id)
      }
    })()
  }, [])

  // Cleanup streaming on unmount
  useEffect(() => {
    return () => {
      if (currentStreamRef.current) {
        currentStreamRef.current.abort()
      }
    }
  }, [])

  // Load history whenever current conversation changes
  useEffect(() => {
    if (!currentConvId) return
    (async () => {
      const hist = await getConversationHistory(currentConvId) as MessageHistoryDTO[]
      const mapped: LocalMsg[] = hist.map((m, idx) => ({
        id: `${idx}-${m.timestamp}`,
        role: (m.role as any) ?? 'assistant',
        content: m.content ?? '',
        timestamp: m.timestamp
      }))
      setMessages(mapped)
      scrollToBottom()
    })()
  }, [currentConvId])

  function scrollToBottom(){
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
  }

  async function onNewChat(){
    setCreating(true)
    const conv = await createConversation('Eco Assistant')
    setCreating(false)
    const updated = [{ conv_id: conv.conv_id, title: conv.title, updated_at: conv.created_at }, ...conversations]
    setConversations(updated)
    setCurrentConvId(conv.conv_id)
    setMessages([])
  }

  async function onDeleteChat(convId: string){
    await deleteConversationApi(convId)
    const rest = conversations.filter(c => c.conv_id !== convId)
    setConversations(rest)
    if (currentConvId === convId) {
      if (rest.length) setCurrentConvId(rest[0].conv_id)
      else {
        const conv = await createConversation('Eco Assistant')
        setConversations([{ conv_id: conv.conv_id, title: conv.title, updated_at: conv.created_at }])
        setCurrentConvId(conv.conv_id)
        setMessages([])
      }
    }
  }

  async function onSend(){
    if (!input.trim() || !currentConvId) return
    
    console.log('onSend called with input:', input, 'convId:', currentConvId)
    
    const userMsg: LocalMsg = {
      id: `local-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMsg])
    const userInput = input
    setInput('')
    setLoading(true)
    scrollToBottom()

    // Create a placeholder for the assistant's streaming response
    const assistantMsgId = `assistant-${Date.now()}`
    const assistantMsg: LocalMsg = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, assistantMsg])

    // Use streaming API
    console.log('Starting stream for conversation:', currentConvId, 'with input:', userInput)
    currentStreamRef.current = sendMessageStream(
      currentConvId,
      userInput,
      (token) => {
        console.log('Received token:', token)
        // Update the assistant message with new token
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMsgId 
            ? { ...msg, content: msg.content + token }
            : msg
        ))
        scrollToBottom()
      },
      () => {
        console.log('Streaming completed')
        // Streaming completed
        setLoading(false)
        currentStreamRef.current = null
        scrollToBottom()
      },
      (error) => {
        console.error('Streaming error:', error)
        // Error occurred
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMsgId 
            ? { ...msg, content: `❌ Error: ${error}` }
            : msg
        ))
        setLoading(false)
        currentStreamRef.current = null
        scrollToBottom()
      }
    )
  }

  async function onUpload(files: FileList | null){
    if (!files || !files.length || !currentConvId) return
    setUploading(true)
    for (const file of Array.from(files)){
      // Show a local echo message
      const echo: LocalMsg = {
        id: `upload-${Date.now()}-${file.name}`,
        role: 'user',
        content: `📎 Uploaded: ${file.name}`,
        timestamp: new Date().toISOString(),
        attachments: [{ name: file.name }]
      }
      setMessages(prev => [...prev, echo])
      scrollToBottom()
      try {
        const res = await uploadImageWithMessage(currentConvId, file)
        const reply: LocalMsg = {
          id: `${Date.now()}-reply`,
          role: 'assistant',
          content: typeof res === 'object' && res?.reply ? res.reply : 'Got it! Here is my analysis.',
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, reply])
      } catch (e) {
        setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: `❌ Failed to process ${file.name}.`, timestamp: new Date().toISOString() }])
      }
    }
    setUploading(false)
    if (fileRef.current) fileRef.current.value = ''
  }

  // Image history functionality removed as endpoint doesn't exist in backend

  return (
    <div className="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-4">
      {/* Sidebar */}
      <aside className="bg-white rounded-2xl shadow-soft p-3 h-[70vh] md:h-[78vh] flex flex-col">
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-semibold">Conversations</h2>
          <button onClick={onNewChat} className="inline-flex items-center gap-1 text-white bg-brand hover:brightness-95 px-3 py-1.5 rounded-xl text-sm disabled:opacity-50" disabled={creating}>
            {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            New
          </button>
        </div>
        <div className="flex-1 overflow-auto space-y-1">
          {conversations.map(c => (
            <div key={c.conv_id} className={`group rounded-xl border p-2 cursor-pointer ${currentConvId===c.conv_id ? 'border-brand/60 bg-emerald-50' : 'hover:bg-gray-50'}`} onClick={() => setCurrentConvId(c.conv_id)}>
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="font-medium truncate">{c.title ?? 'Conversation'}</div>
                  <div className="text-xs text-gray-500">{new Date(c.updated_at).toLocaleString()}</div>
                </div>
                <button className="opacity-0 group-hover:opacity-100 transition text-red-600 hover:bg-red-50 rounded p-1" onClick={(e) => { e.stopPropagation(); onDeleteChat(c.conv_id); }}>
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
          {conversations.length===0 && <div className="text-sm text-gray-500">No conversations yet.</div>}
        </div>

        {/* Image history functionality removed as endpoint doesn't exist in backend */}
      </aside>

      {/* Chat Panel */}
      <section className="bg-white rounded-2xl shadow-soft h-[70vh] md:h-[78vh] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-auto p-4 space-y-3">
        {messages.map(m => (
            <div key={m.id} className={`flex ${m.role==='user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl px-3 py-2 ${m.role==='user' ? 'bg-brand text-white' : 'bg-gray-100 text-gray-800'}`}>
                
                {/* ✅ Render markdown instead of raw text */}
                <div className="prose prose-sm max-w-none text-sm">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>

                {!!m.attachments?.length && (
                  <div className="mt-2 flex gap-2 text-xs opacity-80">
                    {m.attachments.map((a, i) => (
                      <span key={i} className="inline-flex items-center gap-1 bg-black/10 rounded px-2 py-0.5">
                        <Paperclip className="w-3 h-3" />
                        {a.name}
                      </span>
                    ))}
                  </div>
                )}
                <div className="text-[10px] opacity-60 mt-1">{new Date(m.timestamp).toLocaleTimeString()}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-800 px-3 py-2 rounded-2xl inline-flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> typing…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Composer */}
        <div className="border-t p-3">
          <div className="flex items-stretch gap-2">
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => onUpload(e.target.files)}
              className="hidden"
            />
            <button
              onClick={() => fileRef.current?.click()}
              className="px-3 rounded-xl border hover:bg-gray-50"
              disabled={uploading || !currentConvId}
              title="Upload image"
            >
              {uploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ImageIcon className="w-5 h-5" />}
            </button>

            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key==='Enter') onSend() }}
              placeholder="Ask about sustainability or recycling…"
              className="flex-1 px-3 py-2 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
              disabled={!currentConvId}
            />
            <button
              onClick={onSend}
              className="inline-flex items-center gap-2 bg-brand hover:brightness-95 text-white px-4 rounded-xl disabled:opacity-50"
              disabled={!input.trim() || !currentConvId || loading}
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}
