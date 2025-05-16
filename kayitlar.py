from PyQt5.QtWidgets import *
from kayitlarPython import Ui_Form_kayitlar
from veritabani import Veritabani
from openpyxl import Workbook
from PyQt5.QtCore import QDate
from datetime import datetime


vt=Veritabani()
class KayitlarPage(QWidget):
        def __init__(self,parent=None):
            super().__init__()
            self.kayitlarForm=Ui_Form_kayitlar()
            self.kayitlarForm.setupUi(self)
            self.MainWindow = parent
            
            

            self.kayitlarForm.pushButton_geri.clicked.connect(self.geriDon)
            self.kayitlarForm.pushButton_yenile.clicked.connect(self.tabloyuDoldur)
            self.kayitlarForm.pushButton_silTc.clicked.connect(self.veriSilTc)
            self.kayitlarForm.pushButton_silSecerek.clicked.connect(self.secilenKaydiSil)
            self.kayitlarForm.pushButton_kaydet.clicked.connect(self.degisiklikleriKaydet)
            self.kayitlarForm.pushButton_ara.clicked.connect(self.aramaYap)
            self.kayitlarForm.pushButton_exceleDonustur.clicked.connect(self.excelAktar)

        

        def geriDon(self):
            self.hide()
            if self.MainWindow:
                self.MainWindow.show()





        def tabloyuDoldur(self):
            self.veriler = vt.verileriYukle()
            self.kayitlarForm.tableWidget_kayitlar.setRowCount(0)

            for row_number, row_data in enumerate(self.veriler):
                self.kayitlarForm.tableWidget_kayitlar.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    # Tarih kolonları: dogumtarihi (3. sütun), nesbitimtarihi (6. sütun)
                    if column_number in [3, 6]:
                        try:
                            # Tarihi önce yyyy-mm-dd ya da yyyy.mm.dd fark etmez, ikisini de destekle
                            if "." in data:
                                tarih_obj = datetime.strptime(data, "%Y.%m.%d")
                            elif "-" in data:
                                tarih_obj = datetime.strptime(data, "%Y-%m-%d")
                            else:
                                tarih_obj = datetime.strptime(data, "%Y%m%d")  # son çare
                            # Ekrana dd.mm.yyyy şeklinde göster
                            data = tarih_obj.strftime("%d.%m.%Y")
                        except Exception as e:
                            print(f"Tarih formatlama hatası: {e}")
                            pass
                    self.kayitlarForm.tableWidget_kayitlar.setItem(
                        row_number, column_number, QTableWidgetItem(str(data))
                    )

            self.kayitlarForm.tableWidget_kayitlar.setColumnCount(7)





        def veriSilTc(self):
            tc = self.kayitlarForm.lineEdit_tc.text()
            if vt.kayitSil(tc):
                self.messageBoxBasari(title="Silme Başarılı!",text="Seçilen kayıt başarıyla silindi.")
                self.kayitlarForm.lineEdit_tc.clear() # Alanları temizle

                row_count = self.kayitlarForm.tableWidget_kayitlar.rowCount() # Tablodaki satırı bul ve sil
                for row in range(row_count):
                    # TC numarasının 0. sütunda olduğunu varsayıyoruz
                    if self.kayitlarForm.tableWidget_kayitlar.item(row, 0).text() == tc:
                        self.kayitlarForm.tableWidget_kayitlar.removeRow(row)
                        break  # Silme işlemini yaptıktan sonra döngüyü sonlandır

            else:
                self.messageBoxHata()
                


        def secilenKaydiSil(self):
            # Seçilen satır indexlerini al
            selected_rows = set()
            for item in self.kayitlarForm.tableWidget_kayitlar.selectedItems():
                selected_rows.add(item.row())

            
                
            for row in sorted(selected_rows, reverse=True):  # Tabloda yukarıdan değil aşağıdan silmek önemli
                tc_no = self.kayitlarForm.tableWidget_kayitlar.item(row, 0).text()
                if vt.kayitSil(tc_no):  # Veritabanından sil
                    self.kayitlarForm.tableWidget_kayitlar.removeRow(row)  # Tablo arayüzünden de kaldır
            self.messageBoxBasari(title="Silme Başarılı!", text="Seçilen kayıtlar başarıyla silindi.")
            




        def degisiklikleriKaydet(self):
            row_count = self.kayitlarForm.tableWidget_kayitlar.rowCount()

            # Bağlantıyı bir defa açalım
            vt.baglantiAc()

            for row in range(row_count):
                tc = self.kayitlarForm.tableWidget_kayitlar.item(row, 0).text()
                ad = self.kayitlarForm.tableWidget_kayitlar.item(row, 1).text()
                soyad = self.kayitlarForm.tableWidget_kayitlar.item(row, 2).text()

                # Tarihleri önce dd.MM.yyyy olarak al, sonra yyyy-MM-dd formatına çevir
                try:
                    dogumtarihi_str = self.kayitlarForm.tableWidget_kayitlar.item(row, 3).text()
                    dogumtarihi = datetime.strptime(dogumtarihi_str, "%d.%m.%Y").strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Doğum tarihi formatlama hatası: {e}")
                    dogumtarihi = "1900-01-01"

                eposta = self.kayitlarForm.tableWidget_kayitlar.item(row, 4).text()
                birim = self.kayitlarForm.tableWidget_kayitlar.item(row, 5).text()

                try:
                    nesbitimtarihi_str = self.kayitlarForm.tableWidget_kayitlar.item(row, 6).text()
                    nesbitimtarihi = datetime.strptime(nesbitimtarihi_str, "%d.%m.%Y").strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"NES bitim tarihi formatlama hatası: {e}")
                    nesbitimtarihi = "1900-01-01"

                vt.kayitGuncelle(tc, ad, soyad, dogumtarihi, eposta, birim, nesbitimtarihi)

            self.messageBoxBasari(title="Güncelleme Başarılı!", text="Kayıt Başarıyla Güncellendi")

            # Tüm işlemler tamamlandıktan sonra bağlantıyı kapatalım
            vt.baglantiKapat()





        def aramaYap(self):
            tarih1 = self.kayitlarForm.dateEdit_baslangic.date().toString('yyyy-MM-dd')
            tarih2 = self.kayitlarForm.dateEdit_bitis.date().toString('yyyy-MM-dd')

            veriler = vt.nesKayitSorgula(tarih1, tarih2)
            
            self.kayitlarForm.tableWidget_kayitlar.setRowCount(0)

            for row_number, row_data in enumerate(veriler):
                self.kayitlarForm.tableWidget_kayitlar.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    # Eğer bu sütun dogumtarihi (3) ya da nesbitimtarihi (6) ise, formatla
                    if column_number in [3, 6]:
                        try:
                            if "." in data:
                                tarih_obj = datetime.strptime(data, "%Y.%m.%d")
                            elif "-" in data:
                                tarih_obj = datetime.strptime(data, "%Y-%m-%d")
                            else:
                                tarih_obj = datetime.strptime(data, "%Y%m%d")
                            data = tarih_obj.strftime("%d.%m.%Y")
                        except Exception as e:
                            print(f"Tarih formatlama hatası: {e}")
                            pass
                    self.kayitlarForm.tableWidget_kayitlar.setItem(
                        row_number, column_number, QTableWidgetItem(str(data))
                    )





        def excelAktar(self):
            try:
                # Excel dosyası oluştur
                workbook = Workbook()
                sheet = workbook.active
                sheet.title = "Kayıtlar"

                # TableWidget başlıklarını yaz
                column_count = self.kayitlarForm.tableWidget_kayitlar.columnCount()
                headers = []
                for col in range(column_count):
                    header = self.kayitlarForm.tableWidget_kayitlar.horizontalHeaderItem(col).text()
                    headers.append(header)

                # Boş sütun başlıkları ekle
                extra_columns = ["Başvuru Türü", "Açıklama", "Yedek","Akıllı Kart Okuyucu Türü","Açıklama","Yedek","VPN veya Logon","NES süresi","Ödeme Şekli","Not (Ek Bilgi)"]
                headers.extend(extra_columns)

                sheet.append(headers)

                # TableWidget verilerini yaz
                row_count = self.kayitlarForm.tableWidget_kayitlar.rowCount()
                for row in range(row_count):
                    row_data = []
                    for col in range(column_count):
                        item = self.kayitlarForm.tableWidget_kayitlar.item(row, col)
                        row_data.append(item.text() if item else "")
                    
                    # Boş sütunlar için veriler (örneğin boş string)
                    row_data.extend([""] * len(extra_columns))  # Her satır için 3 boş sütun ekleniyor
                    sheet.append(row_data)

                # Kaydetme penceresi
                dosya_yolu, _ = QFileDialog.getSaveFileName(self, "Excel Olarak Kaydet", "", "Excel Files (*.xlsx)")
                if dosya_yolu:
                    if not dosya_yolu.endswith(".xlsx"):
                        dosya_yolu += ".xlsx"
                    workbook.save(dosya_yolu)
                    self.messageBoxBasari(title="Aktarma Başarılı!", text="Aktarma Başarıyla Gerçekleşti!")
            except Exception as e:
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




                  
