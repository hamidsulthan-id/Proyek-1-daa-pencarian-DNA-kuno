"""
FILE 2: main11.py  -> program utama. Jalankan file INI.

Syarat: coding.py dan case1_dino_dna.csv harus berada satu folder dengan file ini.

Alur program:
  1. Membaca dataset genom dinosaurus dari CSV
  2. Menerima fragmen DNA (ketik sendiri, atau tekan Enter untuk memakai contoh soal)
  3. Menjalankan Solusi Kurang Tepat (Brute-Force + Bubble Sort)
  4. Menjalankan Solusi Terbaik (KMP + Merge Sort)
  5. Menampilkan hasil pemetaan dan perbandingan kedua solusi
"""
import csv
import time

from coding import (Dino, Penghitung, basa_valid,
                    solusi_kurang_tepat, solusi_terbaik)

NAMA_FILE_CSV = "case1_dino_dna.csv"

# Contoh fragmen dari soal (dipakai jika kamu menekan Enter saat ditanya jumlah fragmen)
FRAGMEN_CONTOH = [
    "TTTTTTTTTTTTTTTT",     # tidak ditemukan
    "CTGGCACAAACCGTTG",     # mutasi 1 basa di ujung kanan
    "CTTCGGGCAACTTAAC",     # cocok 100%
]


# =====================================================================
# 1. MEMBACA DATASET
# =====================================================================
def baca_dataset(nama_file):
    daftar = []
    with open(nama_file, newline="", encoding="utf-8") as f:
        for baris in csv.DictReader(f):
            sekuens = baris["sekuens_dna"].strip().upper()
            daftar.append(Dino(int(baris["id"]), baris["nama_latin"].strip(), sekuens))
    return daftar


# =====================================================================
# 2. INPUT FRAGMEN DARI PENGGUNA
# =====================================================================
def minta_fragmen(daftar_dino):
    panjang_genom = len(daftar_dino[0].sekuens)

    print("Masukkan jumlah fragmen DNA (k), atau tekan Enter untuk memakai contoh soal.")
    teks = input("Jumlah fragmen: ").strip()
    if teks == "":
        return list(FRAGMEN_CONTOH)

    while not teks.isdigit() or int(teks) < 1:
        teks = input("Masukkan angka bulat minimal 1: ").strip()
    jumlah = int(teks)

    daftar = []
    for nomor in range(1, jumlah + 1):
        while True:
            pola = input(f"Fragmen ke-{nomor} (hanya A, C, G, T): ").strip().upper()
            if len(pola) < 2:
                print("  Fragmen minimal 2 basa.")
            elif len(pola) > panjang_genom:
                print(f"  Fragmen tidak boleh lebih panjang dari genom ({panjang_genom} basa).")
            elif not basa_valid(pola):
                print("  Fragmen hanya boleh berisi huruf A, C, G, atau T.")
            else:
                daftar.append(pola)
                break
    return daftar


# =====================================================================
# 3. MENAMPILKAN HASIL
# =====================================================================
def tampilkan_hasil(judul, hasil_terurut, hitung, waktu_detik):
    print(f"\n{judul}")
    print("=== HASIL PEMETAAN FRAGMEN DNA (TERURUT SKOR TERTINGGI) ===")
    for urutan, h in enumerate(hasil_terurut, start=1):
        persen = h.cocok * 100 / h.panjang
        nomor = h.nomor if h.ditemukan else "-"
        indeks = h.indeks if h.ditemukan else "-"
        print(f'{urutan}. Pola: "{h.pola}"')
        print(f"   Nama Latin: {h.nama}")
        print(f"   Nomor: {nomor}")
        print(f"   Indeks: {indeks}")
        print(f"   Skor Kemiripan: {persen:.1f}% ({h.cocok}/{h.panjang})")
        print(f"   Status: {h.status}")
        if h.jumlah_temuan > 1:
            print(f"   Catatan: ada {h.jumlah_temuan} posisi cocok, yang ditampilkan adalah yang terbaik")
        print()
    print("Metrik Eksekusi:")
    print(f"- Total Operasi Dasar (Perbandingan Karakter): {hitung.karakter} operasi")
    print(f"- Perbandingan saat pengurutan: {hitung.urut} operasi")
    print(f"- Waktu eksekusi: {waktu_detik * 1000:.3f} ms")


def hasil_sama(a, b):
    """Cek apakah dua daftar hasil isinya sama persis."""
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True


# =====================================================================
# PROGRAM UTAMA
# =====================================================================
def main():
    daftar_dino = baca_dataset(NAMA_FILE_CSV)
    print(f"Dataset terbaca: {len(daftar_dino)} genom dinosaurus, "
          f"masing-masing {len(daftar_dino[0].sekuens)} basa.\n")

    daftar_pola = minta_fragmen(daftar_dino)
    print(f"\nInput patterns (Fragmen DNA, k = {len(daftar_pola)}, n = {len(daftar_pola[0])}):")
    for i, pola in enumerate(daftar_pola, start=1):
        print(f'  {i}. "{pola}"')

    # Solusi kurang tepat
    hitung_a = Penghitung()
    mulai = time.perf_counter()
    hasil_a = solusi_kurang_tepat(daftar_dino, daftar_pola, hitung_a)
    waktu_a = time.perf_counter() - mulai

    # Solusi terbaik
    hitung_b = Penghitung()
    mulai = time.perf_counter()
    hasil_b = solusi_terbaik(daftar_dino, daftar_pola, hitung_b)
    waktu_b = time.perf_counter() - mulai

    tampilkan_hasil("##### SOLUSI KURANG TEPAT (Brute-Force + Bubble Sort) #####", hasil_a, hitung_a, waktu_a)
    tampilkan_hasil("##### SOLUSI TERBAIK (KMP + Merge Sort) #####", hasil_b, hitung_b, waktu_b)

    print("\n##### PERBANDINGAN KEDUA SOLUSI #####")
    print(f"{'':<28}{'Brute-Force + Bubble':>22}{'KMP + Merge Sort':>20}")
    print(f"{'Perbandingan karakter':<28}{hitung_a.karakter:>22}{hitung_b.karakter:>20}")
    print(f"{'Perbandingan pengurutan':<28}{hitung_a.urut:>22}{hitung_b.urut:>20}")
    print(f"{'Waktu (ms)':<28}{waktu_a * 1000:>22.3f}{waktu_b * 1000:>20.3f}")
    print("Hasil kedua solusi sama persis:", "YA" if hasil_sama(hasil_a, hasil_b) else "TIDAK")


if __name__ == "__main__":
    main()