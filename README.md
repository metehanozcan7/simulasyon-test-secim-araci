# Simülasyon Tabanlı İstatistiksel Test Seçim Aracı

İki örneklem karşılaştırma testlerinin (Student t, Welch t, Mann-Whitney U, permütasyon, bootstrap-t) farklı veri koşulları altında (çarpıklık, ağır kuyruk, aykırı değer kontaminasyonu, heteroskedastisite, dengesiz örneklem büyüklüğü) Tip I hata kontrolünü ve istatistiksel gücünü Monte Carlo simülasyonuyla sistematik olarak inceleyen bir çalışma.

**Durum:** Aktif geliştirme — simülasyon tamamlandı, görselleştirme/karar aracı/rapor aşamaları devam ediyor.

## Öne Çıkan Bulgular

180 koşul × 3.000 tekrarlık simülasyondan (Monte Carlo standart hatası her tahminle birlikte raporlanmıştır):

1. **Student t-testi, büyük varyans büyük örneklemle eşleştiğinde aşırı muhafazakâr kalıyor.** Normal dağılım, varyans oranı=4, n=(10,50) koşulunda Tip I hata oranı **0.0027** (MC SE=0.0009) — nominal 0.05'in çok altında. Welch aynı koşulda **0.0577**, beklenen düzeyde. Bu muhafazakârlık gücü de doğrudan etkiliyor: aynı koşulda d=0.2 için Student t gücü sadece **0.019**, Welch **0.130**, permütasyon **0.111** — yaklaşık 6-7 kat fark.

2. **Mann-Whitney U, çarpık dağılım + yüksek varyans oranında beklenmedik şekilde şişiyor.** Skew-normal dağılım, varyans oranı=4, n=(100,100) koşulunda Tip I hata oranı **0.194** (MC SE=0.0072) — nominal hatanın neredeyse 4 katı, Welch aynı koşulda 0.0493. Bu, "Mann-Whitney her zaman t-testinin güvenli alternatifidir" şeklindeki yaygın varsayımı doğrudan çürütüyor: test aslında ortalama eşitliğini değil stokastik eşitliği (P(X>Y)=0.5) test ediyor, ve heteroskedastisite + çarpıklık birlikte bu iki hipotezi ayrıştırabiliyor.

3. **Ağır kuyruklu dağılımlarda Mann-Whitney gerçek bir güç avantajı sağlıyor.** t-dağılımı (df=5), dengeli varyans, d=0.5 koşulunda n=30 için güç Mann-Whitney'de **0.554** (MC SE=0.0091), Student t'de 0.490; n=100'de **0.973** (MC SE=0.0030) vs 0.933. Aynı zamanda saf normal veride Mann-Whitney küçük örneklemde hafif geride kalıyor (n=10, d=0.5: 0.156 vs Student t'nin 0.183) — beklenen göreli etkinlik kaybı.

*(Welch t, studentized permütasyon ve bootstrap-t testleri, test edilen tüm 180 koşulda Tip I hata oranını 0.032–0.062 aralığında tutarak sağlamlıklarını korudu.)*

## Metodoloji

- **Hedef parametre:** Tüm testler aynı veri üretim çerçevesi (lokasyon kayması) altında karşılaştırılmıştır. Mann-Whitney U'nun null hipotezinin (stokastik eşitlik) diğer testlerden (ortalama eşitliği) farklı olduğu, Bulgu 2'nin de gösterdiği gibi, açıkça not edilmiştir.
- **Dağılımlar:** Normal, skew-normal (α=5), t-dağılımı (df=5), kontaminasyon karışımı (%95 N(0,1) + %5 N(0,9)) — her biri `hedef_varyans=1` referansına standardize edilmiştir, böylece etki büyüklüğü (Cohen's d) tüm koşullarda karşılaştırılabilir kalır.
- **Etki büyüklüğü uygulaması:** n1/n2 ağırlıklı pooled SD (Student t-testinin kendi pooled variance tahmincisiyle aynı formül).
- **Permütasyon testi:** Studentized (Welch istatistiğine dayalı) — ham ortalama-farkı versiyonu heteroskedastisite altında Student t ile aynı Tip I hata riskini taşıdığı için tercih edilmemiştir.
- **Bootstrap testi:** Bootstrap-t (studentized bootstrap) — percentile bootstrap yerine, çarpık/ağır kuyruklu koşullarda daha yüksek doğruluk sağladığı için.
- **Tekrarlanabilirlik:** Her koşul kendi sabit `seed`'i ile çalışır (`base_seed + kosul_indeksi`); tüm sonuçlar birebir yeniden üretilebilir.

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma

Hızlı doğrulama (kurulumun doğru olduğunu birkaç saniyede kontrol eder):

```bash
python simulasyon_cekirdek.py
```

Tam simülasyon (180 koşul, 3.000 tekrar/koşul — 2 çekirdekli bir makinede ~50 dakika sürer, kasıtlı olarak elle tetiklenir):

```bash
python -c "from simulasyon_cekirdek import tam_simulasyonu_calistir; tam_simulasyonu_calistir()"
```

Sonuçlar `simulasyon_sonuclari.csv` dosyasına kaydedilir.

## Proje Yapısı

```
├── simulasyon_cekirdek.py      # Çekirdek simülasyon kodu (dağılımlar, testler, grid)
├── simulasyon_sonuclari.csv    # 180 koşulun tam sonuçları
├── notebooks/                  # Geliştirme sürecindeki Colab not defterleri
├── rapor/                      # LaTeX teknik rapor (hazırlanıyor)
├── README.md
└── requirements.txt
```

## Yapılacaklar

- [x] Dağılım fonksiyonları (varyans standardizasyonu dahil)
- [x] Beş test fonksiyonu (permütasyon ve bootstrap'ın studentized versiyonları)
- [x] Tam simülasyon çalıştırması (180 koşul, 3.000 tekrar)
- [x] İlk bulgu analizi (Tip I hata + güç)
- [ ] Görselleştirme (güç eğrileri, Tip I hata ısı haritaları)
- [ ] Simülasyon sonuçlarına dayalı test önerisi aracı (`onerilen_test()`)
- [ ] pytest birim testleri
- [ ] LaTeX teknik rapor
- [ ] Gerçek veriyle örnek olay incelemesi (case study)

## Kaynaklar

- Delacre, M., Lakens, D., & Leys, C. (2017). *Why psychologists should by default use Welch's t-test instead of Student's t-test.* International Review of Social Psychology.
- Fagerland, M. W., & Sandvik, L. (2009). *Performance of five two-sample location tests for skewed distributions with unequal variances.* Contemporary Clinical Trials.
- Wilcox, R. R. — *Introduction to Robust Estimation and Hypothesis Testing.*
