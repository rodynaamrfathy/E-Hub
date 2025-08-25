import { useEffect, useMemo, useRef, useState } from 'react'
import { Plus, Send, Image as ImageIcon, Trash2, History, Loader2, Paperclip } from 'lucide-react'
import { 
  createConversation, listConversations, deleteConversationApi, 
  getConversationHistory, sendMessageApi, uploadImageWithMessage, getImageHistory 
} from '../../services/api'
import type { ConversationListDTO, MessageHistoryDTO, ImageHistoryDTO } from '../../types'

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
  const [imgHistoryOpen, setImgHistoryOpen] = useState(false)
  const [imageHistory, setImageHistory] = useState<ImageHistoryDTO[] | null>(null)

  const fileRef = useRef<HTMLInputElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

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
    const userMsg: LocalMsg = {
      id: `local-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    scrollToBottom()
    try {
      const res = await sendMessageApi(currentConvId, userMsg.content)
      const botMsg: LocalMsg = {
        id: res.msg_id,
        role: 'assistant',
        content: res.content,
        timestamp: res.created_at
      }
      setMessages(prev => [...prev, botMsg])
    } catch (e) {
      setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: '❌ Failed to reach server.', timestamp: new Date().toISOString() }])
    } finally {
      setLoading(false)
      scrollToBottom()
    }
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

  async function toggleImageHistory(){
    if (imgHistoryOpen){
      setImgHistoryOpen(false)
      return
    }
    try {
      const data = await getImageHistory()
      setImageHistory(data)
    } catch {
      setImageHistory([])
    } finally {
      setImgHistoryOpen(true)
    }
  }

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

        <button onClick={toggleImageHistory} className="mt-3 inline-flex items-center gap-2 text-sm px-3 py-2 rounded-xl border hover:bg-gray-50">
          <History className="w-4 h-4" />
          Upload history
        </button>

        {imgHistoryOpen && (
          <div className="mt-3 border rounded-xl p-2 h-40 overflow-auto">
            {!imageHistory && <div className="text-sm text-gray-500">Loading...</div>}
            {imageHistory && imageHistory.length===0 && <div className="text-sm text-gray-500">No uploads yet.</div>}
            {imageHistory && imageHistory.map(item => (
              <div key={item.image_id} className="text-sm py-1">
                <div className="font-medium">{item.label}</div>
                <div className="text-xs text-gray-500">{new Date(item.created_at).toLocaleString()}</div>
                <div className="text-xs">{item.recycle_instructions}</div>
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Chat Panel */}
      <section className="bg-white rounded-2xl shadow-soft h-[70vh] md:h-[78vh] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-auto p-4 space-y-3">
          {messages.map(m => (
            <div key={m.id} className={`flex ${m.role==='user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl px-3 py-2 ${m.role==='user' ? 'bg-brand text-white' : 'bg-gray-100 text-gray-800'}`}>
                <div className="whitespace-pre-wrap text-sm">{m.content}</div>
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
