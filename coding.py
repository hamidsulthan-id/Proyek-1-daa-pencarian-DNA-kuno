"""
FILE 1: coding.py
Berisi kelas data, dua cara pencarian, dan dua cara pengurutan.

  SOLUSI KURANG TEPAT : Brute-Force (geser karakter demi karakter) + Bubble Sort
  SOLUSI TERBAIK      : KMP (Knuth-Morris-Pratt)                  + Merge Sort

Setiap algoritma punya dua versi: NON-REKURSIF (iteratif) dan REKURSIF.
Versi non-rekursif ada di bagian 3 sampai 5, versi rekursif di bagian 7.

Aturan soal yang dipatuhi:
  - Tidak memakai fungsi pencarian bawaan Python (find, index, re) maupun fungsi urut bawaan.
  - Alfabet hanya A, C, G, T.
  - Toleransi mutasi: fragmen cocok jika 100% sama, ATAU hanya berbeda 1 basa
    pada posisi paling ujung kanan fragmen.

Operasi dasar yang dihitung: satu kali membandingkan dua karakter DNA.
"""
from dataclasses import dataclass
from typing import List, Optional

BESAR = 10 ** 9      # dipakai sebagai "indeks tak hingga" untuk fragmen yang tidak ditemukan


# =====================================================================
# 1. KELAS DATA
# =====================================================================
@dataclass
class Dino:
    """Satu baris dataset: satu genom dinosaurus."""
    nomor: int
    nama: str
    sekuens: str


@dataclass
class Temuan:
    """Satu posisi di genom tempat fragmen cocok."""
    nomor: int
    nama: str
    indeks: int          # posisi awal (mulai dari 0)
    exact: bool          # True = 100% sama, False = beda 1 basa di ujung kanan


@dataclass
class HasilPemetaan:
    """Hasil akhir untuk satu fragmen (satu pola)."""
    pola: str
    ditemukan: bool
    nama: str            # "-" jika tidak ditemukan
    nomor: Optional[int]
    indeks: Optional[int]
    cocok: int           # jumlah basa yang cocok (k atau k-1, atau 0)
    panjang: int         # panjang fragmen (k)
    status: str          # "Exact Match" / "End-Mutated" / "Not Found"
    jumlah_temuan: int   # berapa posisi yang cocok secara keseluruhan


class Penghitung:
    """Menyimpan jumlah operasi dasar."""
    def __init__(self):
        self.karakter = 0    # perbandingan karakter (pencarian)
        self.urut = 0        # perbandingan saat pengurutan


# =====================================================================
# 2. VALIDASI FRAGMEN
# =====================================================================
def basa_valid(teks: str) -> bool:
    """True jika semua karakter hanya A, C, G, atau T."""
    for c in teks:
        if not (c == "A" or c == "C" or c == "G" or c == "T"):
            return False
    return True


# =====================================================================
# 3A. PENCARIAN KURANG TEPAT: BRUTE-FORCE (non-rekursif)
#     Geser fragmen satu posisi demi satu posisi, bandingkan karakter satu per satu.
#     Basa terakhir boleh beda, jadi dicek paling akhir.
# =====================================================================
def cari_brute_force(daftar_dino: List[Dino], pola: str, hitung: Penghitung) -> List[Temuan]:
    k = len(pola)
    temuan = []
    for d in daftar_dino:
        g = d.sekuens
        n = len(g)
        for i in range(n - k + 1):                 # semua posisi awal yang muat
            j = 0
            sama = True
            while j < k - 1:                        # k-1 basa pertama harus persis sama
                hitung.karakter += 1
                if g[i + j] != pola[j]:
                    sama = False
                    break
                j += 1
            if sama:
                hitung.karakter += 1                # basa paling kanan (boleh beda 1)
                temuan.append(Temuan(d.nomor, d.nama, i, g[i + k - 1] == pola[k - 1]))
    return temuan


# =====================================================================
# 3B. PENCARIAN TERBAIK: KMP (non-rekursif)
#     KMP dipakai untuk mencari k-1 basa pertama fragmen. Setiap kali ketemu,
#     basa terakhir dicek 1 kali untuk menentukan Exact atau End-Mutated.
# =====================================================================
def buat_tabel_lps(p: str, hitung: Penghitung) -> List[int]:
    """Tabel LPS: panjang awalan terpanjang yang juga akhiran, untuk tiap posisi p."""
    m = len(p)
    lps = [0] * m
    panjang = 0
    i = 1
    while i < m:
        hitung.karakter += 1
        if p[i] == p[panjang]:
            panjang += 1
            lps[i] = panjang
            i += 1
        elif panjang != 0:
            panjang = lps[panjang - 1]
        else:
            lps[i] = 0
            i += 1
    return lps


def cari_kmp(daftar_dino: List[Dino], pola: str, hitung: Penghitung) -> List[Temuan]:
    k = len(pola)
    awalan = pola[:k - 1]            # k-1 basa pertama
    m = len(awalan)
    lps = buat_tabel_lps(awalan, hitung)
    temuan = []
    for d in daftar_dino:
        g = d.sekuens
        n = len(g)
        i = 0                        # posisi di genom
        j = 0                        # posisi di awalan
        while i < n:
            hitung.karakter += 1
            if g[i] == awalan[j]:
                i += 1
                j += 1
                if j == m:           # awalan ditemukan penuh
                    mulai = i - m
                    if mulai + k <= n:          # basa terakhir harus masih ada di genom
                        hitung.karakter += 1
                        temuan.append(Temuan(d.nomor, d.nama, mulai, g[mulai + k - 1] == pola[k - 1]))
                    j = lps[j - 1]
            elif j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return temuan


# =====================================================================
# 4. MEMILIH TEMUAN TERBAIK UNTUK SATU FRAGMEN (pencarian linear)
#    Urutan prioritas: exact dulu, lalu indeks terkecil, lalu nomor terkecil.
# =====================================================================
def temuan_lebih_baik(a: Temuan, b: Temuan) -> bool:
    if a.exact != b.exact:
        return a.exact
    if a.indeks != b.indeks:
        return a.indeks < b.indeks
    return a.nomor < b.nomor


def pilih_terbaik_iteratif(temuan: List[Temuan]) -> Temuan:
    """Pencarian linear nilai terbaik: periksa semua temuan satu per satu (non-rekursif)."""
    terbaik = temuan[0]
    for t in temuan:
        if temuan_lebih_baik(t, terbaik):
            terbaik = t
    return terbaik


def buat_hasil(pola: str, temuan: List[Temuan]) -> HasilPemetaan:
    k = len(pola)
    if len(temuan) == 0:
        return HasilPemetaan(pola, False, "-", None, None, 0, k, "Not Found", 0)
    terbaik = pilih_terbaik_iteratif(temuan)
    if terbaik.exact:
        return HasilPemetaan(pola, True, terbaik.nama, terbaik.nomor, terbaik.indeks,
                             k, k, "Exact Match", len(temuan))
    return HasilPemetaan(pola, True, terbaik.nama, terbaik.nomor, terbaik.indeks,
                         k - 1, k, "End-Mutated", len(temuan))


# =====================================================================
# 5. PENGURUTAN HASIL (non-rekursif: Bubble Sort dan Merge Sort bottom-up;
#    Merge Sort versi rekursif ada di bagian 7)
#    Aturan urutan: skor kemiripan tertinggi dulu, jika sama maka indeks terkecil dulu.
#    Fragmen yang tidak ditemukan (skor 0) otomatis di paling bawah.
# =====================================================================
def harus_sebelum(a: HasilPemetaan, b: HasilPemetaan) -> bool:
    """True jika a harus tampil lebih dulu daripada b (benar-benar lebih dulu, bukan sama)."""
    kiri = a.cocok * b.panjang       # bandingkan a.cocok/a.panjang dengan b.cocok/b.panjang
    kanan = b.cocok * a.panjang      # tanpa pecahan desimal supaya tepat
    if kiri != kanan:
        return kiri > kanan
    ia = a.indeks if a.ditemukan else BESAR
    ib = b.indeks if b.ditemukan else BESAR
    return ia < ib


def bubble_sort(data: List[HasilPemetaan], hitung: Penghitung) -> List[HasilPemetaan]:
    """Solusi kurang tepat: tukar tetangga yang urutannya salah, ulang sampai tidak ada tukar."""
    a = list(data)
    n = len(a)
    for i in range(n - 1):
        ada_tukar = False
        for j in range(n - 1 - i):
            hitung.urut += 1
            if harus_sebelum(a[j + 1], a[j]):
                a[j], a[j + 1] = a[j + 1], a[j]
                ada_tukar = True
        if not ada_tukar:
            break
    return a


def gabung(kiri: List[HasilPemetaan], kanan: List[HasilPemetaan], hitung: Penghitung) -> List[HasilPemetaan]:
    """Gabungkan dua daftar yang sudah terurut menjadi satu daftar terurut (stabil)."""
    hasil = []
    i = 0
    j = 0
    while i < len(kiri) and j < len(kanan):
        hitung.urut += 1
        if harus_sebelum(kanan[j], kiri[i]):
            hasil.append(kanan[j])
            j += 1
        else:
            hasil.append(kiri[i])
            i += 1
    while i < len(kiri):
        hasil.append(kiri[i])
        i += 1
    while j < len(kanan):
        hasil.append(kanan[j])
        j += 1
    return hasil


def merge_sort_iteratif(data: List[HasilPemetaan], hitung: Penghitung) -> List[HasilPemetaan]:
    """Merge Sort tanpa rekursi (bottom-up): gabungkan blok selebar 1, 2, 4, 8, ... sampai satu blok."""
    a = list(data)
    n = len(a)
    lebar = 1
    while lebar < n:
        baru = []
        awal = 0
        while awal < n:
            kiri = a[awal:awal + lebar]
            kanan = a[awal + lebar:awal + 2 * lebar]
            baru.extend(gabung(kiri, kanan, hitung))
            awal += 2 * lebar
        a = baru
        lebar *= 2
    return a


# =====================================================================
# 6. DUA SOLUSI LENGKAP
#    rekursif=False -> semua algoritma versi non-rekursif (bawaan)
#    rekursif=True  -> semua algoritma versi rekursif (bagian 7)
# =====================================================================
def solusi_kurang_tepat(daftar_dino: List[Dino], daftar_pola: List[str], hitung: Penghitung,
                        rekursif: bool = False):
    """Brute-Force + Bubble Sort."""
    cari = cari_brute_force_rekursif if rekursif else cari_brute_force
    urut = bubble_sort_rekursif if rekursif else bubble_sort
    hasil = []
    for pola in daftar_pola:
        hasil.append(buat_hasil(pola, cari(daftar_dino, pola, hitung)))
    return urut(hasil, hitung)


def solusi_terbaik(daftar_dino: List[Dino], daftar_pola: List[str], hitung: Penghitung,
                   rekursif: bool = False):
    """KMP + Merge Sort."""
    cari = cari_kmp_rekursif if rekursif else cari_kmp
    urut = merge_sort if rekursif else merge_sort_iteratif
    hasil = []
    for pola in daftar_pola:
        hasil.append(buat_hasil(pola, cari(daftar_dino, pola, hitung)))
    return urut(hasil, hitung)


# =====================================================================
# 7. VERSI REKURSIF
#    Hasil tiap versi rekursif SAMA dengan versi non-rekursifnya.
#    Untuk teks panjang, kedalaman rekursi besar, jadi program eksperimen
#    menaikkan batas rekursi Python (sys.setrecursionlimit).
# =====================================================================

# ---- 7a. Pilih temuan terbaik (pencarian linear), rekursif ----------
def pilih_terbaik_rekursif(temuan: List[Temuan], i: int = 0, terbaik: Optional[Temuan] = None) -> Temuan:
    if i == len(temuan):                         # kasus dasar: semua sudah diperiksa
        return terbaik
    t = temuan[i]
    if terbaik is None or temuan_lebih_baik(t, terbaik):
        terbaik = t
    return pilih_terbaik_rekursif(temuan, i + 1, terbaik)


# ---- 7b. Brute-Force rekursif ---------------------------------------
def _prefiks_sama_rek(g: str, pola: str, i: int, j: int, k: int, hitung: Penghitung) -> bool:
    """Apakah k-1 basa pertama pola sama dengan g mulai posisi i? (membandingkan basa ke-j dst.)"""
    if j == k - 1:                               # kasus dasar: semua k-1 basa sudah cocok
        return True
    hitung.karakter += 1
    if g[i + j] != pola[j]:                      # kasus dasar: ada yang beda
        return False
    return _prefiks_sama_rek(g, pola, i, j + 1, k, hitung)


def _geser_rek(g: str, pola: str, i: int, k: int, d: Dino, hitung: Penghitung, temuan: List[Temuan]) -> None:
    """Coba cocokkan pola di posisi i, lalu geser ke posisi i+1 secara rekursif."""
    if i > len(g) - k:                           # kasus dasar: tidak ada posisi awal yang muat lagi
        return
    if _prefiks_sama_rek(g, pola, i, 0, k, hitung):
        hitung.karakter += 1
        temuan.append(Temuan(d.nomor, d.nama, i, g[i + k - 1] == pola[k - 1]))
    _geser_rek(g, pola, i + 1, k, d, hitung, temuan)


def cari_brute_force_rekursif(daftar_dino: List[Dino], pola: str, hitung: Penghitung) -> List[Temuan]:
    k = len(pola)
    temuan = []
    for d in daftar_dino:
        _geser_rek(d.sekuens, pola, 0, k, d, hitung, temuan)
    return temuan


# ---- 7c. KMP rekursif -----------------------------------------------
def _lps_rek(p: str, lps: List[int], i: int, panjang: int, hitung: Penghitung) -> None:
    if i >= len(p):                              # kasus dasar: tabel selesai
        return
    hitung.karakter += 1
    if p[i] == p[panjang]:
        lps[i] = panjang + 1
        _lps_rek(p, lps, i + 1, panjang + 1, hitung)
    elif panjang != 0:
        _lps_rek(p, lps, i, lps[panjang - 1], hitung)
    else:
        lps[i] = 0
        _lps_rek(p, lps, i + 1, 0, hitung)


def _kmp_rek(g: str, pola: str, lps: List[int], i: int, j: int,
             d: Dino, hitung: Penghitung, temuan: List[Temuan]) -> None:
    """Satu langkah KMP per panggilan. i = posisi di genom, j = posisi di awalan (k-1 basa pertama pola)."""
    k = len(pola)
    m = k - 1
    n = len(g)
    if i >= n:                                   # kasus dasar: genom habis
        return
    hitung.karakter += 1
    if g[i] == pola[j]:
        i += 1
        j += 1
        if j == m:
            mulai = i - m
            if mulai + k <= n:
                hitung.karakter += 1
                temuan.append(Temuan(d.nomor, d.nama, mulai, g[mulai + k - 1] == pola[k - 1]))
            j = lps[j - 1]
        _kmp_rek(g, pola, lps, i, j, d, hitung, temuan)
    elif j != 0:
        _kmp_rek(g, pola, lps, i, lps[j - 1], d, hitung, temuan)
    else:
        _kmp_rek(g, pola, lps, i + 1, j, d, hitung, temuan)


def cari_kmp_rekursif(daftar_dino: List[Dino], pola: str, hitung: Penghitung) -> List[Temuan]:
    k = len(pola)
    awalan = pola[:k - 1]
    lps = [0] * len(awalan)
    _lps_rek(awalan, lps, 1, 0, hitung)
    temuan = []
    for d in daftar_dino:
        _kmp_rek(d.sekuens, pola, lps, 0, 0, d, hitung, temuan)
    return temuan


# ---- 7d. Bubble Sort rekursif ---------------------------------------
def _satu_putaran_rek(a: List[HasilPemetaan], j: int, batas: int, hitung: Penghitung) -> bool:
    """Satu putaran bubble: bandingkan a[j] dan a[j+1] sampai j = batas. True jika ada penukaran."""
    if j >= batas:                               # kasus dasar: putaran selesai
        return False
    hitung.urut += 1
    tukar = False
    if harus_sebelum(a[j + 1], a[j]):
        a[j], a[j + 1] = a[j + 1], a[j]
        tukar = True
    sisa = _satu_putaran_rek(a, j + 1, batas, hitung)
    return tukar or sisa


def _bubble_rek(a: List[HasilPemetaan], batas: int, hitung: Penghitung) -> None:
    if batas <= 0:                               # kasus dasar: tinggal satu elemen
        return
    if not _satu_putaran_rek(a, 0, batas, hitung):   # kasus dasar: tidak ada tukar = sudah terurut
        return
    _bubble_rek(a, batas - 1, hitung)            # elemen terakhir sudah di tempatnya


def bubble_sort_rekursif(data: List[HasilPemetaan], hitung: Penghitung) -> List[HasilPemetaan]:
    a = list(data)
    _bubble_rek(a, len(a) - 1, hitung)
    return a


# ---- 7e. Merge Sort rekursif ----------------------------------------
def merge_sort(data: List[HasilPemetaan], hitung: Penghitung) -> List[HasilPemetaan]:
    """Bagi dua, urutkan masing-masing secara rekursif, lalu gabungkan."""
    if len(data) <= 1:                           # kasus dasar
        return list(data)
    tengah = len(data) // 2
    kiri = merge_sort(data[:tengah], hitung)
    kanan = merge_sort(data[tengah:], hitung)
    return gabung(kiri, kanan, hitung)