import { useEffect, useState } from 'react'
import client from '../api/client'
import Sidebar from '../components/Sidebar'
import ChatArea from '../components/ChatArea'

export default function Chat() {
  const [conversations,setConversations]=useState([])
  const [selectedId,setSelectedId]=useState(null)
  const [messages,setMessages]=useState([])
  const [loading,setLoading]=useState(false)
  const [sidebarOpen,setSidebarOpen]=useState(false)

  const fetchConvs = async () => {
    try { const {data}=await client.get('/api/conversations'); setConversations(data) } catch(e){ if(e.response?.status===401) window.location.href='/login' }
  }
  useEffect(()=>{ fetchConvs() },[])

  const handleNewChat = async () => {
    const {data}=await client.post('/api/conversations',{title:'New Chat'})
    setConversations(prev=>[data,...prev]); setSelectedId(data.id); setMessages([])
  }

  const handleSelect = async (id) => {
    setSelectedId(id); setLoading(true)
    try { const {data}=await client.get(`/api/conversations/${id}`); setMessages(data.messages) } catch(e){ console.error(e) } finally { setLoading(false) }
  }

  const handleSend = async (content) => {
    if (!selectedId){ await handleNewChat(); return }
    setLoading(true)
    const tempUser = {id:'temp-'+Date.now(), role:'user', content}
    setMessages(prev=>[...prev,tempUser])
    try {
      const {data}=await client.post(`/api/conversations/${selectedId}/messages`,{content})
      setMessages(prev=>[...prev.filter(m=>m.id!==tempUser.id), data.user_message, data.assistant_message])
      fetchConvs()
    } catch(e){
      setMessages(prev=>prev.filter(m=>m.id!==tempUser.id))
      alert(e.response?.data?.detail || 'Failed to send')
    } finally { setLoading(false) }
  }

  const handleRename = async (id,title) => {
    await client.patch(`/api/conversations/${id}`,{title}); fetchConvs()
  }
  const handleDelete = async (id) => {
    await client.delete(`/api/conversations/${id}`); setConversations(prev=>prev.filter(c=>c.id!==id)); if(selectedId===id){ setSelectedId(null); setMessages([]) }
  }

  const currentConv = conversations.find(c=>c.id===selectedId)

  return (
    <div className="flex h-screen">
      <Sidebar conversations={conversations} onNewChat={handleNewChat} onSelect={handleSelect} selectedId={selectedId} onRename={handleRename} onDelete={handleDelete} isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <div className="flex-1 flex flex-col">
        <div className="lg:hidden bg-[#171717] p-2 flex items-center"><button onClick={()=>setSidebarOpen(true)} className="text-white text-sm px-3 py-1 bg-zinc-800 rounded-full">☰ History</button></div>
        <ChatArea messages={messages} onSend={handleSend} loading={loading} conversation={currentConv} />
      </div>
    </div>
  )
}
