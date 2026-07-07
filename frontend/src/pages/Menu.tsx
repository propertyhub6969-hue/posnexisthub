import { useEffect, useState } from 'react'
import { Loader2, Plus, Trash2 } from 'lucide-react'
import api, { fmt } from '../api'
import type { Category, MenuItem } from '../types'

export default function Menu() {
  const [cats, setCats] = useState<Category[]>([])
  const [items, setItems] = useState<MenuItem[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')

  const [catName, setCatName] = useState('')
  const [form, setForm] = useState<{ name: string; price?: number; category_id: string }>({ name: '', price: undefined, category_id: '' })
  const [busy, setBusy] = useState(false)

  const load = async () => {
    setLoading(true)
    const [c, i] = await Promise.all([api.get<Category[]>('/menu/categories'), api.get<MenuItem[]>('/menu/items')])
    setCats(c.data); setItems(i.data); setLoading(false)
  }
  useEffect(() => { load() }, [])

  async function addCat(e: React.FormEvent) {
    e.preventDefault(); if (!catName.trim()) return
    try { await api.post('/menu/categories', { name: catName.trim() }); setCatName(''); await load() }
    catch (e: any) { setErr(e?.response?.data?.detail || 'Gagal.') }
  }
  async function delCat(id: string) {
    if (!confirm('Hapus kategori?')) return
    await api.delete(`/menu/categories/${id}`); await load()
  }
  async function addItem(e: React.FormEvent) {
    e.preventDefault(); if (!form.name.trim() || form.price == null) { setErr('Nama & harga wajib.'); return }
    setBusy(true); setErr('')
    try {
      await api.post('/menu/items', { name: form.name.trim(), price: form.price, category_id: form.category_id || null })
      setForm({ name: '', price: undefined, category_id: '' }); await load()
    } catch (e: any) { setErr(e?.response?.data?.detail || 'Gagal.') } finally { setBusy(false) }
  }
  async function delItem(id: string) {
    if (!confirm('Hapus menu?')) return
    await api.delete(`/menu/items/${id}`); await load()
  }
  async function toggleAvail(it: MenuItem) {
    await api.patch(`/menu/items/${it.id}`, { is_available: !it.is_available }); await load()
  }

  if (loading) return <div className="p-10 text-center text-slate-400"><Loader2 className="inline animate-spin" /></div>

  return (
    <div className="p-4 max-w-4xl mx-auto grid md:grid-cols-3 gap-4">
      {/* Categories */}
      <div className="card p-4 h-fit">
        <p className="font-semibold text-slate-800 mb-3">Kategori</p>
        <form onSubmit={addCat} className="flex gap-2 mb-3">
          <input className="input" placeholder="Nama kategori" value={catName} onChange={(e) => setCatName(e.target.value)} />
          <button className="btn-primary px-3"><Plus size={16} /></button>
        </form>
        <div className="space-y-1">
          {cats.length === 0 && <p className="text-xs text-slate-400">Belum ada kategori.</p>}
          {cats.map((c) => (
            <div key={c.id} className="flex items-center justify-between text-sm py-1.5 border-b border-slate-100">
              <span className="text-slate-700">{c.name}</span>
              <button onClick={() => delCat(c.id)} className="text-slate-300 hover:text-red-600"><Trash2 size={14} /></button>
            </div>
          ))}
        </div>
      </div>

      {/* Items */}
      <div className="md:col-span-2 space-y-4">
        <div className="card p-4">
          <p className="font-semibold text-slate-800 mb-3">Tambah Menu</p>
          <form onSubmit={addItem} className="grid grid-cols-2 gap-2">
            <input className="input col-span-2" placeholder="Nama menu" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <input className="input" type="number" min={0} placeholder="Harga" value={form.price ?? ''} onChange={(e) => setForm({ ...form, price: e.target.value === '' ? undefined : Number(e.target.value) })} />
            <select className="input" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
              <option value="">Tanpa kategori</option>
              {cats.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            {err && <p className="text-xs text-red-600 col-span-2">{err}</p>}
            <button disabled={busy} className="btn-primary col-span-2 flex items-center justify-center gap-2">{busy && <Loader2 size={15} className="animate-spin" />}Tambah</button>
          </form>
        </div>

        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200"><tr>{['Menu', 'Kategori', 'Harga', 'Tersedia', ''].map((h, i) => (
              <th key={i} className="px-3 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>))}</tr></thead>
            <tbody className="divide-y divide-slate-100">
              {items.length === 0 ? (
                <tr><td colSpan={5} className="py-8 text-center text-slate-400 text-sm">Belum ada menu.</td></tr>
              ) : items.map((it) => (
                <tr key={it.id} className="hover:bg-slate-50">
                  <td className="px-3 py-2.5 font-medium text-slate-800">{it.name}</td>
                  <td className="px-3 py-2.5 text-slate-500">{it.category_name ?? '—'}</td>
                  <td className="px-3 py-2.5 text-slate-700">{fmt(it.price)}</td>
                  <td className="px-3 py-2.5">
                    <button onClick={() => toggleAvail(it)} className={`text-xs px-2 py-0.5 rounded-full ${it.is_available ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>{it.is_available ? 'Ya' : 'Tidak'}</button>
                  </td>
                  <td className="px-3 py-2.5 text-right"><button onClick={() => delItem(it.id)} className="text-slate-300 hover:text-red-600"><Trash2 size={15} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
