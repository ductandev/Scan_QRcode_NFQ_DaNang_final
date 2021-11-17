from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
import sys
from json import dumps, load, loads
import os

f = open('hrdata/loggin.json')              # đọc file json
data_user_name = load(f)


url = 'https://qrcode.danang.gov.vn/kbyt/'
driver = webdriver.Firefox(executable_path='geckodriver/geckodriver')

try:
    driver.get(url)
    results = driver.find_elements_by_class_name('frm_title')
    value_ketqua = results[2].text.split(" ")
    if value_ketqua[1] == "+":
        x_value_ketqua = int(value_ketqua[0]) + int(value_ketqua[2])
    elif value_ketqua[1] == "-":
        x_value_ketqua = int(value_ketqua[0]) - int(value_ketqua[2])
    elif value_ketqua[1] == "*":
        x_value_ketqua = int(value_ketqua[0]) * int(value_ketqua[2])
    print(x_value_ketqua)
    # driver.find_element_by_name("email").send_keys("abcdxyz@gmail.com")
    # driver.find_element_by_name("password").send_keys("abcd123456789")
    driver.find_element_by_name("email").send_keys(data_user_name["email"])
    driver.find_element_by_name("password").send_keys(data_user_name["password"])
    driver.find_element_by_name("ketqua").send_keys(str(x_value_ketqua))
    driver.find_element_by_class_name("input_btn").click()
    # driver.find_element_by_class_name("places_btn").click()
    vlaue_tolen = driver.find_element_by_name("pl_token").get_attribute('value')
    vlaue_name = driver.find_element_by_name("pl_name").get_attribute('value')
    vlaue_address = driver.find_element_by_name("pl_address").get_attribute('value')
    vlaue_id = driver.find_element_by_name("pl_id").get_attribute('value')
    distionary = {
        "pl_name" : vlaue_name,
        "pl_address": vlaue_address,
        "pl_id" : vlaue_id,
        "pl_token" : vlaue_tolen
    }
    # Serializing json 
    json_object = json.dumps(distionary, indent = len(distionary))

    # Writing to sample.json
    with open("hrdata/sample.json", "w") as outfile:
        outfile.write(json_object)
        print("DONE-----GETTOKEN SUCCESSED-----------------")
    driver.close()

except:                                      # Mat ket noi mang thi out chuong trinh
    driver.close()
    os.system('notify-send -t 1000000 "Error" "Loggin fail -- please try loggin again"')
    sys.exit("|| WRONG PASSWORD || OR || NO INTERNET CONNECTED ||")
    
