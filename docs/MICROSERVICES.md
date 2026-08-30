# Konsep Arsitektur — Peta Microservice NexistPOS

Versi ringkas per **2026-08-30**. Versi interaktif (diagram) dipublish sebagai Claude Artifact privat dari sesi Claude Code — dokumen ini adalah salinan tertulisnya supaya tetap ada di riwayat repo.

## Rekomendasi singkat

Trafik `pos.nexisthub.id` saat ini masih ringan (satu backend container) dan cuma tiga domain aktif: identitas, katalog menu, order. Kalau langsung dipecah jadi service + database + network call terpisah di setiap transaksi kasir, biaya operasionalnya naik lebih cepat daripada manfaatnya.

Jalan yang lebih pas: **rapikan dulu jadi modular monolith** (batas modul tegas, tanpa query lintas modul langsung), baru **ekstraksi fisik dilakukan satu-satu** saat ada pemicu nyata.

Karena NexistPOS akan dijual sebagai produk langganan dan punya aplikasi Back Office resmi, ada satu domain yang benar-benar baru dan perlu masuk rancangan sejak Fase 0: **Billing & Subscription**. Back Office sendiri **bukan** alasan untuk memecah Identity lebih awal — satu backend bisa melayani dua frontend tanpa masalah (lihat bagian "Koreksi" di bawah).

## Bentuk sekarang vs target

**Sekarang**: `pos_frontend` (React SPA) → `pos_backend` (FastAPI, satu proses, modul auth/menu/order) → `pos_db` (PostgreSQL, semua tabel dalam satu database). 1 deployable, 1 database.

**Target**: Gateway (Caddy, `pos.nexisthub.id/api/v1/*`) di depan empat service, masing-masing dengan database sendiri:

| Service | Tanggung jawab | Memiliki tabel | Endpoint saat ini |
|---|---|---|---|
| **Identity** | Autentikasi, manajemen tenant & user, terbitkan JWT (role owner/cashier) | `tenants`, `users` | `/api/v1/auth/*` |
| **Catalog** | Kategori menu, item menu, harga, status tersedia/habis | `categories`, `menu_items` | `/api/v1/menu/*` |
| **Order** | Transaksi kasir (bill), baris item, status & metode bayar | `orders`, `order_items` | `/api/v1/orders/*` |
| **Billing & Subscription** *(baru)* | Paket langganan, tagihan, status aktif/trial/suspend tenant, integrasi payment gateway (Midtrans/Xendit) | `subscriptions`, `invoices`, `payment_transactions` | `/api/v1/billing/*` — belum ada |

Identity & Billing dipakai bareng oleh POS Terminal *dan* Back Office. Catalog & Order terutama dipakai POS Terminal.

Satu hal yang sudah benar di kode sekarang dan sangat membantu pemisahan ini: `OrderItem` sudah menyimpan **salinan** `name` dan `price` saat transaksi dibuat, bukan referensi hidup ke `menu_items`. Artinya Order Service nanti cuma perlu bicara ke Catalog Service **sekali, saat item ditambahkan ke keranjang** — bukan setiap kali order dibaca atau struk dicetak.

## Koreksi: Back Office bukan alasan pisah Identity

Satu backend (monolith atau bukan) bisa melayani banyak frontend sekaligus lewat endpoint yang sama — kasir dan Back Office cukup sama-sama login ke `/api/v1/auth/*` yang sudah ada. Back Office aman dibangun langsung di atas Fase 0 (modular monolith), tanpa menunggu Identity dipisah jadi service sendiri.

Yang benar-benar baru — bukan cuma "dipecah nanti" tapi **belum dirancang sama sekali** — adalah siklus tagihan, integrasi payment gateway, dan status aktif/suspend tenant. Domain ini perlu masuk perencanaan dari Fase 0 karena riwayatnya beda total dari transaksi kasir: webhook dari luar, bukan trafik dari POS.

## Pola komunikasi

**Sinkron (wajib cepat)**: kasir tambah item → Order Service → `GET /menu/items/{id}` ke Catalog Service → simpan snapshot harga & nama ke `order_db`. Auth: JWT ditandatangani Identity Service, **diverifikasi lokal** oleh service lain pakai secret bersama — bukan panggil Identity di setiap request.

**Async (boleh telat)**: Order Service terbitkan event `order.paid`; Billing Service terbitkan `tenant.suspended` / `invoice.paid`. Di skala ini belum perlu Kafka/RabbitMQ — Redis Streams atau Postgres `LISTEN/NOTIFY` sudah cukup sampai jumlah consumer bertambah. Konsumen masa depan: Reporting, Inventory, Notifikasi.

## Roadmap bertahap

| Fase | Aksi | Pemicu |
|---|---|---|
| **0 — sekarang** | Modular monolith + rancang modul `billing` (skeleton, payment gateway belum tersambung). Back Office boleh dibangun di fase ini. | — |
| **1** | Ekstrak **Billing Service** | Payment gateway (Midtrans/Xendit) tersambung — webhook tak boleh ikut lambat/gagal saat trafik kasir ramai, dan sebaliknya |
| **2** | Ekstrak **Catalog Service** | Menu dipakai lintas kanal (QR order meja, marketplace) atau harga perlu update tanpa redeploy POS inti |
| **3** | Ekstrak **Identity Service** | Butuh situs pricing/signup publik yang membuat tenant baru di luar backend POS, atau trafik login perlu scaling terpisah dari trafik kasir — **bukan** "dua app butuh SSO" |
| **4 — terakhir** | Ekstrak **Order Service** | Jumlah outlet/transaksi naik signifikan, butuh scaling independen dari service lain. Paling berisiko — jalur pendapatan inti, dipecah paling akhir setelah pola dari fase sebelumnya terbukti jalan |

## Risiko yang perlu diwaspadai

1. **Transaksi terdistribusi di jalur checkout** — jangan pakai 2-phase commit lintas service. Order Service tetap satu-satunya source of truth; panggilan ke Catalog saat checkout cukup read-only + snapshot.
2. **Kebocoran data antar tenant** — `tenant_id` dari JWT wajib difilter di setiap query, di setiap service, bukan cuma di Order seperti sekarang.
3. **Beban operasional naik lebih cepat dari tim** — tiap service = container + database + jalur deploy sendiri. Jangan pecah lebih dari yang benar-benar dioperasikan.
4. **Panggilan N+1 ke Catalog** — jangan panggil per-item satu-satu saat render daftar order. Desain endpoint Catalog agar terima banyak id sekaligus (`GET /menu/items?ids=a,b,c`).
5. **Webhook payment gateway diproses dobel** — Billing Service wajib idempotent, simpan `payment_transaction_id` dari gateway sebagai kunci unik.
6. **Kasir tetap jalan padahal tenant sudah nunggak** — perlu keputusan produk: suspend berlaku detik itu juga atau ditunda sampai akhir siklus tagihan? Order Service baca status ini dari cache/klaim (mis. di JWT, di-refresh berkala), bukan cek langsung ke Billing tiap transaksi.

## Referensi
- `docs/HANDOFF.md` — status proyek & next steps.
- `/opt/REPOS.md` — peta repo & deploy semua app di VPS ini.
