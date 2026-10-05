"""
Dashboard Posyandu — pencatatan balita, pengukuran bulanan, status gizi z-score WHO.
Stack: Flask + SQLite + modul who_lms.py (business logic terpisah).
"""
from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, url_for

from who_lms import status_gizi, z_score_weight

DB = Path(__file__).parent / "posyandu.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS balita (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nama TEXT NOT NULL,
  gender TEXT NOT NULL CHECK(gender IN ('L','P')),
  tgl_lahir TEXT NOT NULL,
  nama_ortu TEXT DEFAULT '',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS pengukuran (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  balita_id INTEGER NOT NULL REFERENCES balita(id),
  tanggal TEXT NOT NULL,
  berat_kg REAL NOT NULL,
  tinggi_cm REAL DEFAULT 0,
  z_score REAL,
  status TEXT
);
"""

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.executescript(SCHEMA)
    return g.db


@app.teardown_appcontext
def close_db(_e=None):
    db = g.pop("db", None)
    if db:
        db.close()


def usia_bulan(tgl_lahir: str, ref: date | None = None) -> int:
    lahir = date.fromisoformat(tgl_lahir)
    ref = ref or date.today()
    months = (ref.year - lahir.year) * 12 + (ref.month - lahir.month)
    return max(0, months - (1 if ref.day < lahir.day else 0))


@app.route("/")
def dashboard():
    db = get_db()
    balita_list = db.execute("SELECT * FROM balita ORDER BY nama").fetchall()

    # Status terkini tiap balita
    rows = []
    counts = {"ok": 0, "warning": 0, "danger": 0}
    for b in balita_list:
        m = db.execute(
            "SELECT * FROM pengukuran WHERE balita_id=? ORDER BY tanggal DESC LIMIT 1", (b["id"],)
        ).fetchone()
        age = usia_bulan(b["tgl_lahir"])
        rows.append({"balita": b, "ukur": m, "usia": age})
        if m and m["status"]:
            cls = {"Berat Badan Buruk": "danger", "Berat Badan Kurang": "warning",
                   "Gizi Baik": "ok"}.get(m["status"], "warning")
            counts[cls] += 1
        else:
            counts["warning"] += 1  # belum diukur = perlu perhatian

    total = len(rows)
    stats = {
        "balita": total,
        "gizi_baik": counts["ok"],
        "perlu_perhatian": counts["warning"],
        "buruk": counts["danger"],
        "persen_baik": round(counts["ok"] / total * 100) if total else 0,
    }
    return render_template("dashboard.html", rows=rows, stats=stats, today=date.today(), tab="dashboard")


@app.route("/balita", methods=["POST"])
def tambah_balita():
    db = get_db()
    db.execute("INSERT INTO balita (nama, gender, tgl_lahir, nama_ortu) VALUES (?,?,?,?)", (
        request.form["nama"], request.form["gender"], request.form["tgl_lahir"],
        request.form.get("nama_ortu", "")))
    db.commit()
    return redirect(url_for("dashboard"))


@app.route("/ukur", methods=["POST"])
def ukur():
    db = get_db()
    balita_id = request.form.get("balita_id", type=int)
    berat = request.form.get("berat_kg", type=float)
    b = db.execute("SELECT * FROM balita WHERE id=?", (balita_id,)).fetchone()
    if b and berat:
        age = usia_bulan(b["tgl_lahir"])
        z = z_score_weight(age, berat, b["gender"])
        status, _ = status_gizi(z)
        db.execute(
            "INSERT INTO pengukuran (balita_id, tanggal, berat_kg, tinggi_cm, z_score, status) VALUES (?,?,?,?,?,?)",
            (balita_id, date.today().isoformat(), berat,
             request.form.get("tinggi_cm", type=float) or 0, round(z, 2), status))
        db.commit()
    return redirect(url_for("dashboard"))


@app.route("/riwayat/<int:balita_id>")
def riwayat(balita_id):
    db = get_db()
    b = db.execute("SELECT * FROM balita WHERE id=?", (balita_id,)).fetchone()
    data = db.execute(
        "SELECT * FROM pengukuran WHERE balita_id=? ORDER BY tanggal", (balita_id,)).fetchall()
    return render_template("riwayat.html", balita=b, data=data, tab="riwayat")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
