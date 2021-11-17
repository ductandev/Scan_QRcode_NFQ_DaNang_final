
from datetime import datetime, date, timedelta
import pickle
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import os
import csv

from tensorflow.python.ops.gen_linalg_ops import qr

from gtts import gTTS
from time import sleep
import threading
from serial import Serial
import tensorflow
import detect_face
from pyzbar import pyzbar
from json import dumps, load, loads

from GUIVIDEO import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication,QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import  QThread,  pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

import requests
from bs4 import BeautifulSoup



os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# ----tensorflow version check
if tensorflow.__version__.startswith('1.'):
    import tensorflow as tf
else:
    import tensorflow.compat.v1 as tf
    tf.disable_v2_behavior()
print("Tensorflow version: ",tf.__version__)



f = open('hrdata/sample.json')                                     # đọc file json
data_web = load(f)


font_cv = cv2.FONT_HERSHEY_SIMPLEX
unknownTemperature = []
unknownTime = []
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG'} 
                                     

with open('hrdata/data/qrcode.csv') as file_read:                   # Tạo 1 list đã chứa những người đã checkin trong file csv
    csv_reader = csv.reader(file_read, delimiter=',')
    qr_code = [row[0] for row in csv_reader]
file_read.close()



class Thread(QThread):
    changePixmap = pyqtSignal(QImage, name='video')
    changeTime = pyqtSignal(str, name='time')
    changePhoto = pyqtSignal(QImage, name='avatar')
    changeTemperature = pyqtSignal(str, name='temperature')
    changeResultQRcode = pyqtSignal(str, name='result')


    def write_read(self, x):
        self.arduino.write(bytes(x, 'utf-8'))
        sleep(0.05)
        data = self.arduino.readline()
        return data

    def soud(self, staffName):
        os.system("mpg123 amthanh/warning2.mp3")

    def soud2(self, staffName):
        os.system("mpg123 amthanh/wash_hand_scan_qrcode.mp3")

    def soud3(self, names):
        os.system("mpg123 amthanh/succss.mp3")





    def blur_camera(self):                      # hàm xử lý cho camera và quét QRcode
        self.cap.set(28, 0)                     # lệnh cho camera trở lại bình thường
        self.cho_phep_scan_qrcode = 0           # cho dừng quét QRcode                      


    #----Lưu save người checkin/checkout QR code
    def save_status_id(self, codes):
        with open('hrdata/data/qrcode.csv', mode="w", newline='') as file_save:     # newline : bo cach dong
            csv_write = csv.writer(file_save, delimiter=',')
            for code in codes:
                csv_write.writerow([code])
        file_save.close()

    def delete_data_csv(self):                                          # xóa file csv khi qua ngày mới
        with open('hrdata/data/qrcode.csv', mode="w") as detele_file_csv:
            detele_file_csv.truncate()
        detele_file_csv.close()

    def save_csv_backup(self,codes_backup):
        with open('hrdata/data/qrcode_backup.csv', mode="+a", newline='') as file_save_backup:     # newline : bo cach dong
            csv_write_backup = csv.writer(file_save_backup, delimiter=',')
            csv_write_backup.writerow([codes_backup, str(datetime.now().strftime("%Y/%m/%d , %H:%M:%S")) ])
        file_save_backup.close()


    def destroy_groupbox(self):                 # hàm xử lý cho xóa groups_box
        ui.groupBox.close()
        ui.qr_khaibaoyte_danang.show()
        ui.no_internet.close()
        ui.icon_ok.close()
        ui.icon_not_ok.close()


    def get_data(self, response):
        page = BeautifulSoup(response.content, "html.parser")
        elem = page.find_all("p")
        icon = page.find_all("img", {"class": "icon_noti"})
        results = BeautifulSoup(str(elem), features="html.parser").get_text()
        results = results.replace("[", "")
        results = results.replace("]", "")
        results = results.split(".")
        if icon[0].get("src") == "/kbyt/img/ico_ok.png":
            results.append("OK")
        else:
            results.append("NOTOK")
        return results



    #----Post data QR code
    def get_QR(self, code, state=0):
        URL_checkin = "https://qrcode.danang.gov.vn/kbyt/site/checkin.php"
        URL_checkout = "https://qrcode.danang.gov.vn/kbyt/site/checkin.php"#checkout.php"

        data = {
            "pl_name": "{}".format(data_web['pl_name']),    # .format() có thể định dạng lại chữ sai định dạng bên file json
            "pl_address": data_web['pl_address'],
            "pl_id": data_web['pl_id'],
            "pl_token": data_web['pl_token'],
            "ID": "{}".format(code)
        }

        try:
            ui.no_internet.close()
            if state == 0:
                response = requests.post(URL_checkin, data)
                results = self.get_data(response)
            else:
                response = requests.post(URL_checkout, data)
                results = self.get_data(response)
            return results

        except:
            results = ""                    #"NO INTERNET CONNECTION"
            print("NO INTERNET CONETION")
            ui.no_internet.show()
            return results






    def run(self):

        try:
            self.arduino =  Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
        except Exception as e:
            print(e)

        global qr_code
        self.temperature = 17
        self.threshold = 70
        self.color = (0,255,0)
        self.minsize = 550  # minimum size of face
        self.threshold = [0.6, 0.7, 0.7]  # three steps's threshold
        self.factor = 0.709  # scale factor
        with tf.Graph().as_default():
            config = tf.ConfigProto(log_device_placement=False,
                                    allow_soft_placement=False
                                    )
            config.gpu_options.per_process_gpu_memory_fraction = 0
            sess = tf.Session(config=config)
            with sess.as_default():
                self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(sess, None)
        self.cap = cv2.VideoCapture(0)
        # self.cap = cv2.VideoCapture("./test.mp4") 
        
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.cap.set(28, 0)
        self.cap.set(3, 1280) 
        self.cap.set(4, 720)

        self.start_time_temp = time.time()
        self.interrup_time = time.time() - 16  # trừ thời gian trước để có thể bắt đầu chạy vòng lặp 
        self.demwaring = 0
        self.cho_phep_scan_qrcode = 0
        self.today = date.today()  #- timedelta(days=1)  # NGÀY THÁNG NĂM HÔM NAY
        self.barcodeData = None
        self.timer_destroy_groupbox = threading.Timer(5.0, self.destroy_groupbox)    # khai báo biến timer_destroy_groupbox để có thể xử dụng cancel tránh lặp


        while (self.cap.isOpened()):     
            self.ret, self.frame = self.cap.read()
            if self.ret:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                try:
                    self.bounding_boxes, self.points = detect_face.detect_face(self.frame, self.minsize, self.pnet, self.rnet, self.onet, self.threshold, self.factor)
                    self.nrof_faces = self.bounding_boxes.shape[0]
                    # cv2.rectangle(self.frame, (320,180), (960,540), self.color, 2)
                    self.timeDetect = datetime.now().strftime("%H:%M:%S")
                


                    if self.nrof_faces > 0:
                        if  ((time.time() - self.interrup_time ) > 12):         # mỗi 1 lượt quét QR sẽ diễn ra trong vòng 13 giây
                            self.interrup_time = time.time()                    # thời gian ngắt 13 giây
   
                            while True:
                                try:
                                    num = '?'
                                    value = self.write_read(num).decode("utf8","ignore")
                                    x_max = float(value)
                                    self.temperature =  round(0.1455*x_max + 32.108,2)  

                                    if (self.temperature > 37.5):
                                        if (self.temperature > 38.5):
                                            self.temperature= 38.5 

                                        t1_s = threading.Thread(target=self.soud, args=( time.time(), ))
                                        t1_s.start()
                                    if (self.temperature < 35.5):
                                        self.temperature= 35.5              
                                    break
                                except Exception as es:
                                    print("es---------------------------------------    {}".format(es))
                                    self.temperature = "None"
                                    try:
                                        self.arduino =  Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
                                    except Exception as e:
                                        print(e)
                                    break



                            t2_s = threading.Thread(target=self.soud2, args=( time.time(), )) # phát loa yêu cầu rửa tay
                            t2_s.start()

                            img_save_1 = Image.open("recogniteImage/people_recognite_1.png")  # image extension *.png,*.jpg
                            img_save_1.save("recogniteImage/people_recognite_3.png")

                            cv2.imwrite('img.png', cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
                            self.changeTemperature.emit(str(self.temperature))
                            self.changeTime.emit(str(self.timeDetect))
                            img_save_4 = Image.open("img.png")
                            width, height = img_save_4.size
                            x = (width - height) // 2
                            img_cropped = img_save_4.crop((x, 0, x + height, height))
                            mask = Image.new('L', img_cropped.size)
                            mask_draw = ImageDraw.Draw(mask)
                            width, height = img_cropped.size
                            mask_draw.ellipse((10, 10, width-10, height-10), fill=255)
                            img_cropped.putalpha(mask)
                            img_save_4 = img_cropped.resize((128, 128), Image.ANTIALIAS)
                            img_save_4.save("recogniteImage/people_recognite_1.png")
                            photo = QImage('recogniteImage/people_recognite_1.png')
                            self.changePhoto.emit(photo)

                            self.cap.set(28, 100)                   # Bắt đầu cho mờ camera 
                            self.timer_blur_camera = threading.Timer(11.0, self.blur_camera)     # 9 giây sau tự động camera trở về trạng thái bình thường, và ko cho quét QRcode nữa
                            self.timer_blur_camera.start()          # Bắt đầu 9 giây sau tự động camera trở về trạng thái bình thường, và ko cho quét QRcode nữa
                            self.cho_phep_scan_qrcode = 1           # Bằng 1 : cho phép bắt đầu scan QRcode

                    elif self.cho_phep_scan_qrcode == 1:            # Bằng 1 : cho phép bắt đầu scan QRcode
                        # ''' Code xử lý cho phần quét QR code ở đây'''
                        #==============================================
                        barcodes = pyzbar.decode(self.frame)
                        for barcode in barcodes:
                            (x, y, w, h) = barcode.rect
                            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            self.barcodeData = barcode.data.decode("utf-8")
                            barcodeType = barcode.type
                            text = "{} ({})".format(self.barcodeData, barcodeType)

                            self.time_scan_qrcode = time.time()
                            self.save_csv_backup_file = threading.Timer(0.0, self.save_csv_backup(self.barcodeData))  # lưu QR code vào file csv backup ( kể cả mất mạng hay có mạng đều lưu)
                            self.save_csv_backup_file.start()
                            
                            if self.barcodeData in qr_code:         # nếu QRcode đã tồn tại trong list file cvs trước đó thì xóa trong list và cho check out || qr_code : file csv line 50
                                #----thông tin check out
                                # print(self.get_QR(barcode, state=1))
                                self.result = self.get_QR(barcode, state=1) 
                                print(self.result)
                                #---- Xử lý cho hiện "icon ok" và "not OK"
                                try:
                                    self.icon = self.result[-1]
                                    self.result.pop()               # xóa phần tử sau cùng của mảng
                                except:
                                    pass
                                #----Xử lý ghép chuỗi bỏ list đi
                                self.ghep_chuoi_qr = ''.join(self.result) # xử lý chuỗi sử dụng hàm ghép chuỗi join và ghép lại với nhau bằng '' 
                                # for chuoi_kq_qr in self.result:   # bỏ list chuỗi đi và ghép chuỗi kết quả quét QR lại với nhau thành 1 dòng
                                #     self.ghep_chuoi_qr +=chuoi_kq_qr
                                self.changeResultQRcode.emit(str(self.ghep_chuoi_qr))   # cho phép hiển thị lên UI
                                #----xóa khỏi list danh sách đã check in
                                if self.result != "":               # nếu reslut khác "" có nghĩ là có mạng, vì ko có mạng result trả về ""
                                    qr_code.remove(self.barcodeData)# xóa QR code trong list
                            else:                                   # nếu QRcode không có trong file cvs thì cho check in
                                #----thông tin check in
                                # print(self.get_QR(barcode))
                                self.result = self.get_QR(barcode)
                                print(self.result)
                                #----Xử lý cho hiện "icon ok" và "not OK"
                                try:
                                    self.icon = self.result[-1]
                                    self.result.pop()               # xóa phần tử sau cùng của mảng
                                except:
                                    pass
                                #----Xử lý ghép chuỗi bỏ list đi
                                self.ghep_chuoi_qr = ''.join(self.result) # xử lý chuỗi sử dụng hàm ghép chuỗi join và ghép lại với nhau bằng '' 
                                # for chuoi_kq_qr in self.result:   # bỏ list chuỗi đi và ghép chuỗi kết quả quét QR lại với nhau thành 1 dòng
                                #     self.ghep_chuoi_qr +=chuoi_kq_qr                               
                                self.changeResultQRcode.emit(str(self.ghep_chuoi_qr))        # cho phép hiển thị lên UI
                                #----thêm vào danh sách đã check in
                                if self.result != "":               # nếu reslut khác "" có nghĩ là có mạng, vì ko có mạng result trả về "", tránh trường hợp xóa mất data 
                                    qr_code.append(self.barcodeData)


                        if self.barcodeData is not None:            # Nếu phát hiện có barcodeData tồn tại || not None: có tồn tại
                            t3_s = threading.Thread(target=self.soud3, args=( time.time(), )) # phát loa yêu cầu rửa tay
                            t3_s.start()
                            self.cho_phep_scan_qrcode = 0
                            self.barcodeData = None                 # đưa về trạng trái không tồn tại để không bị lưu lại cho vòng if lần sau 
                            self.save_status_id(qr_code)            # lưu QR code vào file csv mới

                            ui.groupBox.show()                      # Cho hiển thị group box
                            ui.qr_khaibaoyte_danang.close()         # tắt QR code khai báo y tế đà nẵng

                            ui.icon_ok.close()
                            ui.icon_not_ok.close()
                            if self.icon == "OK":
                                ui.icon_ok.show()
                                self.icon = None
                            if self.icon == "NOTOK":
                                ui.icon_not_ok.show()
                                self.icon = None


                            self.timer_destroy_groupbox.cancel()    # tắt trạng thái trước nếu người sau quét tiếp
                            self.timer_destroy_groupbox = threading.Timer(12.0, self.destroy_groupbox)    # cho hiện group box 12 giây sau đó xóa đi
                            self.timer_destroy_groupbox.start()
                        #============================================



                    else:
                        if self.today < date.today():               # xóa file cvs khi qua ngày mới
                            self.delete_data_csv()
                            self.today = date.today()
                            qr_code=[]

                        cv2.putText(self.frame, "No face", (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 5)




                except Exception as e:
                    print(e)
  

                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR) 
                cv2.putText(self.frame, str(datetime.now().strftime("%Y/%m/%d , %H:%M:%S")), (80,60), font_cv, 1, (0, 0, 255), 2, cv2.LINE_AA)
                rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
                if cv2.waitKey(1) & 0xFF == ord("q"): 
                    self.cap.release()
                    cv2.destroyAllWindows()
                    exit(0)


class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.temp = QtWidgets.QLabel(self.centralwidget)
        self.time_log = QtWidgets.QLabel(self.centralwidget)
        self.photo = QtWidgets.QLabel(self.centralwidget)
        self.photo_title = QtWidgets.QLabel(self.centralwidget)
        self.titkul_hotline = QtWidgets.QLabel(self.centralwidget)
        self.qr_khaibaoyte_danang = QtWidgets.QLabel(self.centralwidget)
        self.video = QtWidgets.QLabel(self.centralwidget)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layout1 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.label_ketqua = QtWidgets.QLabel(self.groupBox)
        self.result_qrcode = QtWidgets.QLabel(self.groupBox)
        self.no_internet = QtWidgets.QLabel(self.groupBox)
        self.icon_ok = QtWidgets.QLabel(self.groupBox)
        self.icon_not_ok = QtWidgets.QLabel(self.groupBox)



        try:
            self.arduino =  Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
        except Exception as e:
            print(e)

        th = Thread(self.centralwidget)
        th.changePixmap.connect(lambda image: self.setImage(image))
        th.changeTime.connect(lambda time: self.setTime(time))
        th.changePhoto.connect(lambda photo: self.setPhoto(photo))
        th.changeTemperature.connect(lambda temp: self.setTemperature(temp))
        th.changeResultQRcode.connect(lambda result_qrcode: self.setResult_qrcode(result_qrcode))
        th.start()

    @pyqtSlot(QImage, name='video')
    def setImage(self, image):
        image = QPixmap.fromImage(image)
        image = image.scaled(640, 480, Qt.KeepAspectRatio)
        self.video.setPixmap(image)

    @pyqtSlot(QImage, name='avatar')
    def setPhoto(self, photo):
        photo = QPixmap.fromImage(photo)
        self.photo.setStyleSheet(" border: 6px solid #ff6b00; border-radius: 138px; ")     
        self.photo.setPixmap(photo)


    @pyqtSlot(str, name='time')
    def setTime(self, time):
        self.time_log.setStyleSheet("background-color: none;  border: 1px solid none;")
        self.time_log.setText('Time: ' + time)


    @pyqtSlot(str, name='temperature')
    def setTemperature(self, temperature):
        if temperature != "None":
            if (float(temperature) >= 37.5):
                self.temp.setStyleSheet("background-color: red;  border: 1px solid black;") 
                self.temp.setText('Temperature: > ' + temperature + ' °C')
            else:
                self.temp.setStyleSheet("background-color: none;  border: 1px solid none;")
                self.temp.setText('Temperature: ' + temperature + ' °C')
        else:
            self.temp.setStyleSheet("background-color: red;  border: 1px solid black;") 
            self.temp.setText('Temperature: ' + temperature)


    @pyqtSlot(str, name='result')
    def setResult_qrcode(self, result):
        # self.result_qrcode.setStyleSheet("background-color: none;  border: none;")
        self.result_qrcode.setText(result)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setStyleSheet("background-color: white")
        MainWindow.resize(1080, 1920)
        MainWindow.setMinimumSize(QtCore.QSize(1080, 1920))
        MainWindow.setMaximumSize(QtCore.QSize(1080, 1920))
        MainWindow.setSizeIncrement(QtCore.QSize(1080, 1920))
        MainWindow.setBaseSize(QtCore.QSize(1080, 1920))
        font = QtGui.QFont('Arial', 10)
        self.browser = window1()
        font.setPointSize(8)
        MainWindow.setFont(font)
        self.centralwidget.setObjectName("centralwidget")
        self.video.setGeometry(QtCore.QRect(485, 272, 488, 464))
        self.video.setMinimumSize(QtCore.QSize(488, 464))
        self.video.setText("")
        self.video.setStyleSheet(" border: 10px solid #ff6b00; ")
        self.video.setScaledContents(True)

        self.photo_title.setGeometry(QtCore.QRect(180, 105, 720, 80))
        self.photo_title.setText("")
        self.photo_title.setPixmap(QtGui.QPixmap("Image/1.png"))
        self.photo_title.setScaledContents(True)


        self.photo.setGeometry(QtCore.QRect(108, 275, 276, 276))
        self.photo.setText("")
        self.photo.setPixmap(QtGui.QPixmap("Image/circled_user_male_480px_new.png"))
        self.photo.setStyleSheet(" border: 6px solid #ff6b00; border-radius: 138px; ")
        self.photo.setScaledContents(True)


        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 1080, 1040, 700))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.web = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.web.setObjectName("web")

        
        self.layout1.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.layout1.setContentsMargins(0, 0, 0, 0)
        self.layout1.setObjectName("layout1")
        self.layout1.addWidget(self.browser)


        self.titkul_hotline.setGeometry(QtCore.QRect(0, 1785, 1080, 100))
        self.titkul_hotline.setText("")
        self.titkul_hotline.setPixmap(QtGui.QPixmap("Image/titkul_hotline3.png"))
        self.titkul_hotline.setScaledContents(True)
        self.titkul_hotline.setObjectName("titkul_hotline")


        self.qr_khaibaoyte_danang.setGeometry(QtCore.QRect(95, 820, 890, 250))
        self.qr_khaibaoyte_danang.setText("")
        self.qr_khaibaoyte_danang.setPixmap(QtGui.QPixmap("Image/qr_khaibaoyte_danang.png"))
        self.qr_khaibaoyte_danang.setScaledContents(True)
        self.qr_khaibaoyte_danang.setObjectName("qr_khaibaoyte_danang")       


        self.time_log.setGeometry(QtCore.QRect(100, 625, 260, 30))
        font = QtGui.QFont('Lato', 20)
        self.time_log.setFont(font)
        self.time_log.setStyleSheet("background-color: none;  border: 1px solid none;")

        self.temp.setGeometry(QtCore.QRect(100, 665, 350, 30))
        font = QtGui.QFont('Lato', 20)
        self.temp.setFont(font)
        self.temp.setStyleSheet("background-color: none;  border: 1px solid none;")


        self.groupBox.setGeometry(QtCore.QRect(50, 820, 980, 250))
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setStyleSheet("background-color: none; border: 6px solid #ff6b00; border-radius: 80px; ")
        # self.groupBox.stackUnder(self.label_ketqua)    # cho hiển thị bên dưới
        ui.groupBox.close()                              # tắt group_box, chưa cho hiển thị


        self.label_ketqua.setGeometry(QtCore.QRect(315, 5, 350, 40))
        font = QtGui.QFont('Lato', 20)
        font.setBold(True)
        self.label_ketqua.setFont(font)
        self.label_ketqua.setStyleSheet("background-color: none; color: #007afc;  border: none")

        self.result_qrcode.setGeometry(QtCore.QRect(10, 25, 960, 270))
        font = QtGui.QFont('Lato', 12)
        self.result_qrcode.setFont(font)
        self.result_qrcode.setWordWrap(True)                # cho kết quả xuống hàng chữ
        self.result_qrcode.setAlignment(Qt.AlignCenter)     # hàm căn giữa chữ
        self.result_qrcode.setStyleSheet("background-color: none;  border: none;")     


        self.no_internet.setGeometry(QtCore.QRect(353, 40, 274, 205))
        self.no_internet.setText("")
        self.no_internet.setPixmap(QtGui.QPixmap("Image/no_internet.jpg"))
        self.no_internet.setScaledContents(True)
        self.no_internet.setObjectName("no_internet")
        self.no_internet.setStyleSheet("background-color: none;  border: none;") 
        ui.no_internet.close()                              # tắt hình no_internet, chưa cho hiển thị

        self.icon_ok.setGeometry(QtCore.QRect(458, 40, 64, 64))
        self.icon_ok.setText("")
        self.icon_ok.setPixmap(QtGui.QPixmap("Image/icon_ok.png"))
        self.icon_ok.setScaledContents(True)
        self.icon_ok.setObjectName("icon_ok")
        self.icon_ok.setStyleSheet("background-color: none;  border: none;") 
        ui.icon_ok.close()                              # tắt hình icon_ok, chưa cho hiển thị

        self.icon_not_ok.setGeometry(QtCore.QRect(458, 50, 64, 64))
        self.icon_not_ok.setText("")
        self.icon_not_ok.setPixmap(QtGui.QPixmap("Image/icon_not_ok.ico"))
        self.icon_not_ok.setScaledContents(True)
        self.icon_not_ok.setObjectName("icon_not_ok")
        self.icon_not_ok.setStyleSheet("background-color: none;  border: none;") 
        ui.icon_not_ok.close()                              # tắt hình icon_not_ok, chưa cho hiển thị


        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 19))

        MainWindow.setMenuBar(self.menubar)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def video_run(self):
        pass

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "NFQ_DA_Nang_001"))
        self.time_log.setText(_translate("MainWindow", "Time:"))
        self.temp.setText(_translate("MainWindow", "Temperature:"))
        self.groupBox.setTitle(_translate("MainWindow", ""))
        self.label_ketqua.setText(_translate("MainWindow", "KẾT QUẢ QUÉT MÃ QR"))
        self.result_qrcode.setText(_translate("MainWindow", ""))
        self.web.setText(_translate("MainWindow", ""))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.move(0,0)
    MainWindow.show()
    sys.exit(app.exec_())
