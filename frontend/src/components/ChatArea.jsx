import { useState, useRef, useEffect } from 'react'

export default function ChatArea({ messages, onSend, loading, conversation }) {
  const [input, setInput] = useState('')
  const [selectedImage, setSelectedImage] = useState(null)
  const bottomRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(()=>{ bottomRef.current?.scrollIntoView({behavior:'smooth'}) }, [messages, loading])

  const handleSend = () => {
    if ((!input.trim() && !selectedImage) || loading) return
    
    // Agar image hai to uska naam bhi bhejo
    let finalMessage = input.trim()
    if (selectedImage) {
      finalMessage = finalMessage ? `${finalMessage} [Image attached]` : "Please describe this image"
    }
    
    onSend(finalMessage)
    setInput('')
    setSelectedImage(null)
  }

  const handleImageSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (ev) => setSelectedImage(ev.target.result)
      reader.readAsDataURL(file)
    }
  }

  // Image generation - agar user "generate image of cat" bole
  const isImageGenRequest = (text) => {
    return text.toLowerCase().includes("generate image") || text.toLowerCase().includes("create image") || text.toLowerCase().includes("image of")
  }

  const getImageUrl = (prompt) => {
    const cleanPrompt = prompt.replace(/generate image of|create image of|image of/gi, "").trim()
    return `https://image.pollinations.ai/prompt/${encodeURIComponent(cleanPrompt)}?width=512&height=512&nologo=true`
  }

  return (
    <div className="flex-1 flex flex-col bg-[#212121] h-screen">
      {/* Header with Logo */}
      <div className="bg-[#171717] p-3 flex items-center gap-3 border-b border-zinc-800">
        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold">M</div>
        <div>
          <div className="text-white font-semibold text-sm">Maham GPT</div>
          <div className="text-zinc-400 text-">AI Assistant • Online</div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 lg:p-6">
        {!conversation && (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mb-4 text-2xl font-bold text-white">M</div>
            <h1 className="text-3xl text-white font-semibold mb-2">How can I help you today? - Maham GPT</h1>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 mt-8 max-w-2xl w-full">
              <div className="bg-[#2f2f2f] p-4 rounded-xl text-left hover:bg-[#3a3a3a] cursor-pointer" onClick={()=>onSend("Hello!")}>
                <div className="text-white text-sm font-medium">Say hello 👋</div>
                <div className="text-zinc-400 text-xs mt-1">Start a friendly conversation</div>
              </div>
              <div className="bg-[#2f2f2f] p-4 rounded-xl text-left hover:bg-[#3a3a3a] cursor-pointer" onClick={()=>onSend("Generate image of a cute cat")}>
                <div className="text-white text-sm font-medium">Generate image 🖼️</div>
                <div className="text-zinc-400 text-xs mt-1">Create any image you imagine</div>
              </div>
              <div className="bg-[#2f2f2f] p-4 rounded-xl text-left hover:bg-[#3a3a3a] cursor-pointer" onClick={()=>onSend("Help me write an email")}>
                <div className="text-white text-sm font-medium">Write an email ✉️</div>
                <div className="text-zinc-400 text-xs mt-1">Help with writing</div>
              </div>
              <div className="bg-[#2f2f2f] p-4 rounded-xl text-left hover:bg-[#3a3a3a] cursor-pointer" onClick={()=>onSend("Explain quantum computing simply")}>
                <div className="text-white text-sm font-medium">Explain something 💡</div>
                <div className="text-zinc-400 text-xs mt-1">Learn anything</div>
              </div>
            </div>
          </div>
        )}
        
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.map(m => {
            const showImageGen = m.role === 'assistant' && isImageGenRequest(messages[messages.findIndex(msg => msg.id === m.id) -1]?.content || "")
            return (
              <div key={m.id} className={`flex gap-3 ${m.role==='user' ? 'justify-end' : 'justify-start'}`}>
                {m.role === 'assistant' && (
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0">M</div>
                )}
                <div className={`max-w-[85%] rounded-2xl px-5 py-3 text- leading-6 whitespace-pre-wrap break-words ${m.role==='user' ? 'bg-white text-black' : 'bg-[#2f2f2f] text-white'}`}>
                  {m.content}
                  {/* Show generated image if it was image request */}
                  {m.role === 'assistant' && messages.length > 1 && (
                    (() => {
                      const prevMsg = messages[messages.findIndex(msg => msg.id === m.id) -1]
                      if (prevMsg && isImageGenRequest(prevMsg.content)) {
                        return <img src={getImageUrl(prevMsg.content)} alt="Generated" className="mt-3 rounded-xl max-w-full border border-zinc-700" onError={(e)=>e.target.style.display='none'} />
                      }
                      return null
                    })()
                  )}
                </div>
                {m.role === 'user' && (
                  <div className="w-8 h-8 bg-zinc-600 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0">U</div>
                )}
              </div>
            )
          })}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-xs font-bold">M</div>
              <div className="bg-[#2f2f2f] text-white rounded-2xl px-5 py-3 text-sm animate-pulse">Thinking...</div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Selected image preview */}
      {selectedImage && (
        <div className="bg-[#212121] px-4 pb-2">
          <div className="max-w-3xl mx-auto relative inline-block">
            <img src={selectedImage} alt="Selected" className="h-20 rounded-lg border border-zinc-600" />
            <button onClick={()=>setSelectedImage(null)} className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">×</button>
          </div>
        </div>
      )}

      <div className="p-4 bg-[#212121]">
        <div className="max-w-3xl mx-auto flex gap-2 items-end bg-[#2f2f2f] rounded- px-4 py-2 border border-zinc-700 focus-within:border-zinc-500">
          {/* Image upload button */}
          <button onClick={()=>fileInputRef.current.click()} className="text-zinc-400 hover:text-white p-1">
            📎
          </button>
          <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageSelect} className="hidden" />
          
          <textarea
            value={input}
            onChange={e=>setInput(e.target.value)}
            onKeyDown={e=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); handleSend() }}}
            placeholder="Message Maham GPT"
            rows={1}
            className="flex-1 bg-transparent text-white placeholder-zinc-500 outline-none resize-none max-h-32 py-2.5 text-"
          />
          <button onClick={handleSend} disabled={loading || (!input.trim() && !selectedImage)} className="bg-white text-black rounded-full w-8 h-8 flex items-center justify-center disabled:opacity-40 hover:bg-zinc-200 transition">↑</button>
        </div>
        <p className="text- text-zinc-500 text-center mt-3">Maham GPT can make mistakes. Check important info.</p>
      </div>
    </div>
  )
}