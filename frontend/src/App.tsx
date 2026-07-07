import { Routes, Route, Navigate, NavLink, useNavigate } from 'react-router-dom'
import { ShoppingCart, ReceiptText, UtensilsCrossed, LogOut, Loader2 } from 'lucide-react'
import { useAuth } from './auth'
import Login from './pages/Login'
import POS from './pages/POS'
import Orders from './pages/Orders'
import Menu from './pages/Menu'

function Shell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const nav = [
    { to: '/', label: 'Kasir', icon: ShoppingCart, end: true },
    { to: '/orders', label: 'Transaksi', icon: ReceiptText, end: false },
    ...(user?.role === 'owner' ? [{ to: '/menu', label: 'Menu', icon: UtensilsCrossed, end: false }] : []),
  ]
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200 px-4 h-14 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <span className="font-bold text-brand-600 text-lg">Nexist<span className="text-slate-800">POS</span></span>
          <nav className="flex items-center gap-1">
            {nav.map((n) => (
              <NavLink key={n.to} to={n.to} end={n.end}
                className={({ isActive }) => `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium ${isActive ? 'bg-brand-50 text-brand-700' : 'text-slate-500 hover:bg-slate-100'}`}>
                <n.icon size={16} /> {n.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <div className="text-right leading-tight hidden sm:block">
            <p className="font-medium text-slate-800">{user?.outlet_name}</p>
            <p className="text-xs text-slate-400">{user?.full_name} · {user?.role}</p>
          </div>
          <button onClick={logout} className="text-slate-400 hover:text-red-600" title="Keluar"><LogOut size={18} /></button>
        </div>
      </header>
      <main className="flex-1 min-h-0">{children}</main>
    </div>
  )
}

function Protected({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center text-slate-400"><Loader2 className="animate-spin" /></div>
  if (!user) return <Navigate to="/login" replace />
  return <Shell>{children}</Shell>
}

export default function App() {
  const { user } = useAuth()
  const navigate = useNavigate()
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login onDone={() => navigate('/')} />} />
      <Route path="/" element={<Protected><POS /></Protected>} />
      <Route path="/orders" element={<Protected><Orders /></Protected>} />
      <Route path="/menu" element={<Protected><Menu /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
