# NexistPOS — Handoff

Status proyek per **2026-08-30**. Dokumen ini adalah titik masuk untuk sesi/engineer berikutnya.

## Apa itu NexistPOS
POS F&B (kasir, menu, transaksi), multi-tenant. **Arah produk: dijual sebagai layanan langganan (SaaS)** ke banyak bisnis F&B eksternal — bukan cuma alat internal satu outlet. Akan punya **aplikasi Back Office resmi** sebagai frontend kedua (laporan, manajemen multi-outlet, manajemen staf/langganan) di samping frontend kasir yang sudah ada.

NexistPOS **terpisah dan tidak terkait** dengan NexistHub (ERP) meski satu domain keluarga `nexisthub.id` — jangan asumsikan mereka berbagi user/auth.

## Yang sudah ada (DONE)
| Item | Status | Lokasi |
|---|---|---|
| Backend FastAPI (auth, menu, order) | ✅ | `app/` — lihat struktur di bawah |
| Frontend kasir (React + Vite) | ✅ | `frontend/src/pages/` (Login, Menu, Orders, POS) |
| Migrasi DB (Alembic) | ✅ | `alembic/` |
| Deploy Docker Compose (prod) | ✅ | `docker-compose.prod.yml` |
| **Live production** | ✅ https://pos.nexisthub.id | via Caddy shared edge |
| Repo GitHub | ✅ pushed `main` | github.com/propertyhub6969-hue/posnexisthub |
| **Konsep arsitektur microservice** | ✅ | `docs/MICROSERVICES.md` (ringkas) + artifact interaktif (lihat Referensi) |

## Struktur backend saat ini (monolith)
```
app/
  api/v1/endpoints/  auth.py · menu.py · order.py
  models/            tenant.py · user.py · menu.py · order.py
  schemas/           auth.py · menu.py · order.py
  core/              config.py · database.py · security.py
```
Satu database (`pos_db`) menyimpan semua tabel: `tenants`, `users`, `categories`, `menu_items`, `orders`, `order_items`. Auth berbasis JWT dengan `tenant_id` di klaim token (lihat `app/api/deps.py::AuthContext`). `OrderItem` sudah menyimpan **salinan** `name`/`price` saat transaksi dibuat (bukan referensi hidup ke `menu_items`) — pola ini penting untuk rencana pemisahan service, lihat `docs/MICROSERVICES.md`.

**Belum ada sama sekali**: modul billing/subscription (paket langganan, invoice, integrasi payment gateway, status aktif/suspend tenant). Ini domain baru yang perlu dirancang untuk mendukung model SaaS.

## Deployment (PENTING — jangan sampai mengganggu app lain)
Server ini menjalankan **banyak app** di belakang **satu container Caddy** bersama (network `edge`). Lihat `/opt/REPOS.md` untuk peta lengkap semua repo di VPS ini.

```bash
cd /opt/pos-nexisthub
git pull
docker compose -f docker-compose.prod.yml up -d --build          # rebuild semua
docker compose -f docker-compose.prod.yml up -d --build frontend  # frontend saja
```
Backend menjalankan `alembic upgrade head` otomatis saat start. Kode di-COPY ke image → **wajib** `--build` tiap perubahan. Database (`pos_db`) terikat ke `127.0.0.1:5435` saja, tidak terbuka ke internet.

## Git / push
Remote SSH: `git@github.com:propertyhub6969-hue/posnexisthub.git`, pakai key akun `~/.ssh/gh_account` (default, tanpa override `core.sshCommand`) — `git push` langsung jalan.

## Arsitektur target — ringkasan (detail: `docs/MICROSERVICES.md`)
**Rekomendasi: jangan langsung pecah jadi microservice fisik.** Skala saat ini (1 backend container) belum butuh itu — biayanya (network hop tiap transaksi, N kali database, N jalur deploy) lebih besar dari manfaatnya sekarang. Jalan yang benar: **modular monolith** dulu (batas modul tegas, tanpa query lintas modul), baru diekstraksi satu-satu saat ada pemicu nyata.

**Empat bounded context target:**
- **Identity** — `tenants`, `users`, auth/JWT
- **Billing & Subscription** (baru, belum ada di kode) — `subscriptions`, `invoices`, `payment_transactions`, status tenant, integrasi payment gateway (Midtrans/Xendit)
- **Catalog** — `categories`, `menu_items`
- **Order** — `orders`, `order_items` (jalur pendapatan inti — ekstraksi paling akhir & paling hati-hati)

**Koreksi penting**: aplikasi Back Office (frontend kedua) **bukan** alasan untuk memisahkan Identity lebih awal — satu backend bisa melayani dua frontend lewat endpoint auth yang sama. Pemicu ekstraksi Identity yang lebih realistis: situs pricing/signup publik, atau trafik login butuh scaling terpisah dari trafik kasir.

**Roadmap 5 fase**: (0) modular monolith + rancang modul billing, Back Office boleh dibangun di fase ini → (1) ekstrak Billing (dipicu integrasi payment gateway — webhook tak boleh terganggu trafik kasir, dan sebaliknya) → (2) ekstrak Catalog (dipicu multi-kanal menu) → (3) ekstrak Identity (dipicu signup publik / scaling login) → (4) ekstrak Order (terakhir, paling berisiko).

**Risiko yang perlu diwaspadai**: transaksi terdistribusi di jalur checkout (jangan 2PC — Order tetap source of truth, panggilan ke Catalog read-only + snapshot), kebocoran tenant_id antar service, beban ops naik lebih cepat dari tim, panggilan N+1 ke Catalog, webhook payment gateway diproses dobel (butuh idempotency key), race condition status suspend vs transaksi kasir yang masih berjalan.

## Next steps (belum dikerjakan)
1. Refactor `app/` jadi modul identity/catalog/order dengan batas tegas (Fase 0).
2. Rancang skema tabel `subscriptions`/`invoices`/`payment_transactions` untuk modul billing (belum implementasi payment gateway).
3. Scaffold aplikasi Back Office (frontend kedua) di atas endpoint yang sudah ada.
4. Pilih payment gateway (Midtrans/Xendit) untuk penagihan berulang.
5. Desain endpoint Catalog batch (`GET /menu/items?ids=...`) untuk hindari N+1 sebelum ekstraksi service.

## Referensi
- Detail konsep arsitektur: `docs/MICROSERVICES.md`.
- Peta repo & deploy semua app di VPS ini: `/opt/REPOS.md`.
- App lain di proxy Caddy yang sama: Nexafin (`nexafin.id`), NexistHub ERP (`app.nexisthub.id`), Reformer Pilates (`reformeryourbody.com`).
