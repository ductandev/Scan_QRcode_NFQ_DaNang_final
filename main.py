import time
import csv
import cv2
import pyzbar.pyzbar as pyzbar
import requests
from bs4 import BeautifulSoup

# get the webcam:
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
with open('qrcode.csv') as file_read:                   #tao 1 list chua nhung nguoi da checkin
    csv_reader = csv.reader(file_read, delimiter=',')
    qr_code = [row[0] for row in csv_reader]
file_read.close()


def save(codes):
    with open('qrcode.csv', mode="w", newline='') as file_save:     # newline : bo cach dong
        csv_write = csv.writer(file_save, delimiter=',')
        for code in codes:
            csv_write.writerow([code])
    file_save.close()


def get_data(response):
    page = BeautifulSoup(response.content, "html.parser")
    elem = page.find_all("p")
    results = BeautifulSoup(str(elem), features="html.parser").get_text()
    results = results.replace("[", "")
    results = results.replace("]", "")
    results = results.split(".")
    return results


def get_QR(code, state=0):
    URL_checkin = "https://qrcode.danang.gov.vn/kbyt/site/checkin.php"
    URL_checkout = "https://qrcode.danang.gov.vn/kbyt/site/checkout.php"

    data = {
        "pl_name": "abc",
        "pl_address": "123 tesy",
        "pl_id": "6184856078973f00401268ff",
        "pl_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
                    ".eyJ1aWQiOiI2MTg0ODU0ODBlNDgzODAwMmEwOWY2YjAiLCJyb2xlIjoib3duZXItcGxhY2UiLCJpYXQiOjE2MzYwNzU1ODAsImV4cCI6MTYzNjA3NTU4MH0.yWqJw9d90t5Ppx9jOdUeqOSVZkOxWctmOuai2076-CU",
        "ID": "{}".format(code)
    }
    if state == 0:
        response = requests.post(URL_checkin, data)
        results = get_data(response)
    else:
        response = requests.post(URL_checkout, data)
        results = get_data(response)
    return results


def decode(im):
    decoded_Objects = pyzbar.decode(im)
    return decoded_Objects


sleep_time = 0
check = True
while cap.isOpened():
    ret, frame = cap.read()
    im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # thời gian giữa mỗi lần check, với fps = 30, 450 tương ứng với 15s
    if sleep_time % 450 == 0:
        check = True                #check: Dieu kien de chay QR code
    if check:
        decodedObjects = decode(im)
        for decodedObject in decodedObjects:
            code = decodedObject.data.decode("ascii")
            print("decodedObject = ",decodedObject)
            print("code =",code)
            if code in qr_code:         # qr_code : file csv line 14
                # thông tin check out
                print(get_QR(decodedObject, state=1))
                # xóa khỏi list danh sách đã check in
                qr_code.remove(code)    # xoa QR code trong list
            else:
                # thông tin check in
                print(get_QR(decodedObject))
                # thêm vào danh sách đã check in
                qr_code.append(code)
            check = False
        save(qr_code)
    sleep_time += 1
    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
