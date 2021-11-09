import requests

URL = "https://qrcode.danang.gov.vn/kbyt/site/checkin.php"

data = {
    "pl_name": "abc",
    "pl_address": "123 tesy",
    "pl_id": "6184856078973f00401268ff",
    "pl_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI2MTg0ODU0ODBlNDgzODAwMmEwOWY2YjAiLCJyb2xlIjoib3duZXItcGxhY2UiLCJpYXQiOjE2MzYwNzU1ODAsImV4cCI6MTYzNjA3NTU4MH0.yWqJw9d90t5Ppx9jOdUeqOSVZkOxWctmOuai2076-CU",
    "ID": "079098013***|NGUYEN DUC TAN|1998-11-16|0|163604196810496278|<1<00<<0908246***"
}
response = requests.post(URL,data)

print(response.text)
