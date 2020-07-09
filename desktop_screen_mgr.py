import pyautogui
import threading


class Config:
    screen_size = (1280, 720)


while True:
    # make a screenshot
    img = pyautogui.screenshot()
    img.save('screenshots/last.jpg')
    # open('screenshots/last.jpg', 'wb').write(img)
    input('Enter...')