"""
FILE 3: eksperimen.py  -> eksperimen waktu dan ruang (memori), versi non-rekursif vs rekursif.

Jalankan:  python eksperimen.py
Hasil   :  folder hasil_eksperimen/ berisi file CSV tiap percobaan, dan grafik PNG (jika matplotlib ada).

Yang diukur untuk setiap varian dan setiap ukuran input:
  - operasi      : jumlah perbandingan (operasi dasar), dari Penghitung
  - waktu_ms     : waktu eksekusi, median dari beberapa kali jalan (tanpa tracemalloc)
  - memori_kb    : memori puncak TAMBAHAN selama algoritma berjalan (tracemalloc), termasuk tumpukan rekursi
  - kedalaman    : kedalaman maksimum tumpukan panggilan fungsi (sys.setprofile), dikurangi nilai dasar
Waktu dan memori diukur pada jalan yang terpisah supaya tracemalloc tidak mengganggu waktu.
"""
import csv
import os
import random
import statistics
import sys
import time
import tracemalloc

import coding as C
from main import baca_dataset

sys.setrecursionlimit(500000)       # versi rekursif butuh batas yang tinggi untuk input besar

FOLDER = "hasil_eksperimen"
rnd = random.Random(2026)           # seed tetap supaya hasil bisa diulang


# =====================================================================
# ALAT UKUR
# =====================================================================
def ukur_waktu_ms(fn, ulang):
    """Median waktu (milidetik) dari beberapa kali menjalankan fn."""
    hasil = []
    for _ in range(ulang):
        mulai = time.perf_counter()
        fn()
        hasil.append((time.perf_counter() - mulai) * 1000)
    return statistics.median(hasil)


def ukur_memori_kb(fn):
    """Memori puncak tambahan (KB) selama fn berjalan. Input harus sudah dibuat SEBELUM ini."""
    tracemalloc.start()
    fn()
    _, puncak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return puncak / 1024


def ukur_kedalaman(fn):
    """Kedalaman maksimum tumpukan panggilan fungsi Python selama fn berjalan."""
    keadaan = {"d": 0, "maks": 0}

    def pantau(frame, event, arg):
        if event == "call":
            keadaan["d"] += 1
            if keadaan["d"] > keadaan["maks"]:
                keadaan["maks"] = keadaan["d"]
        elif event == "return":
            keadaan["d"] -= 1

    sys.setprofile(pantau)
    fn()
    sys.setprofile(None)
    return keadaan["maks"]


def ukur_semua(nama_varian, skala, k, fungsi_dengan_penghitung, ulang):
    """fungsi_dengan_penghitung(hitung) menjalankan algoritma dan mengisi hitung. Mengembalikan satu baris hasil."""
    hitung = C.Penghitung()
    fungsi_dengan_penghitung(hitung)
    operasi = hitung.karakter + hitung.urut

    def jalan():
        fungsi_dengan_penghitung(C.Penghitung())

    dasar = ukur_kedalaman(lambda: None)
    return {
        "varian": nama_varian, "skala": skala, "k": k, "operasi": operasi,
        "waktu_ms": round(ukur_waktu_ms(jalan, ulang), 4),
        "memori_kb": round(ukur_memori_kb(jalan), 2),
        "kedalaman": ukur_kedalaman(jalan) - dasar,
    }


def simpan(nama, baris):
    os.makedirs(FOLDER, exist_ok=True)
    jalur = os.path.join(FOLDER, nama + ".csv")
    with open(jalur, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(baris[0].keys()))
        w.writeheader()
        w.writerows(baris)
    print(f"  -> {jalur}")


def acak_dna(n):
    return "".join(rnd.choice("ACGT") for _ in range(n))


def satu_genom(teks):
    return [C.Dino(1, "uji", teks)]


# =====================================================================
# PERCOBAAN 1-3: STRING MATCHING (Brute-Force vs KMP, iteratif vs rekursif)
# =====================================================================
VARIAN_CARI = [
    ("Brute-Force iteratif", C.cari_brute_force),
    ("Brute-Force rekursif", C.cari_brute_force_rekursif),
    ("KMP iteratif", C.cari_kmp),
    ("KMP rekursif", C.cari_kmp_rekursif),
]


def jalankan_cari(daftar, teks, pola, ulang):
    baris = []
    for nama, fn in VARIAN_CARI:
        g = satu_genom(teks)
        baris.append(ukur_semua(nama, len(teks), len(pola),
                                lambda h, fn=fn, g=g, pola=pola: fn(g, pola, h), ulang))
    for b in baris:
        daftar.append(b)


def percobaan_teks_acak():
    print("Percobaan 1: teks DNA acak, panjang teks bervariasi (k = 16)")
    hasil = []
    for n in [1000, 2000, 4000, 8000, 16000]:
        pola = acak_dna(16)
        jalankan_cari(hasil, acak_dna(n), pola, ulang=5)
    simpan("1_cari_teks_acak", hasil)
    return hasil


def pola_terburuk(k):
    """k-2 huruf A, lalu C, lalu G. Pada teks 'AAAA...' basa ke-(k-1) selalu gagal -> Brute-Force terlama."""
    return "A" * (k - 2) + "CG"


def percobaan_teks_terburuk():
    print("Percobaan 2: kasus terburuk Brute-Force (teks AAAA...), panjang teks bervariasi (k = 16)")
    hasil = []
    for n in [1000, 2000, 4000, 8000, 16000]:
        jalankan_cari(hasil, "A" * n, pola_terburuk(16), ulang=5)
    simpan("2_cari_kasus_terburuk_n", hasil)
    return hasil


def percobaan_panjang_pola():
    print("Percobaan 3: kasus terburuk, panjang pola bervariasi (teks 4000 basa)")
    hasil = []
    for k in [4, 8, 16, 32, 64, 128]:
        jalankan_cari(hasil, "A" * 4000, pola_terburuk(k), ulang=5)
    simpan("3_cari_kasus_terburuk_k", hasil)
    return hasil


# =====================================================================
# PERCOBAAN 4-5: SORTING (Bubble vs Merge, iteratif vs rekursif)
# =====================================================================
VARIAN_URUT = [
    ("Bubble Sort iteratif", C.bubble_sort),
    ("Bubble Sort rekursif", C.bubble_sort_rekursif),
    ("Merge Sort iteratif", C.merge_sort_iteratif),
    ("Merge Sort rekursif", C.merge_sort),
]


def buat_hasil_acak(r):
    data = []
    for _ in range(r):
        cocok = rnd.choice([0, 15, 16])
        data.append(C.HasilPemetaan("P", cocok > 0, "n" if cocok else "-", 1 if cocok else None,
                                    rnd.randint(0, 240) if cocok else None, cocok, 16, "s", 1))
    return data


def jalankan_urut(daftar, data, nama_kasus, ulang):
    for nama, fn in VARIAN_URUT:
        baris = ukur_semua(nama, len(data), 0, lambda h, fn=fn, data=data: fn(data, h), ulang)
        baris["kasus"] = nama_kasus
        daftar.append(baris)


def percobaan_urut_ukuran():
    print("Percobaan 4: pengurutan data acak, jumlah data bervariasi")
    hasil = []
    for r in [100, 200, 400, 800, 1600]:
        jalankan_urut(hasil, buat_hasil_acak(r), "acak", ulang=3)
    simpan("4_urut_ukuran", hasil)
    return hasil


def percobaan_urut_kasus():
    print("Percobaan 5: pengurutan 800 data, kondisi awal berbeda (acak, sudah terurut, terbalik)")
    hasil = []
    acak = buat_hasil_acak(800)
    terurut = C.merge_sort(acak, C.Penghitung())
    terbalik = terurut[::-1]
    for nama_kasus, data in [("acak", acak), ("sudah terurut", terurut), ("terbalik", terbalik)]:
        jalankan_urut(hasil, data, nama_kasus, ulang=3)
    simpan("5_urut_kasus", hasil)
    return hasil


# =====================================================================
# PERCOBAAN 6: PENCARIAN LINEAR TEMUAN TERBAIK (iteratif vs rekursif)
# =====================================================================
def percobaan_pilih_terbaik():
    print("Percobaan 6: memilih temuan terbaik (pencarian linear), jumlah temuan bervariasi")
    hasil = []
    for m in [1000, 2000, 4000, 8000, 16000]:
        data = [C.Temuan(rnd.randint(1, 100), "x", rnd.randint(0, 255), rnd.random() < 0.5) for _ in range(m)]
        for nama, fn in [("Pilih terbaik iteratif", C.pilih_terbaik_iteratif),
                         ("Pilih terbaik rekursif", C.pilih_terbaik_rekursif)]:
            baris = ukur_semua(nama, m, 0, lambda h, fn=fn, data=data: fn(data), ulang=5)
            hasil.append(baris)
    simpan("6_pilih_terbaik", hasil)
    return hasil


# =====================================================================
# PERCOBAAN 7: DATA NYATA (100 genom dinosaurus), jumlah fragmen bervariasi
# =====================================================================
def buat_fragmen_nyata(dinos, jumlah, k=16):
    daftar = []
    for _ in range(jumlah):
        r = rnd.random()
        if r < 0.15:
            daftar.append(acak_dna(k))                       # kemungkinan besar tidak ada
            continue
        d = rnd.choice(dinos)
        i = rnd.randint(0, len(d.sekuens) - k)
        pola = d.sekuens[i:i + k]
        if r < 0.55:                                         # mutasi 1 basa di ujung kanan
            pola = pola[:-1] + rnd.choice([c for c in "ACGT" if c != pola[-1]])
        daftar.append(pola)
    return daftar


def percobaan_data_nyata():
    print("Percobaan 7: data nyata 100 genom, jumlah fragmen bervariasi (k = 16)")
    dinos = baca_dataset("case1_dino_dna.csv")
    hasil = []
    kombinasi = [
        ("Brute-Force + Bubble iteratif", C.solusi_kurang_tepat, False),
        ("Brute-Force + Bubble rekursif", C.solusi_kurang_tepat, True),
        ("KMP + Merge iteratif", C.solusi_terbaik, False),
        ("KMP + Merge rekursif", C.solusi_terbaik, True),
    ]
    for jumlah in [3, 10, 25, 50, 100]:
        fragmen = buat_fragmen_nyata(dinos, jumlah)
        for nama, fn, rek in kombinasi:
            baris = ukur_semua(nama, jumlah, 16,
                               lambda h, fn=fn, rek=rek, fragmen=fragmen: fn(dinos, fragmen, h, rekursif=rek),
                               ulang=3)
            hasil.append(baris)
    simpan("7_data_nyata", hasil)
    return hasil


# =====================================================================
# GRAFIK (opsional, perlu matplotlib)
# =====================================================================
def buat_grafik(semua):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib belum terpasang, grafik dilewati (python -m pip install matplotlib)")
        return

    def gambar(nama_berkas, judul, data, kolom_y, label_y, kolom_x="skala", label_x="ukuran input", log=True):
        varian = []
        for b in data:
            ada = False
            for v in varian:
                if v == b["varian"]:
                    ada = True
            if not ada:
                varian.append(b["varian"])
        plt.figure(figsize=(6.4, 4))
        for v in varian:
            xs = [b[kolom_x] for b in data if b["varian"] == v]
            ys = [b[kolom_y] for b in data if b["varian"] == v]
            gaya = "--" if "rekursif" in v else "-"
            plt.plot(xs, ys, gaya, marker="o", label=v)
        if log:
            plt.xscale("log")
            plt.yscale("log")
        plt.title(judul)
        plt.xlabel(label_x)
        plt.ylabel(label_y)
        plt.legend(fontsize=8)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(FOLDER, nama_berkas), dpi=150)
        plt.close()

    gambar("g1_waktu_teks_acak.png", "Teks acak: waktu", semua["1"], "waktu_ms", "waktu (ms)")
    gambar("g1_memori_teks_acak.png", "Teks acak: memori", semua["1"], "memori_kb", "memori puncak (KB)")
    gambar("g2_operasi_terburuk.png", "Kasus terburuk: jumlah perbandingan", semua["2"], "operasi", "perbandingan")
    gambar("g2_waktu_terburuk.png", "Kasus terburuk: waktu", semua["2"], "waktu_ms", "waktu (ms)")
    gambar("g4_waktu_urut.png", "Pengurutan acak: waktu", semua["4"], "waktu_ms", "waktu (ms)")
    gambar("g4_memori_urut.png", "Pengurutan acak: memori", semua["4"], "memori_kb", "memori puncak (KB)")
    print(f"  -> grafik PNG ada di folder {FOLDER}")


# =====================================================================
# PROGRAM UTAMA
# =====================================================================
def main():
    semua = {}
    semua["1"] = percobaan_teks_acak()
    semua["2"] = percobaan_teks_terburuk()
    semua["3"] = percobaan_panjang_pola()
    semua["4"] = percobaan_urut_ukuran()
    semua["5"] = percobaan_urut_kasus()
    semua["6"] = percobaan_pilih_terbaik()
    semua["7"] = percobaan_data_nyata()
    buat_grafik(semua)
    print("Selesai.")


if __name__ == "__main__":
    main()