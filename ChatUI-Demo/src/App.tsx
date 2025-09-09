import { useEffect, useState } from 'react'
import ChatApp from './components/chat/ChatApp'
import { Activity, Leaf } from 'lucide-react'
import { getStatus } from './services/api'

export default function App() {
  const [online, setOnline] = useState<boolean | null>(null)

  useEffect(() => {
    (async () => {
      try {
        await getStatus()
        setOnline(true)
      } catch {
        setOnline(false)
      }
    })()
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur border-b">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Leaf className="w-5 h-5 text-brand" />
            <h1 className="font-semibold">Dawar • Eco Assistant</h1>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Activity className={`w-4 h-4 ${online ? 'text-emerald-500' : online===false ? 'text-red-500' : 'text-gray-400'}`} />
            <span className={`${online ? 'text-emerald-600' : online===false ? 'text-red-600' : 'text-gray-500'}`}>
              {online===null ? 'Checking...' : online ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </header>
      <main className="flex-1">
        <div className="max-w-5xl mx-auto p-4">
          <ChatApp />
        </div>
      </main>
      <footer className="border-t">
        <div className="max-w-5xl mx-auto px-4 py-3 text-sm text-gray-500">
          Built with ❤️ for sustainability.
        </div>
      </footer>
    </div>
  )
}
