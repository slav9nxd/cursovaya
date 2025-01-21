from PyQt6.QtWidgets import QApplication, QMainWindow, QSplashScreen
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QTimer
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

# Базовый класс для шифрования
class BaseCipher:
    def encrypt(self, text):
        raise NotImplementedError("Implement encryption in subclass")

    def decrypt(self, text):
        raise NotImplementedError("Implement decryption in subclass")

# Реализация шифра Виженера
class VigenereCipher(BaseCipher):
    def __init__(self, key):
        self.key = key.upper()

    def encrypt(self, text):
        result = []
        key_index = 0
        for char in text:
            if char.isalpha():
                shift = ord(self.key[key_index % len(self.key)]) - ord('A')
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base + shift) % 26 + base))
                key_index += 1
            else:
                result.append(char)
        return ''.join(result)

    def decrypt(self, text):
        result = []
        key_index = 0
        for char in text:
            if char.isalpha():
                shift = ord(self.key[key_index % len(self.key)]) - ord('A')
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base - shift) % 26 + base))
                key_index += 1
            else:
                result.append(char)
        return ''.join(result)

# Генерация цифровой рамки
def generate_frame(bits, duration=0.1, rate=100):
    t = np.linspace(0, duration * len(bits), int(len(bits) * rate * duration))
    y = np.repeat(bits, int(rate * duration))
    return t, y

# Построение графика цифровой рамки
def plot_frame(bits, duration=0.1, rate=100):
    t, y = generate_frame(bits, duration, rate)
    plt.figure(figsize=(6, 3))
    plt.plot(t, y, drawstyle="steps-pre", label="Digital Frame")
    plt.title("Digital Frame")
    plt.xlabel("Time (s)")
    plt.ylabel("Signal Level")
    plt.ylim(-0.5, 1.5)
    plt.yticks([0, 1], ["0", "1"])
    plt.grid(True)
    plt.legend()
    plt.savefig("frame_plot.png")
    plt.close()

# Низкочастотный фильтр
def lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    norm_cutoff = cutoff / nyq
    b, a = butter(order, norm_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("mainwindow.ui", self)

        # Устанавливаем значение ключа по умолчанию
        self.lineEdit_key.setText("DEFAULT")

        # Применение базового стиля
        self.apply_default_styles()

        # Привязка кнопок
        self.shifr.clicked.connect(self.handle_encrypt)
        self.deshifr.clicked.connect(self.handle_decrypt)
        self.ramka.clicked.connect(self.show_frame)
        self.filtr_signala.clicked.connect(self.filter_signal)

    def apply_default_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E3A5F;
            }
            QPushButton {
                background-color: #3B6CA6;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4A8DDC;
            }
            QLabel {
                color: white;
            }
            QLineEdit, QTextEdit {
                background-color: rgba(30, 58, 95, 0.8);
                color: white;
                border: 2px solid #3B6CA6;
                border-radius: 5px;
                padding: 5px;
            }
        """)

    def handle_encrypt(self):
        text = self.vvod_inf.text()
        key = self.lineEdit_key.text() or "DEFAULT"
        cipher = VigenereCipher(key)
        encrypted = cipher.encrypt(text)
        self.vvod_inf.setText(encrypted)

        # Шаги шифрования
        steps = []
        key_index = 0
        for char in text:
            if char.isalpha():
                shift = ord(key[key_index % len(key)].upper()) - ord('A')
                base = ord('A') if char.isupper() else ord('a')
                shifted_char = chr((ord(char) - base + shift) % 26 + base)
                steps.append(f"'{char}' -> '{shifted_char}' (shift={shift})")
                key_index += 1
            else:
                steps.append(f"'{char}' remains unchanged")
        self.textEdit_steps.setText("\n".join(steps))

    def handle_decrypt(self):
        text = self.vvod_inf.text()
        key = self.lineEdit_key.text() or "DEFAULT"
        cipher = VigenereCipher(key)
        decrypted = cipher.decrypt(text)
        self.vvod_inf.setText(decrypted)

        # Шаги дешифрования
        steps = []
        key_index = 0
        for char in text:
            if char.isalpha():
                shift = ord(key[key_index % len(key)].upper()) - ord('A')
                base = ord('A') if char.isupper() else ord('a')
                original_char = chr((ord(char) - base - shift) % 26 + base)
                steps.append(f"'{char}' -> '{original_char}' (unshift={shift})")
                key_index += 1
            else:
                steps.append(f"'{char}' remains unchanged")
        self.textEdit_steps.setText("\n".join(steps))

    def show_frame(self):
        bits = [1, 0, 1, 1, 0, 0, 1]
        plot_frame(bits)
        self.label_ramka.setPixmap(QPixmap("frame_plot.png"))

    def filter_signal(self):
        fs = 1000
        t = np.linspace(0, 1, fs)
        signal = np.sin(2 * np.pi * 50 * t) + 0.5 * np.random.randn(len(t))
        filtered = lowpass_filter(signal, 100, fs)

        plt.figure(figsize=(10, 5))
        plt.subplot(2, 1, 1)
        plt.plot(t, signal, label="Original Signal")
        plt.title("Before Filtering")
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(t, filtered, label="Filtered Signal")
        plt.title("After Filtering")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()