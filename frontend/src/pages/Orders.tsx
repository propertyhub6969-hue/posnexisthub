import { useEffect, useState } from 'react'
import { Loader2, Eye } from 'lucide-react'
import api, { fmt } from '../api'
import type { Order } from '../types'

export default function Orders() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [todayOnly, setTodayOnly] = useState(true)
  const [view, setView] = useState<Order | null>(null)

  const load = (today: boolean) => {
    setLoading(true)
    api.get<Order[]>('/orders', { params: { today } }).then((r) => setOrders(r.data)).finally(() => setLoading(false))
  }
  useEffect(() => { load(todayOnly) }, [todayOnly])

  const total = orders.filter((o) => o.status === 'paid').reduce((s, o) => s + Number(o.total), 0)

  return (
    <div className="p-4 max-w-4xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex rounded-lg bg-white border border-slate-200 p-1 text-sm">
          {[{ k: true, l: 'Hari ini' }, { k: false, l: 'Semua' }].map((t) => (
            <button key={String(t.k)} onClick={() => setTodayOnly(t.k)} className={`px-3 py-1 rounded-md font-medium ${todayOnly === t.k ? 'bg-brand-500 text-white' : 'text-slate-500'}`}>{t.l}</button>
          ))}
        </div>
        <div className="text-sm text-slate-500">Omzet {todayOnly ? 'hari ini' : 'total'}: <span className="font-semibold text-slate-800">{fmt(total)}</span> · {orders.length} transaksi</div>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200"><tr>{['No.', 'Waktu', 'Tipe', 'Item', 'Total', 'Bayar', 'Kasir', ''].map((h, i) => (
            <th key={i} className="px-3 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>))}</tr></thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr><td colSpan={8} className="py-10 text-center text-slate-400"><Loader2 className="inline animate-spin" /></td></tr>
            ) : orders.length === 0 ? (
              <tr><td colSpan={8} className="py-10 text-center text-slate-400 text-sm">Belum ada transaksi.</td></tr>
            ) : orders.map((o) => (
              <tr key={o.id} className="hover:bg-slate-50">
                <td className="px-3 py-2.5 font-medium text-slate-800">{o.order_number}</td>
                <td className="px-3 py-2.5 text-slate-500 text-xs">{new Date(o.created_at).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}</td>
                <td className="px-3 py-2.5 text-slate-500 capitalize">{o.order_type.replace('_', '-')}{o.table_no ? ` · ${o.table_no}` : ''}</td>
                <td className="px-3 py-2.5 text-slate-500">{o.items.reduce((s, it) => s + Number(it.quantity), 0)}</td>
                <td className="px-3 py-2.5 font-medium text-slate-800">{fmt(o.total)}</td>
                <td className="px-3 py-2.5 text-slate-500 uppercase text-xs">{o.payment_method}</td>
                <td className="px-3 py-2.5 text-slate-500 text-xs">{o.cashier_name ?? '—'}</td>
                <td className="px-3 py-2.5 text-right"><button onClick={() => setView(o)} className="text-slate-400 hover:text-brand-600"><Eye size={16} /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {view && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={() => setView(null)}>
          <div className="bg-white rounded-xl w-full max-w-xs p-5" onClick={(e) => e.stopPropagation()}>
            <p className="text-center font-bold text-slate-800">{view.order_number}</p>
            <p className="text-center text-xs text-slate-400 mb-3">{new Date(view.created_at).toLocaleString('id-ID')}</p>
            <div className="border-t border-dashed border-slate-200 py-2 space-y-1 text-sm">
              {view.items.map((it) => (
                <div key={it.id} className="flex justify-between"><span className="text-slate-600">{Number(it.quantity)}× {it.name}</span><span>{fmt(it.line_total)}</span></div>
              ))}
            </div>
            <div className="border-t border-dashed border-slate-200 pt-2 text-sm space-y-1">
              <div className="flex justify-between font-semibold"><span>Total</span><span>{fmt(view.total)}</span></div>
              <div className="flex justify-between text-slate-500"><span>Bayar</span><span>{fmt(view.paid_amount)}</span></div>
              <div className="flex justify-between text-slate-500"><span>Kembali</span><span>{fmt(view.change_amount)}</span></div>
            </div>
            <button onClick={() => setView(null)} className="btn-primary w-full mt-4 text-sm">Tutup</button>
          </div>
        </div>
      )}
    </div>
  )
}
