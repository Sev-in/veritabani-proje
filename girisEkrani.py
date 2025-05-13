import sys
from PyQt5.QtWidgets import *
from girisEkraniPython import Ui_GirisEkrani  # Qt Designer ile oluşturduğunuz sınıf
from cokluKayit import CokluKayitPage
from manuelKayit import ManuelKayitPage
from kayitlar import KayitlarPage
from veritabani import Veritabani

vt=Veritabani()
class MainWindow(QMainWindow, Ui_GirisEkrani):
    def __init__(self,parent=None):
        super().__init__()
        self.onay=Ui_GirisEkrani()
        self.onay.setupUi(self)  # Arayüzü kur

        # Parent (self) gönderilerek oluşturuluyor
        # Bu sayfalara parent=self ile atanmış. Yani, bu sayfalara MainWindow'u "parent" olarak gösteriyoruz.
        self.cokluKayitPage = CokluKayitPage(parent=self)
        self.manuelKayitPage = ManuelKayitPage(parent=self)
        self.kayitlarPage = KayitlarPage(parent=self)

        # Buton tıklama işlemi
        self.onay.pushButton_cokluKayit.clicked.connect(self.CokluKayit)
        self.onay.pushButton_tekliKayit.clicked.connect(self.ManuelKayit)
        self.onay.pushButton_kayitlar.clicked.connect(self.Kayitlar)

        self.showMaximized() # ekranı büyütür.



    def CokluKayit(self):
        self.hide()
        self.cokluKayitPage.showMaximized()

    def ManuelKayit(self):
        self.hide()
        self.manuelKayitPage.showMaximized()

    def Kayitlar(self):
        self.hide()
        self.kayitlarPage.showMaximized()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())