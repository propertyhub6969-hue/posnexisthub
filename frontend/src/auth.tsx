import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import api from './api'
import type { Me } from './types'

interface AuthCtx {
  user: Me | null
  loading: boolean
  setToken: (t: string) => Promise<void>
  logout: () => void
  refresh: () => Promise<void>
}

const Ctx = createContext<AuthCtx>({} as AuthCtx)
export const useAuth = () => useContext(Ctx)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    if (!localStorage.getItem('pos_token')) { setUser(null); setLoading(false); return }
    try {
      const { data } = await api.get<Me>('/auth/me')
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { refresh() }, [])

  const setToken = async (t: string) => {
    localStorage.setItem('pos_token', t)
    setLoading(true)
    await refresh()
  }
  const logout = () => {
    localStorage.removeItem('pos_token')
    setUser(null)
    location.href = '/login'
  }

  return <Ctx.Provider value={{ user, loading, setToken, logout, refresh }}>{children}</Ctx.Provider>
}
