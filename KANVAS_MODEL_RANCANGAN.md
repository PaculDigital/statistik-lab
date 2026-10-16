# 📐 KANVAS MODEL PENELITIAN — RANCANGAN TEKNIS

**Dibuat:** 17 Sep 2026 · **ACC Bos:** pilih mode **elemen siap-pakai** (bukan kanvas bebas)

---

## 🎯 GAGASAN BOS (verbatim)

> *"Atau disiapin elemen 2 nya seperti lingkaran dan panah, panah putus putus, elemen
> mediasi, moderasi, elemen y. Paling seperti itu saja tidak banyak, user tinggal klik
> klik elemen dan sambung panah arah, atau panah titik titik, dan elemen H1, H2 dll."*

> *"Bagaimana bisa tidak user mulai merancang model penelitiannya dulu... user bisa
> menyusun gambar design penelitiannya dulu, agar jelas arahnya, mungkin disempurnakan
> oleh ai"*

**Inti:** jangan kanvas kosong yang bebas. **Sediakan elemen berbentuk** — user tinggal
ketuk, sambung, selesai. **Dibatasi justru yang membuat mudah.**

---

## 🧱 ELEMEN (apa yang disediakan)

| Ikon | Nama di layar | Peran di mesin | Kelas internal |
|---|---|---|---|
| 🟩 | **Variabel Bebas (X)** | penyebab | `x` |
| 🟦 | **Variabel Terikat (Y)** | akibat | `y` |
| 🟨 | **Mediasi (M)** | perantara | `m` |
| 🟪 | **Moderasi (Z)** | memperkuat/melemahkan | `z` |
| ⬜ | **Kontrol (C)** | pengganggu, tidak diuji | `c` |

## 🔗 PENYAMBUNG

| Bentuk | Arti | Kelas |
|---|---|---|
| **→** penuh | hipotesis, DIUJI | `h` |
| **⇢** putus-putus | hubungan TIDAK dihipotesiskan (NH) | `nh` |
| **⤙** masuk ke garis | moderasi (Z mengetes jalur) | `mod` |
| **🏷️ H1, H2…** | label otomatis, urut | — |

## ✋ CARA PAKAI (3 langkah, ramah HP)

1. **Ketuk** elemen → kotak muncul di kanvas
2. **Ketuk** kotak → ketik namanya (mis. "Self-efficacy")
3. **Ketuk** kotak A → **ketuk** kotak B → **panah tersambung** + label H otomatis

Menghapus: ketuk elemen → tombol 🗑️.

---

## 🖼️ GALERI CONTOH BAWAAN (ketuk → langsung muncul)

| Nama | Isi |
|---|---|
| Regresi Sederhana | 1 X → 1 Y |
| Mediasi | X → M → Y |
| Moderasi | X → Y, Z menghadang jalur |
| **Goal-Directed (model Bos)** | 9 kotak · 12 H · 1 NH · 2 keluaran |

---

## ⚠️ PAGAR (JANGAN DILANGGAR)

1. **Hanya bentuk yang MESIN SANGGUP.** Kanvas harus MENOLAK bentuk yang tidak bisa
   dibangun (mis. lingkaran tertutup) dengan pesan ramah — bukan crash.
2. **AI TIDAK BOLEH mengubah struktur.** AI hanya **komentar & usul**; user yang
   memutuskan. Kalau AI bebas mengubah → user lihat model A, jadi model B. **BAHAYA.**
3. **Moderasi = panah ke GARIS**, bukan ke kotak. Di HP: ketuk garis dulu, baru ketuk Z.
   **BELUM DIUJI** — jangan janji sebelum terbukti.
4. **Target sentuh ≥ 44px** di 360px. Kotak & panah harus bisa diketuk jari.

---

## 🚧 BELUM DIPECAHKAN (jujur)

- Panah moderasi di HP (nomer 3 di atas) — rencana ada, **belum terukur**
- Bentuk tidak sah: daftar lengkap yang harus ditolak **belum final**
- Kotak yang sangat banyak (≥15) — apakah kanvas masih terbaca di 360px?

---

## URUTAN KERJA (ACC Bos 17Sep26)

1. ✅ **HP dulu** — perbaiki tampilan HP (preset tumpuk + melebar)
2. ⏳ **Kanvas ringkas** — 5 kotak + 3 penyambung + label H + 4 contoh. **Tanpa AI dulu.**
