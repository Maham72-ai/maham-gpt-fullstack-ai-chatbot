import { useState } from 'react'

function groupConversations(convs) {
  const now = new Date()
  const todayStr = now.toDateString()
  const yesterday = new Date(now); yesterday.setDate(now.getDate()-1)
  const yesterdayStr = yesterday.toDateString()
  const sevenDaysAgo = new Date(now); sevenDaysAgo.setDate(now.getDate()-7)

  const groups = { Today: [], Yesterday: [], 'Previous 7 Days': [], Older: [] }
  convs.forEach(c => {
    const d = new Date(c.last_message_at)
    const ds = d.toDateString()
    if (ds === todayStr) groups.Today.push(c)
    else if (ds === yesterdayStr) groups.Yesterday.push(c)
    else if (d >= sevenDaysAgo) groups['Previous 7 Days'].push(c)
    else groups.Older.push(c)
  })
  return groups
}

export default function Sidebar({ conversations, onNewChat, onSelect, selectedId, onRename, onDelete, isOpen, setIsOpen }) {
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const groups = groupConversations(conversations)

  return (
    <>
      <div className={`fixed inset-0 bg-black/50 z-20 lg:hidden ${isOpen ? '' : 'hidden'}`} onClick={()=>setIsOpen(false)} />
      <div className={`w-[280px] bg-[#171717] text-white flex flex-col h-screen fixed lg:static z-30 transition-transform ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="p-3">
          <button onClick={onNewChat} className="w-full bg-white text-black rounded-full py-2.5 font-medium hover:bg-zinc-200">+ New Chat</button>
        </div>
        <div className="flex-1 overflow-y-auto px-2">
          {Object.entries(groups).map(([label, list]) => list.length>0 && (
            <div key={label} className="mb-4">
              <div className="text-[11px] text-zinc-500 font-semibold uppercase tracking-wider px-2 py-1">{label}</div>
              {list.map(c => (
                <div key={c.id} className={`group flex items-center justify-between px-2 py-2 rounded-lg cursor-pointer hover:bg-zinc-800 ${selectedId===c.id ? 'bg-zinc-800' : ''}`}>
                  {editingId===c.id ? (
                    <input autoFocus value={editTitle} onChange={e=>setEditTitle(e.target.value)}
                      onBlur={()=>{ if(editTitle.trim()) onRename(c.id, editTitle.trim()); setEditingId(null)}}
                      onKeyDown={e=>{ if(e.key==='Enter'){ onRename(c.id, editTitle.trim()); setEditingId(null)} if(e.key==='Escape') setEditingId(null)}}
                      className="bg-zinc-900 text-white text-sm px-2 py-1 rounded w-full" />
                  ) : (
                    <div onClick={()=>{ onSelect(c.id); setIsOpen(false)}} className="truncate text-sm flex-1">{c.title}</div>
                  )}
                  <div className="hidden group-hover:flex gap-1 ml-2">
                    <button onClick={()=>{ setEditingId(c.id); setEditTitle(c.title)}} className="text-xs text-zinc-400 hover:text-white">✎</button>
                    <button onClick={()=>{ if(confirm('Delete this chat?')) onDelete(c.id)}} className="text-xs text-zinc-400 hover:text-red-400">🗑</button>
                  </div>
                </div>
              ))}
            </div>
          ))}
          {conversations.length===0 && <div className="text-zinc-500 text-sm text-center mt-10">No chats yet</div>}
        </div>
        <div className="p-3 border-t border-zinc-800">
          <button onClick={()=>{ localStorage.clear(); window.location.href='/login'}} className="text-sm text-zinc-400 hover:text-white">Logout</button>
        </div>
      </div>
    </>
  )
}
