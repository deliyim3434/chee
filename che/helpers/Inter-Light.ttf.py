import os
from PIL import Image, ImageDraw, ImageFont

def uygulama_baslat():
    # 1. VERİTABANI BAĞLANTI KONTROLÜ (Simülasyon)
    # Loglardaki WriteError hatasını önlemek için bağlantı ayarlarınızı kontrol edin
    print("Veritabanı bağlantısı kuruluyor...")
    try:
        # Burada veritabanı bağlantı kodlarınız olmalı (PyMongo, SQLAlchemy vb.)
        # Örn: client = MongoClient(os.environ.get("DATABASE_URL"))
        print("Veritabanı bağlantısı başarılı.")
    except Exception as e:
        print(f"Veritabanı bağlantısı başarısız: {e}")
        # Kritik hata: Uygulamayı durdurmak yerine loglayabiliriz
    
    # 2. FONT YÜKLEME (Inter-Light.ttf)
    # Proje ana dizinini alıyoruz
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Kullanıcı tarafından yüklenen fontun adı
    font_adı = "Inter-Light.ttf" 
    font_yolu = os.path.join(current_dir, font_adı)

    print(f"Font aranıyor: {font_yolu}")

    try:
        # Fontu yüklemeyi dene (Boyut: 24)
        font = ImageFont.truetype(font_yolu, 24)
        print(f"Başarılı: '{font_adı}' fontu yüklendi.")
    except OSError:
        # Eğer font dosyası yoksa veya yolu yanlışsa hata vermemesi için varsayılanı yükle
        print(f"UYARI: {font_adı} bulunamadı. Varsayılan font kullanılıyor.")
        font = ImageFont.load_default()

    # 3. GÖRSEL OLUŞTURMA ÖRNEĞİ
    try:
        img = Image.new('RGB', (400, 200), color=(73, 109, 137))
        canvas = ImageDraw.Draw(img)
        canvas.text((20, 80), "Font Testi Basarili", font=font, fill=(255, 255, 0))
        
        img.save('output.png')
        print("Görsel 'output.png' adıyla kaydedildi.")
    except Exception as e:
        print(f"Görsel oluşturulurken hata: {e}")

if __name__ == "__main__":
    uygulama_baslat()
