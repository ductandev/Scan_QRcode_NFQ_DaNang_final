import csv 

with open('qrcode.csv') as file_read:
    csv_reader = csv.reader(file_read, delimiter=',')
    # qr_code = [row[0] for row in csv_reader]          # cach viet tat vong for ben duoi
    for row in csv_reader:
        print(row[0])
file_read.close()


a = [row for row in range(0,10)]                      #  tao ra 1 list tu 0 den 10
print(a)
