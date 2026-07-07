import { useEffect, useMemo, useState } from 'react'
import { Plus, Minus, Trash2, Loader2, Search, Printer, X } from 'lucide-react'
import api, { fmt } from '../api'
import type { Category, MenuItem, CartLine, Order, OrderType, PaymentMethod } from '../types'

export default function POS() {
  const [cats, setCats] = useState<Category[]>([])
  const [items, setItems] = useState<MenuItem[]>([])
  const [loading, setLoading] = useState(true)
  const [activeCat, setActiveCat] = useState<string>('all')
  const [q, setQ] = useState('')

  const [cart, setCart] = useState<CartLine[]>([])
  const [orderType, setOrderType] = useState<OrderType>('dine_in')
  const [tableNo, setTableNo] = useState('')
  const [payMethod, setPayMethod] = useState<PaymentMethod>('cash')
  const [cash, setCash] = useState<number | undefined>(undefined)
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')
  const [receipt, setReceipt] = useState<Order | null>(null)

  useEffect(() => {
    Promise.all([api.get<Category[]>('/menu/categories'), api.get<MenuItem[]>('/menu/items')])
      .then(([c, i]) => { setCats(c.data); setItems(i.data) })
      .finally(() => setLoading(false))
  }, [])

  const shown = useMemo(() => items.filter((it) =>
    it.is_available &&
    (activeCat === 'all' || it.category_id === activeCat) &&
    (!q || it.name.toLowerCase().includes(q.toLowerCase()))
  ), [items, activeCat, q])

  const subtotal = cart.reduce((s, l) => s + l.price * l.quantity, 0)
  const change = payMethod === 'cash' && cash != null ? cash - subtotal : 0

  function add(it: MenuItem) {
    setCart((c) => {
      const i = c.findIndex((l) => l.menu_item_id === it.id)
      if (i >= 0) { const n = [...c]; n[i] = { ...n[i], quantity: n[i].quantity + 1 }; return n }
      return [...c, { menu_item_id: it.id, name: it.name, price: Number(it.price), quantity: 1 }]
    })
  }
  function setQty(idx: number, delta: number) {
    setCart((c) => c.map((l, i) => i === idx ? { ...l, quantity: l.quantity + delta } : l).filter((l) => l.quantity > 0))
  }
  function removeLine(idx: number) { setCart((c) => c.filter((_, i) => i !== idx)) }
  function reset() { setCart([]); setTableNo(''); setCash(undefined); setPayMethod('cash'); setOrderType('dine_in') }

  async function checkout() {
    if (cart.length === 0) return
    if (payMethod === 'cash' && (cash == null || cash < subtotal)) { setErr('Nominal tunai kurang dari total.'); return }
    setSaving(true); setErr('')
    try {
      const { data } = await api.post<Order>('/orders', {
        order_type: orderType, table_no: tableNo || undefined, payment_method: payMethod,
        paid_amount: payMethod === 'cash' ? cash : subtotal,
        items: cart.map((l) => ({ menu_item_id: l.menu_item_id, name: l.name, price: l.price, quantity: l.quantity })),
      })
      setReceipt(data); reset()
    } catch (e: any) { setErr(e?.response?.data?.detail || 'Gagal menyimpan transaksi.') } finally { setSaving(false) }
  }

  if (loading) return <div className="h-full flex items-center justify-center text-slate-400"><Loader2 className="animate-spin" /></div>

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col lg:flex-row">
      {/* Menu */}
      <div className="flex-1 flex flex-col min-h-0 p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="relative flex-1 max-w-xs">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input className="input pl-9" placeholder="Cari menu..." value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
        </div>
        <div className="flex gap-1.5 mb-3 overflow-x-auto pb-1">
          <button onClick={() => setActiveCat('all')} className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap ${activeCat === 'all' ? 'bg-brand-500 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>Semua</button>
          {cats.map((c) => (
            <button key={c.id} onClick={() => setActiveCat(c.id)} className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap ${activeCat === c.id ? 'bg-brand-500 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>{c.name}</button>
          ))}
        </div>
        <div className="flex-1 overflow-y-auto">
          {shown.length === 0 ? (
            <div className="text-center text-slate-400 text-sm py-16">Belum ada menu. {cats.length === 0 && 'Tambah menu dulu di tab Menu.'}</div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-2.5">
              {shown.map((it) => (
                <button key={it.id} onClick={() => add(it)} className="card p-3 text-left hover:border-brand-400 hover:shadow transition-all active:scale-95">
                  <p className="font-medium text-slate-800 text-sm leading-tight line-clamp-2">{it.name}</p>
                  <p className="text-brand-600 font-semibold text-sm mt-2">{fmt(it.price)}</p>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Cart */}
      <div className="w-full lg:w-96 bg-white border-t lg:border-t-0 lg:border-l border-slate-200 flex flex-col min-h-0">
        <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
          <p className="font-semibold text-slate-800">Pesanan</p>
          {cart.length > 0 && <button onClick={reset} className="text-xs text-slate-400 hover:text-red-600">Kosongkan</button>}
        </div>
        <div className="flex-1 overflow-y-auto px-4 divide-y divide-slate-100">
          {cart.length === 0 ? (
            <p className="text-sm text-slate-400 text-center py-10">Pilih menu untuk mulai.</p>
          ) : cart.map((l, i) => (
            <div key={i} className="py-2.5 flex items-center gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-800 truncate">{l.name}</p>
                <p className="text-xs text-slate-400">{fmt(l.price)}</p>
              </div>
              <div className="flex items-center gap-1.5">
                <button onClick={() => setQty(i, -1)} className="w-6 h-6 rounded bg-slate-100 flex items-center justify-center text-slate-600"><Minus size={13} /></button>
                <span className="w-6 text-center text-sm font-medium">{l.quantity}</span>
                <button onClick={() => setQty(i, 1)} className="w-6 h-6 rounded bg-slate-100 flex items-center justify-center text-slate-600"><Plus size={13} /></button>
              </div>
              <span className="w-20 text-right text-sm font-medium text-slate-700">{fmt(l.price * l.quantity)}</span>
              <button onClick={() => removeLine(i)} className="text-slate-300 hover:text-red-600"><Trash2 size={14} /></button>
            </div>
          ))}
        </div>
        <div className="border-t border-slate-100 p-4 space-y-3">
          <div className="flex gap-2">
            {(['dine_in', 'takeaway'] as const).map((t) => (
              <button key={t} onClick={() => setOrderType(t)} className={`flex-1 py-1.5 rounded-lg text-sm font-medium border ${orderType === t ? 'border-brand-500 bg-brand-50 text-brand-700' : 'border-slate-200 text-slate-500'}`}>
                {t === 'dine_in' ? 'Dine-in' : 'Takeaway'}
              </button>
            ))}
          </div>
          {orderType === 'dine_in' && <input className="input" placeholder="No. meja (opsional)" value={tableNo} onChange={(e) => setTableNo(e.target.value)} />}
          <div className="flex gap-2">
            {(['cash', 'qris', 'transfer'] as const).map((m) => (
              <button key={m} onClick={() => setPayMethod(m)} className={`flex-1 py-1.5 rounded-lg text-xs font-medium border uppercase ${payMethod === m ? 'border-brand-500 bg-brand-50 text-brand-700' : 'border-slate-200 text-slate-500'}`}>{m}</button>
            ))}
          </div>
          {payMethod === 'cash' && (
            <div className="flex items-center gap-2">
              <input className="input" type="number" min={0} placeholder="Uang diterima" value={cash ?? ''} onChange={(e) => setCash(e.target.value === '' ? undefined : Number(e.target.value))} />
              <span className={`text-sm whitespace-nowrap ${change < 0 ? 'text-red-500' : 'text-slate-500'}`}>Kembali {fmt(Math.max(change, 0))}</span>
            </div>
          )}
          <div className="flex items-center justify-between text-base font-semibold">
            <span>Total</span><span className="text-brand-600">{fmt(subtotal)}</span>
          </div>
          {err && <p className="text-xs text-red-600">{err}</p>}
          <button onClick={checkout} disabled={saving || cart.length === 0} className="btn-primary w-full flex items-center justify-center gap-2 py-2.5">
            {saving && <Loader2 size={16} className="animate-spin" />}Bayar
          </button>
        </div>
      </div>

      {receipt && <Receipt order={receipt} onClose={() => setReceipt(null)} />}
    </div>
  )
}

function Receipt({ order, onClose }: { order: Order; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-xl w-full max-w-xs p-5" onClick={(e) => e.stopPropagation()}>
        <div className="text-center mb-3">
          <p className="font-bold text-slate-800">Struk</p>
          <p className="text-xs text-slate-400">{order.order_number} · {new Date(order.created_at).toLocaleString('id-ID')}</p>
          <p className="text-xs text-slate-400 capitalize">{order.order_type.replace('_', '-')}{order.table_no ? ` · Meja ${order.table_no}` : ''}</p>
        </div>
        <div className="border-t border-dashed border-slate-200 py-2 space-y-1 text-sm">
          {order.items.map((it) => (
            <div key={it.id} className="flex justify-between">
              <span className="text-slate-600">{Number(it.quantity)}× {it.name}</span>
              <span className="text-slate-700">{fmt(it.line_total)}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-dashed border-slate-200 pt-2 text-sm space-y-1">
          <div className="flex justify-between font-semibold"><span>Total</span><span>{fmt(order.total)}</span></div>
          <div className="flex justify-between text-slate-500"><span>Bayar ({order.payment_method})</span><span>{fmt(order.paid_amount)}</span></div>
          <div className="flex justify-between text-slate-500"><span>Kembali</span><span>{fmt(order.change_amount)}</span></div>
        </div>
        <div className="flex gap-2 mt-4">
          <button onClick={() => window.print()} className="btn-secondary flex-1 flex items-center justify-center gap-1.5 text-sm"><Printer size={15} /> Cetak</button>
          <button onClick={onClose} className="btn-primary flex-1 flex items-center justify-center gap-1.5 text-sm"><X size={15} /> Tutup</button>
        </div>
      </div>
    </div>
  )
}
