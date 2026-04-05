# Perperok

Perperok, Python ve Tkinter ile yazılmış, tamamen yerel çalışan basit bir PDF şifre kaldırma (unlock) uygulamasıdır.

## Özellikler

- Bir veya birden fazla şifreli PDF seçebilirsiniz.
- Her PDF için ayrı şifre girebilir veya tüm PDF'ler için tek ortak şifre kullanabilirsiniz.
- Şifre alanlarında modern uygulamalardaki gibi "göster/gizle" butonu vardır.
- Çözülen PDF'ler, seçtiğiniz hedef klasöre `*_unlocked.pdf` uzantısıyla kaydedilir.
- İşlem sürecini yüzdelik ilerleme çubuğundan takip edebilirsiniz.
- Uygulama penceresinin üst kısmında **Perperok v1.0.0** başlığını görürsünüz.
- Uygulama tamamen çevrimdışı çalışır; PDF'leriniz hiçbir zaman internete gönderilmez.

---

## 1. Gereksinimler

- macOS, Windows veya Linux
- Python 3.9+ (önerilir)

Yüklü Python sürümünüzü kontrol etmek için:

```bash
python3 --version
```

veya

```bash
python --version
```

---

## 2. Kurulum

1. Projeyi bir klasöre indirin / kopyalayın (örneğin `example123`).
2. Terminali açın ve proje klasörüne geçin:

```bash
cd example123
```

3. (Önerilen) Sanal ortam oluşturun:

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Gerekli paketleri yükleyin (PyPDF2, AES şifreleme için PyCryptodome ve ikon üretimi için Pillow):

```bash
pip install -r requirements.txt
```

---

## 3. Uygulamayı Çalıştırma

Sanal ortam aktifken, proje klasöründe aşağıdaki komutu çalıştırın:

```bash
python app.py
```

veya sisteminizde `python3` komutunu kullanıyorsanız:

```bash
python3 app.py
```

Uygulama açıldığında bir pencere göreceksiniz.

---

## 4. Kullanım

### 4.1. PDF Dosyaları Ekleme

- Üst taraftaki **"PDF Ekle..."** butonuna tıklayın.
- Açılan dosya seçim penceresinden bir veya birden fazla `.pdf` dosyası seçin.
- Seçtiğiniz dosyalar, listede isimleriyle birlikte görünecektir.

### 4.2. Şifre Girme Modları

Uygulamada iki şifre modu vardır:

1. **Her PDF için ayrı şifre** (varsayılan)
   - Bu modda, listedeki her PDF satırında bir şifre alanı görünür.
   - İlgili PDF'in gerçek şifresini bu alana girersiniz.
   - Şifre alanının yanındaki **"Göster"** butonuna tıklayarak, yıldızlı görünümü açıp/kapatabilirsiniz.

2. **Tüm PDF'ler için ortak şifre**
   - **"Tüm PDF'ler için ortak şifre kullan"** kutusunu işaretleyin.
   - Aşağıda **"Ortak Şifre"** alanı aktif olur.
   - Tüm PDF'ler aynı şifreyle korunuyorsa, bu alana bir kez şifre girmeniz yeterlidir.
   - Bu moddayken, listedeki PDF satırlarındaki şifre alanları devre dışı kalır.
   - Kutunun işaretini kaldırdığınızda, satırlardaki şifre alanları tekrar aktif olur.

### 4.3. Hedef Klasör Seçimi

- **"Hedef Klasör"** bölümündeki **"Klasör Seç..."** butonuna tıklayın.
- Çözülen (şifresi kaldırılmış) PDF'lerin kaydedilmesini istediğiniz klasörü seçin.
- Seçtiğiniz klasör yolu, bu bölümde metin olarak gösterilecektir.

### 4.4. Şifreyi Çözme İşlemini Başlatma

1. En az bir PDF dosyası eklediğinizden emin olun.
2. Kullanmak istediğiniz şifre modunu seçin ve gerekli şifre(leri) girin.
3. Hedef klasörü seçtiğinizden emin olun.
4. Pencerenin alt kısmındaki **"Şifreyi Çöz ve Kaydet"** butonuna tıklayın.

İşlem başladığında:

- İlerleme çubuğu (progress bar) yüzdelik olarak güncellenir.
- Alt kısımda, o anda işlenen PDF'in adı ve kaçıncı dosyada olduğunuz gösterilir.
- İşlem bittiğinde, sonuç durumu bir mesaj kutusu ile bildirilir:
  - Tüm dosyalar başarılıysa, başarılı olduğunu belirten bir bilgi mesajı çıkar.
  - Bazı dosyalarda hata varsa, hangi dosyaların neden başarısız olduğu listelenir.

Çıktı dosyaları, seçtiğiniz hedef klasöre şu formatta kaydedilir:

- Orijinal dosya: `ornek.pdf`
- Çözülen dosya: `ornek_unlocked.pdf`

---

## 5. Hata Durumları ve İpuçları

- **Yanlış şifre**: Bir PDF için girilen şifre yanlışsa, o dosya için işlem başarısız olur ve liste halinde raporlanır.
- **Şifre alanı boş**:
  - Ortak şifre modunda ortak şifre alanını boş bırakamazsınız.
  - Her dosya için ayrı şifre modunda, herhangi bir satırda şifre boşsa işlem başlamaz.
- **Dosya bozuk veya desteklenmiyor**: Bazı PDF dosyaları bozuk olabilir veya PyPDF2 tarafından desteklenmeyebilir; bu durumda ilgili dosya hata listesinde gösterilir.

---

## 6. Güvenlik Notları

- Uygulama tamamen **lokalde** çalışır; şifreleriniz ve PDF'leriniz internet üzerinden hiçbir yere gönderilmez.
- Şifreler sadece çalışma esnasında bellek içinde tutulur, disk üzerine kaydedilmez.

---

## 7. İkon Özelleştirme (Opsiyonel)

- İkon üretimi için `pdf_unlocker/assets/butterfly_source.png` dosyası kullanılır.
- Kendi kelebek görselinizi bu dosyayla değiştirerek uygulama ikonunu özelleştirebilirsiniz.
- Uygulama başlarken bu görselden `butterfly_icon.png` üretilir ve pencerenin sol üstünde gösterilir.
- Eğer kaynak görsel bulunamazsa, uygulama ikonsuz olarak sorunsuz şekilde çalışmaya devam eder.

---

## 8. Sık Karşılaşılan Sorunlar

### 7.1. "PyCryptodome is required for AES algorithm" hatası

Bu hata, PDF'in AES ile şifrelenmiş olması ve `pycryptodome` kütüphanesinin yüklü olmaması durumunda görülür. Çözüm:

```bash
pip install -r requirements.txt
```

### 7.2. Uygulama penceresi açılmıyor

- Python sürümünüzün 3.x olduğundan emin olun.
- Komutu proje klasöründe çalıştırdığınızdan emin olun (`app.py` ile aynı klasör).

---

## 9. Lisans

Bu proje kişisel kullanım içindir. İhtiyaçlarınıza göre özgürce düzenleyebilirsiniz.
