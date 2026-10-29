import { useState } from 'react'
import client from '../api/client'
import { useNavigate, Link } from 'react-router-dom'

export default function Register() {
  const [form,setForm]=useState({name:'',email:'',password:'',confirm_password:''}); const [err,setErr]=useState(''); const [loading,setLoading]=useState(false)
  const nav = useNavigate()
  const submit = async e => {
    e.preventDefault(); setErr(''); setLoading(true)
    if (form.password!==form.confirm_password){ setErr('Passwords do not match'); setLoading(false); return }
    try { await client.post('/api/auth/register',form); nav('/login') }
    catch(e){ setErr(e.response?.data?.detail || 'Registration failed') } finally { setLoading(false) }
  }
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0f0f] p-4">
      <form onSubmit={submit} className="w-full max-w-sm bg-[#171717] rounded-2xl p-6 space-y-4">
        <h1 className="text-2xl text-white font-semibold">Create account</h1>
        <input className="w-full bg-[#2f2f2f] text-white rounded-lg px-3 py-2.5 text-sm outline-none" placeholder="Name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required />
        <input className="w-full bg-[#2f2f2f] text-white rounded-lg px-3 py-2.5 text-sm outline-none" placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required />
        <input type="password" className="w-full bg-[#2f2f2f] text-white rounded-lg px-3 py-2.5 text-sm outline-none" placeholder="Password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required />
        <input type="password" className="w-full bg-[#2f2f2f] text-white rounded-lg px-3 py-2.5 text-sm outline-none" placeholder="Confirm Password" value={form.confirm_password} onChange={e=>setForm({...form,confirm_password:e.target.value})} required />
        {err && <div className="text-red-400 text-xs">{err}</div>}
        <button disabled={loading} className="w-full bg-white text-black rounded-full py-2.5 font-medium text-sm disabled:opacity-50">{loading?'Creating...':'Create account'}</button>
        <div className="text-xs text-zinc-400 text-center">Already have account? <Link to="/login" className="text-white underline">Login</Link></div>
      </form>
    </div>
  )
}
