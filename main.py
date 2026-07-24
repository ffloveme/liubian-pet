import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QAction
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QPoint

# 辅助函数：确保打包成 .exe 后能找到解压在临时文件夹里的图片
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class HeartPaperPet(QLabel):
    def __init__(self):
        super().__init__()

        # 名字必须与 GitHub 仓库里的 .png 图片文件名完全一致
        self.images = {
            "normal": resource_path("刘辩-心纸君-正常.png"),
            "happy": resource_path("刘辩-心纸君-开心.png"),
            "sad": resource_path("刘辩-心纸君-哭哭.png"),
            "angry": resource_path("刘辩-心纸君-生气.png"),
            "surprised": resource_path("刘辩-心纸君-惊讶.png"),
            "scared": resource_path("刘辩-心纸君-惶恐.png"),
            "sweat": resource_path("刘辩-心纸君-流汗.png"),
            "shake": resource_path("刘辩-心纸君-摇铃.png"),
            "doubt": resource_path("刘辩-心纸君-疑惑.png")
        }

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.current_state = "normal"
        self.update_image(self.images[self.current_state])

        self.is_dragging = False
        self.drag_position = QPoint()

        # 每 10 秒自动随机换表情
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.random_change_emotion)
        self.timer.start(10000)

        self.show()

    def update_image(self, img_path):
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaledToHeight(220, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
            self.resize(scaled_pixmap.size())

    def random_change_emotion(self):
        emotions = list(self.images.keys())
        self.current_state = random.choice(emotions)
        self.update_image(self.images[self.current_state])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            click_emotions = ["happy", "shake", "surprised", "doubt"]
            self.current_state = random.choice(click_emotions)
            self.update_image(self.images[self.current_state])

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        emotion_menu = menu.addMenu("切换表情")
        for key in self.images.keys():
            action = QAction(key.capitalize(), self)
            action.triggered.connect(lambda checked, k=key: self.set_emotion(k))
            emotion_menu.addAction(action)

        menu.addSeparator()
        
        quit_action = QAction("送心纸君回宫 (退出)", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)

        menu.exec_(event.globalPos())

    def set_emotion(self, emotion_key):
        self.current_state = emotion_key
        self.update_image(self.images[self.current_state])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = HeartPaperPet()
    sys.exit(app.exec_())
