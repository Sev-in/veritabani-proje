from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate
from manuelKayitPython import Ui_Form_tekliKayit
from veritabani import Veritabani
from datetime import datetime 

vt = Veritabani()

class ManuelKayitPage(QWidget):
        def __init__(self,parent=None):
            super().__init__()
            self.manuelKayitForm=Ui_Form_tekliKayit()
            self.manuelKayitForm.setupUi(self)
            self.MainWindow = parent

            self.manuelKayitForm.pushButton_geri.clicked.connect(self.geriDon)
            self.manuelKayitForm.pushButton_kaydet.clicked.connect(self.veriKaydet)


        def geriDon(self):
            self.hide()
            if self.MainWindow:
                self.MainWindow.show()


        def veriKaydet(self):
            tc = self.manuelKayitForm.lineEdit_tc.text()
            ad = self.manuelKayitForm.lineEdit_ad.text().upper()
            soyad = self.manuelKayitForm.lineEdit_soyad.text().upper()

            # Tarihleri veritabanı formatına (yyyy-MM-dd) dönüştürüyoruz
            dogumtarihi_raw = self.manuelKayitForm.dateEdit_dogumTarihi.date().toString("dd-MM-yyyy")
            dogumtarihi = datetime.strptime(dogumtarihi_raw, "%d-%m-%Y").strftime("%Y-%m-%d")

            eposta = self.manuelKayitForm.lineEdit_eposta.text()
            birim_input = self.manuelKayitForm.lineEdit_birim.text().strip()
            birim = f"BAİBÜ-{birim_input}" if not birim_input.startswith("BAİBÜ-") else birim_input


            nesbitimtarihi_raw = self.manuelKayitForm.dateEdit_nesBitimTarihi.date().toString("dd-MM-yyyy")
            nesbitimtarihi = datetime.strptime(nesbitimtarihi_raw, "%d-%m-%Y").strftime("%Y-%m-%d")

            if vt.kayitEkle(tc, ad, soyad, dogumtarihi, eposta, birim, nesbitimtarihi):
                self.messageBoxBasari(title="Kayıt Başarılı!", text="Kayıt Başarıyla Gerçekleşti!")
                # Alanları temizle
                self.manuelKayitForm.lineEdit_ad.clear()
                self.manuelKayitForm.lineEdit_soyad.clear()
                self.manuelKayitForm.lineEdit_tc.clear()
                self.manuelKayitForm.lineEdit_eposta.clear()
                self.manuelKayitForm.dateEdit_dogumTarihi.setDate(QDate.currentDate())
                self.manuelKayitForm.lineEdit_birim.clear()
                self.manuelKayitForm.dateEdit_nesBitimTarihi.setDate(QDate.currentDate())
            else:
                self.messageBoxHata()


        def messageBoxHata(self):
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("⚠ Hata Oluştu")
            msgBox.setText(f"Hata!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStyleSheet("""
                QMessageBox {
                    background-color: black;  /* Siyah arka plan */
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QLabel {
                    color: white;  /* Beyaz yazı rengi */
                    padding: 10px;
                }
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 6px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 80px;
                    }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            msgBox.exec_()

        def messageBoxBasari(self,title,text):
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("✔ "+title)
            msgBox.setText(text)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setStyleSheet("""
                QMessageBox {
                    background-color: black;  /* Siyah arka plan */
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QLabel {
                    color: white;  /* Beyaz yazı rengi */
                    padding: 10px;
                }
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    padding: 6px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            msgBox.exec_()  