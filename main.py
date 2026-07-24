import sys
import random
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QAction
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QPoint

class HeartPaperPet(QLabel):
    def __init__(self):
        super().__init__()

        # 1. 资源配置文件名映射
        self.images = {
            "normal": "刘辩-心纸君-正常.png",
            "happy": "刘辩-心纸君-开心.png",
            "sad": "刘辩-心纸君-哭哭.png",
            "angry": "刘辩-心纸君-生气.png",
            "surprised": "刘辩-心纸君-惊讶.png",
            "scared": "刘辩-心纸君-惶恐.png",
            "sweat": "刘辩-心纸君-流汗.png",
            "shake": "刘辩-心纸君-摇铃.jpg"
        }

        # 2. 窗口无边框、置顶、背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 3. 初始化显示图片
        self.current_state = "normal"
        self.update_image(self.images[self.current_state])

        # 4. 拖拽相关变量
        self.is_dragging = False
        self.drag_position = QPoint()

        # 5. 定时器：随机切换表情（每 10 秒随机触发一次状态变化）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.random_change_emotion)
        self.timer.start(10000)

        self.show()

    def update_image(self, img_path):
        """更新桌宠显示的图片"""
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            # 缩放到合适大小（如高 200px，保持比例）
            scaled_pixmap = pixmap.scaledToHeight(200, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
            self.resize(scaled_pixmap.size())

    def random_change_emotion(self):
        """随机切换心纸君的表情"""
        emotions = list(self.images.keys())
        self.current_state = random.choice(emotions)
        self.update_image(self.images[self.current_state])

    # === 鼠标事件：拖拽与点击交互 ===
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
            # 左键点击时切换到“开心”或“摇铃”
            click_emotions = ["happy", "shake", "surprised"]
            self.current_state = random.choice(click_emotions)
            self.update_image(self.images[self.current_state])

    # === 右键菜单 ===
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # 表情手动切换子菜单
        emotion_menu = menu.addMenu("切换表情")
        for key in self.images.keys():
            action = QAction(key.capitalize(), self)
            action.triggered.connect(lambda checked, k=key: self.set_emotion(k))
            emotion_menu.addAction(action)

        menu.addSeparator()
        
        # 退出选项
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
