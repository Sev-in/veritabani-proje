import sqlite3
import pandas as pd
from veritabani import Veritabani
from PyQt5.QtWidgets import *
from cokluKayitPython import Ui_Form_cokluKayit
from datetime import datetime

vt = Veritabani()

class CokluKayitPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.cokluKayitForm = Ui_Form_cokluKayit()
        self.cokluKayitForm.setupUi(self)
        self.MainWindow = parent

        self.cokluKayitForm.pushButton_geri.clicked.connect(self.geriDon)
        self.cokluKayitForm.pushButton_dosyaSec.clicked.connect(self.excelDosyasiniSec)


    def geriDon(self):
        self.hide()
        if self.MainWindow:
            self.MainWindow.show()

    def excelDosyasiniSec(self):
        dosyaYolu, _ = QFileDialog.getOpenFileName(self, "Excel Dosyasını Seç", "", "Excel Dosyaları (*.xlsx *.xls)")
        
        if dosyaYolu:
            try:
                # Excel dosyasını okuma
                df = pd.read_excel(dosyaYolu, header=None)
                print("İlk birkaç satır:", df.head())

                # Başlık satırını tespit etme
                baslik_satiri = None
                for i, row in df.iterrows():
                    if 'Kimlik No' in row.values or 'Ad' in row.values or 'Soyad' in row.values or 'Soyadı' in row.values:
                        baslik_satiri = i
                        break

                if baslik_satiri is None:
                    raise ValueError("Başlık satırı bulunamadı.")

                df.columns = df.iloc[baslik_satiri]
                df = df.drop(range(baslik_satiri + 1))

                # 'Unnamed' sütunlarını temizleme
                df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
                print("Orijinal sütunlar:", df.columns.tolist())

                # Sütun adlarını eşleştirme
                sutun_eslesmeleri = {
                    'Kimlik No': 'tc', 'T.C. Kimlik No': 'tc', 'TC Kimlik No': 'tc','TC Kimlik No Açık': 'tc', 'TC': 'tc',
                    'Ad': 'ad', 'Adı': 'ad', 'İsim': 'ad', 'Soyad': 'soyad', 'Soyadı': 'soyad', 'Soyisim': 'soyad',
                    'Doğum Tarihi': 'dogumtarihi', 'Doğum Tarihi\n(GG/AA/YYYY)': 'dogumtarihi', 'Kurumsal E-posta': 'eposta','Kullanıcı Mail': 'eposta',
                    'E-posta': 'eposta', 'Email': 'eposta', 'Çalıştığı Kurum-Birim': 'birim', 'Çalıştığı Birim': 'birim', 'Birim': 'birim',
                    'Departman': 'birim', 'NES Bitim Tarihi': 'nesbitimtarihi','Sertifika Bitiş Tarihi': 'nesbitimtarihi', 'Nes Bitim Tarihi': 'nesbitimtarihi', 'NES Bitiş Tarihi': 'nesbitimtarihi'
                }

                df = df.rename(columns=lambda x: sutun_eslesmeleri.get(x, x))

                

                # Zorunlu sütunlar kontrolü
                zorunlu_sutunlar = ['tc', 'ad', 'soyad']
                eksik_zorunlular = [sutun for sutun in zorunlu_sutunlar if sutun not in df.columns]
                if eksik_zorunlular:
                    raise ValueError(f"Zorunlu sütun(lar) eksik: {eksik_zorunlular}")

                # Opsiyonel sütunlar için varsayılan değerler
                opsiyonel_sutunlar = {
                    'dogumtarihi': '01.01.1900', 'eposta': 'None', 'birim': 'Belirtilmemiş', 'nesbitimtarihi': '01.01.1900'
                }

                for sutun, varsayilan in opsiyonel_sutunlar.items():
                    if sutun not in df.columns:
                        df[sutun] = varsayilan
                        print(f"Uyarı: {sutun} sütunu eksik, varsayılan değer atandı")


                gerekli_sutunlar = ['tc', 'ad', 'soyad', 'dogumtarihi', 'eposta', 'birim', 'nesbitimtarihi']
                for sutun in gerekli_sutunlar:
                    if sutun not in df.columns:
                        df[sutun] = opsiyonel_sutunlar.get(sutun, '')  # varsa varsayılanı, yoksa boş

                df = df[gerekli_sutunlar]  # Fazla sütunlar filtreleniyor

                # Veriyi temizleme ve formatlama
                df['tc'] = df['tc'].astype(str).str.strip()
                df['ad'] = df['ad'].astype(str).str.strip().str.title()
                df['soyad'] = df['soyad'].astype(str).str.strip().str.title()

                # Tarih dönüşümü
                for tarih_sutunu in ['dogumtarihi', 'nesbitimtarihi']:
                    try:
                        # Veriler dd.MM.yyyy şeklinde geldiği için dayfirst=True kullanıyoruz
                        df[tarih_sutunu] = pd.to_datetime(df[tarih_sutunu], dayfirst=True, errors='coerce')
                    except Exception as e:
                        print(f"{tarih_sutunu} dönüşüm hatası:", e)
                        df[tarih_sutunu] = opsiyonel_sutunlar[tarih_sutunu]  # Varsayılan tarih

                # Veritabanına kayıt
                basarili_kayitlar = 0
                for index, row in df.iterrows():
                    try:
                        tc_no = str(row['tc'])

                        # TC zaten varsa, bu satırı atla
                        if vt.kayitVarMi(tc_no):
                            print(f"Zaten kayıtlı: {tc_no}")
                            continue

                        # NES bitim tarihi boşsa varsayılan kullan, değilse dönüştür
                        nesbitimtarihi_raw = row['nesbitimtarihi']
                        if pd.isna(nesbitimtarihi_raw) or str(nesbitimtarihi_raw).strip() == "":
                            nesbitimtarihi = "1900-01-01"  # YYYY-MM-DD
                        else:
                            # dd.MM.yyyy → datetime objesi → yyyy-MM-dd
                            nesbitimtarihi = pd.to_datetime(nesbitimtarihi_raw, dayfirst=True).strftime('%Y-%m-%d')

                        dogumtarihi = pd.to_datetime(row['dogumtarihi'], dayfirst=True).strftime('%Y-%m-%d')

                        birim_degeri = str(row['birim']).strip()
                        if not birim_degeri.startswith("BAİBÜ-"):
                            birim = f"BAİBÜ-{birim_degeri}"
                        else:
                            birim = birim_degeri


                        vt.kayitEkle(
                            tc=tc_no,
                            ad=str(row['ad']).upper(),
                            soyad=str(row['soyad']).upper(),
                            dogumtarihi=dogumtarihi,
                            eposta=str(row['eposta']),
                            birim=birim,
                            nesbitimtarihi=nesbitimtarihi
                        )

                        basarili_kayitlar += 1
                    except Exception as e:
                        print(f"Kayıt ekleme hatası (Satır {index+2}):", e)






                self.messageBoxBasari(
                    "Kayıt Tamamlandı", 
                    f"Toplam {len(df)} kayıttan {basarili_kayitlar} tanesi başarıyla kaydedildi."
                )

            except Exception as e:
                self.messageBoxHata()
                print("Detaylı hata:", e)

    def messageBoxHata(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("⚠ Hata Oluştu")
        msgBox.setText("Hata oluştu!")
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setStyleSheet("""QMessageBox { background-color: black; font-family: 'Segoe UI'; font-size: 14px; }
        QLabel { color: white; padding: 10px; }
        QPushButton { background-color: #e74c3c; color: white; border: none; padding: 6px 14px; border-radius: 8px; font-weight: bold; font-size: 13px; min-width: 80px; }
        QPushButton:hover { background-color: #c0392b; }""")
        msgBox.exec_()

    def messageBoxBasari(self, title, text):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(f"✔ {title}")
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setStyleSheet("""QMessageBox { background-color: black; font-family: 'Segoe UI'; font-size: 14px; }
        QLabel { color: white; padding: 10px; }
        QPushButton { background-color: #4caf50; color: white; border: none; padding: 6px 14px; border-radius: 8px; font-weight: bold; font-size: 13px; min-width: 80px; }
        QPushButton:hover { background-color: #45a049; }""")
        msgBox.exec_()
