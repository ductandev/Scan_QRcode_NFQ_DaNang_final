import pyautogui
import time

print(pyautogui.size())                    # lệnh hiển thị độ phân giải màn hình
print(pyautogui.position())                # lệnh hiển thị tọa độ chuột hiện tại         
# pyautogui.moveTo(100, 100, duration = 1) # lệnh di chuyển đến tọa độ x, y trong thời gian 1 gây
pyautogui.click(1000, 300)                 # lệnh click chuột trái
# pyautogui.click(1000, 300)
time.sleep(0.5)

# mouse.click('left')     # left click
# mouse.click('right')    # right click

pyautogui.click(895, 371)
pyautogui.click(895, 371)
pyautogui.click(895, 371)
pyautogui.typewrite("fulloption1998@gmail.com") # lệnh viết  
time.sleep(0.5)
pyautogui.click(1000, 500)
pyautogui.click(1000, 500)
pyautogui.typewrite("tanthanh")


pyautogui.moveTo(845, 550, duration = 0)# di chuyển chuột tới vị trí 
pyautogui.dragRel(100, 0, duration = 0) # kéo rê chuột trái ||duration kéo trong khoản thời gian bao lâu = 0 là tức thì

pyautogui.hotkey("ctrlleft", "c")       # lệnh sử dụng tổ hợp phím "ctr + c"
pyautogui.click(168, 121)
pyautogui.click(168, 121)
pyautogui.click(168, 121)
pyautogui.hotkey("ctrlleft", "v")       # lệnh sử dụng tổ hợp phím "ctr + v"
pyautogui.typewrite(["backspace", "backspace"])          # lệnh sử dụng phím từ bàn phím. Nhớ có ngoặc vuông [] nha

pyautogui.moveTo(120, 110, duration = 0)# di chuyển chuột tới vị trí 
pyautogui.dragRel(100, 0, duration = 0) # kéo rê chuột trái ||duration kéo trong khoản thời gian bao lâu = 0 là tức thì

pyautogui.hotkey("ctrlleft", "c")       # lệnh sử dụng tổ hợp phím "ctr + c"
pyautogui.click(850, 600)
pyautogui.click(850, 600)
pyautogui.click(850, 600)
pyautogui.hotkey("ctrlleft", "v")       # lệnh sử dụng tổ hợp phím "ctr + v"

# pyautogui.click(863, 602)
# pyautogui.hotkey("ctrlleft", "v")     # lệnh sử dụng tổ hợp phím "ctr + v"
# # pyautogui.typewrite("hello")
pyautogui.typewrite(["enter"])