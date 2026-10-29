import { useState } from 'react'
import client from '../api/client'
import { useNavigate, Link } from 'react-router-dom'

export default function Login() {
  const [email,setEmail]=useState(''); const [password,setPassword]=useState(''); const [err,setErr]=useState(''); const [loading,setLoading]=useState(false)
  const nav = useNavigate()
  const submit = async e => {
    e.preventDefault(); setErr(''); setLoading(true)
    try { const {data}=await client.post('/api/auth/login',{email,password}); localStorage.setItem('token',data.access_token); localStorage.setItem('user',JSON.stringify(data.user)); nav('/') }
    catch(e){ setErr(e.response?.data?.detail || 'Login failed') } finally { setLoading(false) }
  }
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0f0f] p-4">
      <form onSubmit={submit} className="w-full max-w-sm bg-[#171717] rounded-2xl p-6 space-y-4">
        <h1 className="text-2xl text-white font-semibold">Welcome back</h1>
        <input className="w-full bg-[#2f2f2f] text-white rounded-lg px-3 py-2.5 text-sm outline-none" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <input type="password" className="w-full bg-[#2f2f2f] text-white rounded-lg px-3 py-2.5 text-sm outline-none" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {err && <div className="text-red-400 text-xs">{err}</div>}
        <button disabled={loading} className="w-full bg-white text-black rounded-full py-2.5 font-medium text-sm disabled:opacity-50">{loading?'Signing in...':'Log in'}</button>
        <div className="text-xs text-zinc-400 text-center">No account? <Link to="/register" className="text-white underline">Register</Link></div>
      </form>
    </div>
  )
}
