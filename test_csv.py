import csv

uuid = ['079098013***|NGUYEN DUC TAN|1998-11-16|0|163604196810496278|<1<00<<0908246***']
uuid1= ['184394***|TRAN TUAN THANH|2000-03-09|0|163607540910761528|<1<00<<0971850***']

#----ghi vao file csv
# with open('uuid.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(uuid)
#     writer.writerow(uuid1)

#----doc file csv
with open('uuid.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row[0])