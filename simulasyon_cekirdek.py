"""
simulasyon_cekirdek.py
Simülasyon Tabanlı İstatistiksel Test Seçim Aracı -- Çekirdek Kod (Master Referans)

Bu dosya, projenin şu ana kadar birlikte yazılıp Colab'da tek tek test edilerek
doğrulanmış TÜM parçalarının, tutarlı ve tekrarsız halidir. Colab notebook'unda
karışıklık/hata olursa, tüm hücreleri silip buradaki blokları sırayla yeniden
yapıştırmak en garantili çözümdür.

Her blok, aşağıda "BLOK N" başlığıyla ayrılmış -- Colab'da her biri kendi
hücresine gidecek şekilde tasarlandı.
"""

# ============================================================
# BLOK 1: Kütüphaneler
# ============================================================
import numpy as np
from scipy import stats
import itertools


# ============================================================
# BLOK 2: Dağılım Örnekleme Fonksiyonları (4 tanesi)
# Hepsi 'hedef_varyans=1' iken popülasyon varyansı tam 1 olacak
# şekilde standardize edilmiştir (bkz. etki büyüklüğü karşılaştırılabilirliği).
# Hepsi 'rng' parametresi alır (tekrarlanabilirlik için).
# ============================================================

def normal_ornekle(n, hedef_varyans=1, rng=None):
    rng = rng or np.random.default_rng()
    std = np.sqrt(hedef_varyans)
    return rng.normal(0, std, n)


def skew_normal_ornekle(n, alpha=5, hedef_varyans=1, rng=None):
    rng = rng or np.random.default_rng()
    delta = alpha / np.sqrt(1 + alpha**2)
    varyans_katsayisi = 1 - (2 * delta**2) / np.pi
    omega = np.sqrt(hedef_varyans / varyans_katsayisi)
    veri = stats.skewnorm.rvs(a=alpha, scale=omega, size=n, random_state=rng)
    teorik_ortalama = stats.skewnorm.mean(a=alpha, scale=omega)
    return veri - teorik_ortalama


def t_dagilimi_ornekle(n, df=5, hedef_varyans=1, rng=None):
    rng = rng or np.random.default_rng()
    scale = np.sqrt(hedef_varyans * (df - 2) / df)
    return stats.t.rvs(df=df, scale=scale, size=n, random_state=rng)


def kontamine_ornekle(n, oran=0.05, kont_orani=3, hedef_varyans=1, rng=None):
    rng = rng or np.random.default_rng()
    ana_std = np.sqrt(hedef_varyans / ((1 - oran) + oran * kont_orani**2))
    kont_std = kont_orani * ana_std
    kontaminasyon_maskesi = rng.random(n) < oran
    veri = rng.normal(0, ana_std, n)
    veri[kontaminasyon_maskesi] = rng.normal(0, kont_std, kontaminasyon_maskesi.sum())
    return veri


# ============================================================
# BLOK 3: Etki Büyüklüğü Yardımcı Fonksiyonları
# ============================================================

def pooled_std_hesapla(n1, n2, varyans1, varyans2):
    dof = n1 + n2 - 2
    pooled_varyans = ((n1 - 1) * varyans1 + (n2 - 1) * varyans2) / dof
    return np.sqrt(pooled_varyans)


def etki_buyuklugu_uygula(n1, n2, varyans1, varyans2, d):
    pooled = pooled_std_hesapla(n1, n2, varyans1, varyans2)
    return d * pooled


# ============================================================
# BLOK 4: İki Grup Üretme
# ============================================================

def iki_grup_uret(dagilim_fonksiyonu, n1, n2, varyans_orani, d, rng=None):
    rng = rng or np.random.default_rng()
    grup1 = dagilim_fonksiyonu(n1, hedef_varyans=1, rng=rng)
    kayma = etki_buyuklugu_uygula(n1, n2, varyans1=1, varyans2=varyans_orani, d=d)
    grup2 = dagilim_fonksiyonu(n2, hedef_varyans=varyans_orani, rng=rng) + kayma
    return grup1, grup2


# ============================================================
# BLOK 5: Beş Test Fonksiyonu
# ============================================================

def student_t_testi(grup1, grup2):
    return stats.ttest_ind(grup1, grup2, equal_var=True)


def welch_t_testi(grup1, grup2):
    return stats.ttest_ind(grup1, grup2, equal_var=False)


def mann_whitney_testi(grup1, grup2):
    return stats.mannwhitneyu(grup1, grup2, alternative="two-sided")


def welch_istatistigi_hesapla(x, y):
    n1, n2 = len(x), len(y)
    var1, var2 = np.var(x, ddof=1), np.var(y, ddof=1)
    se = np.sqrt(var1 / n1 + var2 / n2)
    return (np.mean(x) - np.mean(y)) / se


def studentized_permutasyon_testi(grup1, grup2, n_permutasyon=500, rng=None):
    rng = rng or np.random.default_rng()
    x1, x2 = np.asarray(grup1), np.asarray(grup2)
    n1, n2 = len(x1), len(x2)
    n_toplam = n1 + n2
    t_gozlenen = welch_istatistigi_hesapla(x1, x2)
    birlesik = np.concatenate([x1, x2])
    permutasyon_indeksleri = np.argsort(rng.random((n_permutasyon, n_toplam)), axis=1)
    karisik = birlesik[permutasyon_indeksleri]
    perm_grup1, perm_grup2 = karisik[:, :n1], karisik[:, n1:]
    ort1, ort2 = perm_grup1.mean(axis=1), perm_grup2.mean(axis=1)
    var1, var2 = perm_grup1.var(axis=1, ddof=1), perm_grup2.var(axis=1, ddof=1)
    se = np.sqrt(var1 / n1 + var2 / n2)
    t_perm = (ort1 - ort2) / se
    p_degeri = np.mean(np.abs(t_perm) >= np.abs(t_gozlenen))
    return t_gozlenen, p_degeri


def bootstrap_t_testi(grup1, grup2, B=500, rng=None):
    rng = rng or np.random.default_rng()
    n1, n2 = len(grup1), len(grup2)
    x1, x2 = np.asarray(grup1), np.asarray(grup2)
    ort1, ort2 = x1.mean(), x2.mean()
    t_gozlenen = welch_istatistigi_hesapla(x1, x2)
    x1_merkezli = x1 - ort1
    x2_merkezli = x2 - ort2
    idx1 = rng.integers(0, n1, size=(B, n1))
    idx2 = rng.integers(0, n2, size=(B, n2))
    boot1 = x1_merkezli[idx1]
    boot2 = x2_merkezli[idx2]
    boot_se = np.sqrt(boot1.var(axis=1, ddof=1) / n1 + boot2.var(axis=1, ddof=1) / n2)
    t_star = (boot1.mean(axis=1) - boot2.mean(axis=1)) / boot_se
    p_degeri = np.mean(np.abs(t_star) >= np.abs(t_gozlenen))
    return t_gozlenen, p_degeri


def tum_testleri_calistir(grup1, grup2, rng=None):
    rng = rng or np.random.default_rng()
    return {
        "student_t": student_t_testi(grup1, grup2)[1],
        "welch_t": welch_t_testi(grup1, grup2)[1],
        "mann_whitney": mann_whitney_testi(grup1, grup2)[1],
        "permutasyon": studentized_permutasyon_testi(grup1, grup2, rng=rng)[1],
        "bootstrap_t": bootstrap_t_testi(grup1, grup2, rng=rng)[1],
    }


# ============================================================
# BLOK 6: Tek Koşulu 'tekrar' Kez Çalıştırma
# ============================================================

def tek_kosul_calistir(dagilim_fonksiyonu, n1, n2, varyans_orani, d, tekrar=100, rng=None):
    rng = rng or np.random.default_rng()
    testler = ["student_t", "welch_t", "mann_whitney", "permutasyon", "bootstrap_t"]
    ret_sayisi = {test: 0 for test in testler}
    for _ in range(tekrar):
        grup1, grup2 = iki_grup_uret(dagilim_fonksiyonu, n1, n2, varyans_orani, d, rng=rng)
        p_degerleri = tum_testleri_calistir(grup1, grup2, rng=rng)
        for test in testler:
            if p_degerleri[test] < 0.05:
                ret_sayisi[test] += 1
    return {test: ret_sayisi[test] / tekrar for test in testler}


# ============================================================
# BLOK 7: Simülasyon Grid Tanımı (Config Değerleri)
# Bu değerler, konuşmalarımız sırasında birlikte karar verilmiş
# NİHAİ değerlerdir:
#   - kontaminasyon oranı: 0.05 (kullanıcı kararı)
#   - t-dağılımı df: 5 (kullanıcı kararı, df=3 sonra eklenecek)
#   - tekrar_sayisi: 3000 (5000'den düşürüldü, MC SE hâlâ yeterli: ~0.004)
#   - n_permutasyon / B: 500 (2000'den düşürüldü, hız için)
# ============================================================

dagilim_listesi = {
    "normal": normal_ornekle,
    "skew_normal": skew_normal_ornekle,
    "t_dagilimi": t_dagilimi_ornekle,
    "kontamine": kontamine_ornekle,
}

varyans_oranlari = [1, 2, 4]
n_kombinasyonlari = [(10, 10), (30, 30), (100, 100), (10, 50), (15, 60)]
etki_buyuklukleri = [0, 0.2, 0.5]
tekrar_sayisi = 3000


def kosul_gridini_olustur():
    return list(itertools.product(
        dagilim_listesi.keys(),
        varyans_oranlari,
        n_kombinasyonlari,
        etki_buyuklukleri,
    ))


# ============================================================
# BLOK 8: Tek Bir Koşulu İşleyip Sonuç Satırı Üretme
# (Her koşul kendi sabit tohumunu kullanır -- tekrarlanabilirlik)
# ============================================================

def tek_kosulu_isle(kosul, kosul_indeksi, base_seed=42):
    dagilim_adi, varyans_orani, n_bilgisi, d = kosul
    n1, n2 = n_bilgisi
    dagilim_fonksiyonu = dagilim_listesi[dagilim_adi]
    rng = np.random.default_rng(base_seed + kosul_indeksi)

    ret_oranlari = tek_kosul_calistir(
        dagilim_fonksiyonu, n1, n2, varyans_orani, d,
        tekrar=tekrar_sayisi, rng=rng,
    )

    satir = {
        "kosul_id": kosul_indeksi, "dagilim": dagilim_adi, "varyans_orani": varyans_orani,
        "n1": n1, "n2": n2, "etki_buyuklugu": d,
    }
    satir.update(ret_oranlari)
    return satir


# ============================================================
# BLOK 9: Hızlı Doğrulama (kurulumun doğru olduğunu kontrol eder,
# tam simülasyondan önce birkaç saniyede çalışır)
# ============================================================

def hizli_dogrulama():
    grid = kosul_gridini_olustur()
    print(f"Toplam koşul sayısı: {len(grid)} (beklenen: 180)")

    a = tek_kosulu_isle(grid[0], kosul_indeksi=0)
    b = tek_kosulu_isle(grid[0], kosul_indeksi=0)
    print("Sabit seed ile birebir aynı mı:", a == b, "(beklenen: True)")
    print("Örnek sonuç (d=0, normal, n=10,10):", a)


# ============================================================
# BLOK 10: Tam Simülasyon Çalıştırması (180 koşul, paralel)
# README'de belirtilen ~50 dakikalık çalışma budur -- bu blok
# çalıştırılınca simulasyon_sonuclari.csv üretir/günceller.
# ============================================================

def tam_simulasyonu_calistir(cikti_dosyasi="simulasyon_sonuclari.csv", n_jobs=-1):
    from joblib import Parallel, delayed
    import pandas as pd
    import time

    grid = kosul_gridini_olustur()
    print(f"Tam simülasyon başlıyor: {len(grid)} koşul, {tekrar_sayisi} tekrar/koşul.")
    baslangic = time.time()

    tum_sonuclar = Parallel(n_jobs=n_jobs, verbose=5)(
        delayed(tek_kosulu_isle)(kosul, i) for i, kosul in enumerate(grid)
    )

    toplam_sure = time.time() - baslangic
    print(f"\nBitti. Toplam süre: {toplam_sure/60:.1f} dakika")

    sonuc_df = pd.DataFrame(tum_sonuclar)
    sonuc_df.to_csv(cikti_dosyasi, index=False)
    print(f"{len(sonuc_df)} satır kaydedildi: {cikti_dosyasi}")
    return sonuc_df


if __name__ == "__main__":
    hizli_dogrulama()
    print("\nTam simülasyonu çalıştırmak için: tam_simulasyonu_calistir()")
    print("(Doğrudan bu script'ten otomatik başlatılmıyor -- ~50 dakika sürdüğü için")
    print(" kasıtlı olarak elle çağrılması gerekiyor. Örnek: python -c")
    print(' "from simulasyon_cekirdek import tam_simulasyonu_calistir; tam_simulasyonu_calistir()"')
