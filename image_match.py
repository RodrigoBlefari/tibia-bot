import cv2
from window_capture import capture_window
import win32api, win32con, win32gui

def locate_on_window(window_title, template_path, threshold=0.8):
    screenshot, hwnd = capture_window(window_title)
    if screenshot is None:
        return None, hwnd

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape
        return (max_loc[0], max_loc[1], w, h), hwnd
    return None, hwnd

def click_in_window(hwnd, x, y):
    left, top, _, _ = win32gui.GetWindowRect(hwnd)
    abs_x = left + x
    abs_y = top + y
    win32api.SetCursorPos((abs_x, abs_y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)
