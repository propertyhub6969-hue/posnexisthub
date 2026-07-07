import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import api from '../api'
import { useAuth } from '../auth'

export default function Login({ onDone }: { onDone: () => void }) {
  const { setToken } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [outlet, setOutlet] = useState('')
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setErr(''); setBusy(true)
    try {
      const body = mode === 'register'
        ? { outlet_name: outlet, full_name: fullName, email, password }
        : { email, password }
      const { data } = await api.post(`/auth/${mode}`, body)
      await setToken(data.access_token)
      onDone()
    } catch (e: any) {
      setErr(e?.response?.data?.detail || 'Gagal. Coba lagi.')
    } finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 p-4">
      <div className="w-full max-w-sm card p-6">
        <div className="text-center mb-5">
          <p className="text-2xl font-bold text-brand-600">Nexist<span className="text-slate-800">POS</span></p>
          <p className="text-sm text-slate-400 mt-1">Kasir F&B</p>
        </div>
        <div className="flex rounded-lg bg-slate-100 p-1 mb-4 text-sm">
          {(['login', 'register'] as const).map((m) => (
            <button key={m} onClick={() => setMode(m)}
              className={`flex-1 py-1.5 rounded-md font-medium ${mode === m ? 'bg-white text-brand-600 shadow-sm' : 'text-slate-500'}`}>
              {m === 'login' ? 'Masuk' : 'Daftar Outlet'}
            </button>
          ))}
        </div>
        <form onSubmit={submit} className="space-y-3">
          {mode === 'register' && (
            <>
              <div><label className="label">Nama Outlet</label><input className="input" required value={outlet} onChange={(e) => setOutlet(e.target.value)} placeholder="Kopi Senja" /></div>
              <div><label className="label">Nama Kamu</label><input className="input" required value={fullName} onChange={(e) => setFullName(e.target.value)} /></div>
            </>
          )}
          <div><label className="label">Email</label><input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></div>
          <div><label className="label">Password</label><input className="input" type="password" required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} /></div>
          {err && <p className="text-sm text-red-600">{err}</p>}
          <button type="submit" disabled={busy} className="btn-primary w-full flex items-center justify-center gap-2">
            {busy && <Loader2 size={16} className="animate-spin" />}{mode === 'login' ? 'Masuk' : 'Daftar'}
          </button>
        </form>
      </div>
    </div>
  )
}
