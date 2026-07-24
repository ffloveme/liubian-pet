import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QAction
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QPoint

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class HeartPaperPet(QLabel):
    def __init__(self):
        super().__init__()

        # 加载所有表情
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

        # 窗口透明与置顶
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 移动与状态变量
        self.current_state = "normal"
        self.update_image(self.images[self.current_state])

        self.is_dragging = False
        self.drag_position = QPoint()

        # 运动控制：vx (水平速度), vy (垂直速度)
        self.vx = 0
        self.vy = 0

        # 获取屏幕尺寸，防止走脱
        screen = QApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        # 1. 移动定时器：每 30 毫秒刷新一次位置（移动更平滑）
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_position)
        self.move_timer.start(30)

        # 2. 行为定时器：每 3~6 秒随机改变一次当前动作/移动方向
        self.action_timer = QTimer(self)
        self.action_timer.timeout.connect(self.random_behavior)
        self.action_timer.start(3000)

        self.show()

    def update_image(self, img_path):
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaledToHeight(200, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
            self.resize(scaled_pixmap.size())

    def random_behavior(self):
        """决定心纸君接下来的行动：站着发呆、向左/右走、散步"""
        if self.is_dragging:
            return  # 拖拽时不改变行为

        # 随机选择一种行为模式 (0: 发呆/原地表情, 1: 左右散步, 2: 随意游走)
        mode = random.choice([0, 1, 2])

        if mode == 0:
            # 原地发呆
            self.vx, self.vy = 0, 0
            self.current_state = random.choice(["normal", "doubt", "sweat", "scared"])
        elif mode == 1:
            # 沿水平线漫步
            self.vx = random.choice([-2, -1, 1, 2])
            self.vy = 0
            self.current_state = "happy" if self.vx > 0 else "shake"
        else:
            # 自由斜向游走
            self.vx = random.choice([-2, -1, 1, 2])
            self.vy = random.choice([-1, 1])
            self.current_state = random.choice(["surprised", "happy", "normal"])

        self.update_image(self.images[self.current_state])
        # 下一次行为切换的时间设为随机 3 到 6 秒
        self.action_timer.setInterval(random.randint(3000, 6000))

    def update_position(self):
        """位置更新与屏幕碰撞反弹"""
        if self.is_dragging or (self.vx == 0 and self.vy == 0):
            return

        current_pos = self.pos()
        new_x = current_pos.x() + self.vx
        new_y = current_pos.y() + self.vy

        # 碰屏幕左/右壁：反弹
        if new_x <= 0 or new_x >= (self.screen_width - self.width()):
            self.vx = -self.vx
            self.current_state = "scared"  # 撞墙吓一跳
            self.update_image(self.images[self.current_state])
            new_x = max(0, min(new_x, self.screen_width - self.width()))

        # 碰屏幕上/下壁：反弹
        if new_y <= 0 or new_y >= (self.screen_height - self.height()):
            self.vy = -self.vy
            new_y = max(0, min(new_y, self.screen_height - self.height()))

        self.move(new_x, new_y)

    # === 拖拽与点击交互 ===
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.vx, self.vy = 0, 0  # 抓起时暂停自动移动
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.current_state = "scared"  # 被抓住时表现为惶恐
            self.update_image(self.images[self.current_state])
            event.accept()

    def mouseMoveEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            # 放开鼠标后恢复开心或摇铃，并重置行为计时
            self.current_state = random.choice(["happy", "shake"])
            self.update_image(self.images[self.current_state])
            self.action_timer.start(2000)

    # === 右键菜单 ===
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # 自由活动开关
        toggle_action = QAction("暂停/恢复漫步", self)
        toggle_action.triggered.connect(self.toggle_move)
        menu.addAction(toggle_action)

        emotion_menu = menu.addMenu("手动切换表情")
        for key in self.images.keys():
            action = QAction(key.capitalize(), self)
            action.triggered.connect(lambda checked, k=key: self.set_emotion(k))
            emotion_menu.addAction(action)

        menu.addSeparator()
        
        quit_action = QAction("送心纸君回宫 (退出)", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)

        menu.exec_(event.globalPos())

    def toggle_move(self):
        if self.move_timer.isActive():
            self.move_timer.stop()
            self.action_timer.stop()
            self.vx, self.vy = 0, 0
        else:
            self.move_timer.start(30)
            self.action_timer.start(3000)

    def set_emotion(self, emotion_key):
        self.current_state = emotion_key
        self.update_image(self.images[self.current_state])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = HeartPaperPet()
    sys.exit(app.exec_())
