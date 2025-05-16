import os
import sqlite3
import sys
from datetime import datetime


class Veritabani:
    def __init__(self, db_name='veritabani.db'):
        self.db_path = os.path.join(os.getcwd(), db_name)

        # Eğer veritabanı dosyası mevcut değilse, bir tane oluştur.
        if not os.path.exists(self.db_path):
            self.create_db()

        self.con = None
        self.cursor = None


    def create_db(self):
        try:
            # Veritabanı dosyasını oluşturma işlemi
            self.con = sqlite3.connect(self.db_path)
            self.cursor = self.con.cursor()
            # Tabloyu oluştur
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS kullanici_bilgileri (
                    tc TEXT PRIMARY KEY, 
                    ad TEXT, 
                    soyad TEXT, 
                    dogumtarihi TEXT,
                    eposta TEXT, 
                    birim TEXT, 
                    nesbitimtarihi TEXT
                )
            ''')
            self.con.commit()
            self.con.close()
        except Exception as e:
            print(f"Veritabanı oluşturulurken hata oluştu: {e}")

    def baglantiAc(self):
        try:
            self.con = sqlite3.connect(self.db_path)
            self.cursor = self.con.cursor()
        except:
            print("Veritabanı Bağlantı Hatası!")

    def baglantiKapat(self):
        try:
            self.con.close()
        except:
            print("Veritabanı Kapatılamadı!")

    def kayitEkle(self, tc, ad, soyad, dogumtarihi, eposta, birim, nesbitimtarihi):
        try:
            if not tc or not ad or not soyad or not dogumtarihi or not eposta or not birim or not nesbitimtarihi:
                print("Eksik bilgi var. Lütfen tüm alanları doldurduğunuzdan emin olun.")
                return 0
            
            self.baglantiAc()
            self.cursor.execute(
                "INSERT INTO kullanici_bilgileri (tc, ad, soyad, dogumtarihi, eposta, birim, nesbitimtarihi) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tc, ad, soyad, dogumtarihi, eposta, birim, nesbitimtarihi)
            )
            self.con.commit()
            print("Kayıt başarılı.")
            self.baglantiKapat()
            return 1
        except Exception as e:
            print(f"Veritabanına veri eklerken hata oluştu: {e}")
            self.baglantiKapat()
            return 0

    def verileriYukle(self):
        self.baglantiAc()
        self.cursor.execute("SELECT tc,ad,soyad,dogumtarihi,eposta,birim,nesbitimtarihi FROM kullanici_bilgileri")
        veriler = self.cursor.fetchall()
        self.baglantiKapat()
        return veriler
    
    def kayitSil(self, tc):
        try:
            if tc:
                self.baglantiAc()
                self.cursor.execute("DELETE FROM kullanici_bilgileri where tc = ?", (tc,))
                self.con.commit()
                self.baglantiKapat()
                return 1
        except:
            return 0
        
    def kayitGuncelle(self, tc, ad, soyad, dogumtarihi, eposta, birim, nesbitimtarihi):
        try:
            self.baglantiAc()
            # TC'yi string olarak kullanıyoruz
            tc_str = str(tc)  # Eğer tc bir sayısal veri olarak geliyorsa string'e çevrilir
            query = """
            UPDATE kullanici_bilgileri
            SET ad = ?, soyad = ?, dogumtarihi = ?, eposta = ?, birim = ?, nesbitimtarihi = ?
            WHERE tc = ?
            """
            self.cursor.execute(query, (ad, soyad, dogumtarihi, eposta, birim, nesbitimtarihi, tc_str))
            self.con.commit()
            self.baglantiKapat()
            return True
        except Exception as e:
            print(f"Güncelleme hatası: {e}")
            return False


    def kayitVarMi(self, tc):
        try:
            self.baglantiAc()
            self.cursor.execute("SELECT 1 FROM kullanici_bilgileri WHERE tc = ?", (tc,))
            varMi = self.cursor.fetchone() is not None
            self.baglantiKapat()
            return varMi
        except Exception as e:
            print(f"Kayıt kontrol hatası: {e}")
            self.baglantiKapat()
            return False

    def nesKayitSorgula(self, tarih1, tarih2):
        try:
            self.baglantiAc()
            # Sorguyu doğru tarih formatıyla oluşturuyoruz
            query = f"SELECT tc,ad,soyad,dogumtarihi,eposta,birim,nesbitimtarihi FROM kullanici_bilgileri WHERE nesbitimtarihi BETWEEN '{tarih1}' AND '{tarih2}'"
            self.cursor.execute(query)
            veriler = self.cursor.fetchall()
            self.baglantiKapat()
            return veriler
            
        except Exception as e:
            print(f"Sorgu hatası: {e}")
            return []
