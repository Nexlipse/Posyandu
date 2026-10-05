# 👶 Dashboard Posyandu (Status Gizi Z-Score WHO)

Dashboard kader posyandu: daftar balita, pencatatan pengukuran bulanan, dan **status gizi otomatis dari z-score weight-for-age WHO** (LMS + interpolasi, ditulis dari nol di `who_lms.py`).

## ⚠️ Disclaimer
Penggunaan menjadi **tanggung jawab masing-masing pengguna**. Status gizi bersifat penapisan, **bukan diagnosis medis**. Lihat [DISCLAIMER.md](DISCLAIMER.md).

## Arsitektur
```
browser ──▶ app.py (Flask) ──┬── who_lms.py (z-score engine, terpisah & testable)
                             └── SQLite (posyandu.db)
```

## Fitur Dashboard
- KPI: total balita, gizi baik, perlu perhatian, gizi buruk, cakupan %
- Z-score otomatis saat input berat → label: Buruk / Kurang / Baik / Lebih
- Riwayat per anak + indikator tren (📈/📉)
- Kategorisasi mengikuti cut-off WHO: z < -3 buruk, z < -2 kurang, dst.

## Menjalankan
```bash
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt
python app.py
# http://localhost:5002
```

## Struktur
```
02-posyandu/
├── app.py                  # Route + SQLite
├── who_lms.py              # Engine z-score (business logic terisolasi)
├── templates/
│   ├── dashboard.html
│   └── riwayat.html
├── requirements.txt
├── README.md
├── LICENSE                 # MIT
└── DISCLAIMER.md
```

## Roadmap
- [ ] Grafik pertumbuhan (chart garis berat vs usia)
- [ ] Ekspor rekap bulanan untuk Puskesmas
