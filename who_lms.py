"""Perhitungan status gizi berbasis z-score (referensi WHO Child Growth Standards).

Z-score weight-for-age: z = (x - median) / L... versi sederhana memakai
nilai L/M/S weight-for-age boys & girls 0-60 bulan (subset titik usia utama,
interpolasi linear antar bulan). Untuk produksi: pakai dataset LMS lengkap WHO.
"""
from __future__ import annotations

# Titik usia (bulan): (L, M, S) — weight-for-age
# Sumber nilai: WHO 2006 (boys table wfa), disederhanakan ke titik 6 bulanan.
LMS_BOYS = {
    0: (0.3487, 3.3464, 0.14602), 6: (-0.3079, 7.9340, 0.12269),
    12: (-0.2131, 9.6479, 0.11316), 18: (-0.2352, 10.9385, 0.11080),
    24: (-0.1521, 12.1515, 0.11221), 36: (-0.0538, 14.3429, 0.11677),
    48: (0.0323, 16.3489, 0.12154), 60: (0.1061, 18.2683, 0.12571),
}
LMS_GIRLS = {
    0: (0.3809, 3.2322, 0.14171), 6: (-0.3811, 7.2970, 0.13000),
    12: (-0.1984, 8.9481, 0.12237), 18: (-0.2043, 10.2445, 0.11975),
    24: (-0.1399, 11.4775, 0.12060), 36: (-0.0728, 13.8425, 0.12402),
    48: (0.0111, 15.9750, 0.12738), 60: (0.1246, 17.9365, 0.13031),
}


def _lms_at(table: dict, age_months: int) -> tuple[float, float, float]:
    """Interpolasi linear L, M, S pada usia tertentu."""
    ages = sorted(table)
    lo = max(a for a in ages if a <= age_months)
    hi = min(a for a in ages if a >= age_months)
    if lo == hi:
        return table[lo]
    t = (age_months - lo) / (hi - lo)
    l_lo, m_lo, s_lo = table[lo]
    l_hi, m_hi, s_hi = table[hi]
    return tuple(l_lo + (l_hi - l_lo) * t for l_lo, l_hi in zip((l_lo, m_lo, s_lo), (l_hi, m_hi, s_hi)))


def z_score_weight(age_months: int, weight_kg: float, gender: str) -> float:
    """Z-score weight-for-age. gender: 'L' (laki) / 'P' (perempuan)."""
    table = LMS_BOYS if gender == "L" else LMS_GIRLS
    L, M, S = _lms_at(table, age_months)
    if L == 0:
        return (weight_kg / M - 1) / S
    return ((weight_kg / M) ** L - 1) / (L * S)


def status_gizi(z: float) -> tuple[str, str]:
    """Kembalikan (label, css_class) dari z-score berat/umur."""
    if z < -3:
        return "Berat Badan Buruk", "danger"
    if z < -2:
        return "Berat Badan Kurang", "warning"
    if z <= 1:
        return "Gizi Baik", "ok"
    if z <= 2:
        return "Berisiko Lebih", "warning"
    return "Berat Badan Lebih", "warning"
