from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QSizePolicy, QHBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

class VirtualKeyboard(QWidget):
    def __init__(self, input_widget):
        super().__init__()
        self.input_widget = input_widget
        self.is_uppercase = False
        
        # 키보드 색상 및 스타일 설정
        self.bg_color = "#FFFFFF"
        self.border_color = "#CCCCCC"
        self.border_width = 1
        self.border_radius = 10
        self.padding = 10
        self.button_bg_color = "#F0F0F0"
        self.button_text_color = "#000000"
        self.button_pressed_color = "#E0E0E0"
        self.button_radius = 5
        self.shift_btn_color = "#D3D3D3"
        self.shift_btn_active_color = "#007BFF"  # 대문자 상태일 때 shift 키 색상
        self.backspace_btn_color = "#FF0000"
        self.next_btn_color = "#4CAF50"
        self.font_size = 30
        self.special_btn_width = 80
        
        # 콜백 함수 초기화
        self.on_next_pressed = None
        
        # 제목 표시줄 제거 및 항상 상위에 유지
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.initUI()
        self.update_keyboard_labels()

        self.bumper = False

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.setStyleSheet(f"""
        VirtualKeyboard {{
            background-color: {self.bg_color};
            border: {self.border_width}px solid {self.border_color};
            border-radius: {self.border_radius}px;
            padding: {self.padding}px;
        }}
        """)
            
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '←'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
        ]

        # 버튼 고정 너비 계산 (첫 세 줄에만 적용)
        self.fixed_button_width = 100
        
        self.button_widgets = []
        for row_idx, row in enumerate(self.keys):
            row_buttons = []
            
            # 상단 3줄은 고정 너비 사용
            if row_idx < 4:
                row_layout = QHBoxLayout()
                row_layout.setSpacing(5)
                
                for key in row:
                    button = QPushButton(self.get_display_key(key))
                    button.setFont(QFont('Pretendard', self.font_size))
                    
                    # Backspace 버튼 특별 처리
                    if key == '←':
                        button.clicked.connect(self.backspace)
                        button.setStyleSheet(self.get_special_button_style(self.backspace_btn_color))
                    else:
                        button.clicked.connect(lambda checked, text=key: self.button_clicked(text))
                        button.setStyleSheet(self.get_button_style())
                    
                    # 버튼 너비 고정, 높이는 확장
                    button.setFixedWidth(self.fixed_button_width)
                    button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                    
                    row_layout.addWidget(button)
                    row_buttons.append(button)
                
                # 각 줄을 중앙 정렬
                row_layout.addStretch(1)
                row_layout.insertStretch(0, 1)
            
            # 마지막 줄은 기존 방식 유지
            else:
                row_layout = QGridLayout()
                row_layout.setSpacing(5)
                
                for i, key in enumerate(row):
                    button = QPushButton(self.get_display_key(key))
                    button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                    button.setFont(QFont('Pretendard', self.font_size))
                    
                    # Backspace 버튼 특별 처리
                    if key == '←':
                        button.clicked.connect(self.backspace)
                        button.setStyleSheet(self.get_special_button_style(self.backspace_btn_color))
                    else:
                        button.clicked.connect(lambda checked, text=key: self.button_clicked(text))
                        button.setStyleSheet(self.get_button_style())
                    row_layout.addWidget(button, 0, i)
                    row_buttons.append(button)
            
            self.layout.addLayout(row_layout)
            self.button_widgets.append(row_buttons)

        special_layout = QGridLayout()
        special_layout.setSpacing(5)

        # 각 버튼 설정
        shift_btn = QPushButton('Shift')
        shift_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        shift_btn.setFont(QFont('Pretendard', self.font_size))
        shift_btn.clicked.connect(self.toggle_shift)
        shift_btn.setStyleSheet(self.get_special_button_style(self.shift_btn_color))
        shift_btn.setFixedWidth(200)

        space_btn = QPushButton('Space')
        space_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        space_btn.setFont(QFont('Pretendard', self.font_size))
        space_btn.clicked.connect(self.space_pressed)
        space_btn.setStyleSheet(self.get_button_style())
        space_btn.setFixedWidth(600)

        # 다음 버튼 추가
        next_btn = QPushButton('다음')
        next_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        next_btn.setFont(QFont('Pretendard', self.font_size))
        next_btn.clicked.connect(self.next_pressed)
        next_btn.setStyleSheet(self.get_special_button_style(self.next_btn_color))
        next_btn.setFixedWidth(200)
        
        # 레이아웃에 버튼 추가
        special_layout.addWidget(shift_btn, 0, 0)
        special_layout.addWidget(space_btn, 0, 1)
        special_layout.addWidget(next_btn, 0, 2)
        
        # 열 비율 설정 제거 (고정 너비 사용)
        # special_layout.setColumnStretch(0, 2)
        # special_layout.setColumnStretch(1, 4)
        # special_layout.setColumnStretch(2, 2)

        self.layout.addLayout(special_layout)
        self.setLayout(self.layout)

    def button_clicked(self, key):
        current_text = self.input_widget.text()
        
        char = key.upper() if self.is_uppercase else key.lower()
        self.input_widget.setText(current_text + char)
        self.bumper = True
        
    def insert_text(self, char):
        if char:
            self.input_widget.setText(self.input_widget.text() + char)
            self.input_widget.setCursorPosition(len(self.input_widget.text()))

    def toggle_shift(self):
        self.is_uppercase = not self.is_uppercase
        self.update_keyboard_labels()
        
        # shift 버튼 색상 업데이트
        shift_button = None
        for widget in self.findChildren(QPushButton):
            if widget.text().lower() == 'shift':
                shift_button = widget
                break
                
        if shift_button:
            if self.is_uppercase:
                shift_button.setStyleSheet(self.get_special_button_style(self.shift_btn_active_color))
            else:
                shift_button.setStyleSheet(self.get_special_button_style(self.shift_btn_color))

    def space_pressed(self):
        self.insert_text(' ')
        self.bumper = True

    def backspace(self):
        text = self.input_widget.text()
        if not text:
            return

        text = text[:-1]
        self.input_widget.setText(text)
        self.input_widget.setCursorPosition(len(text))

    def next_pressed(self):
        """다음 버튼 클릭 시 동작"""
        # shift 상태 초기화 (대문자 상태 해제)
        if self.is_uppercase:
            self.is_uppercase = False
            self.update_keyboard_labels()
            
            # shift 버튼 색상 업데이트
            shift_button = None
            for widget in self.findChildren(QPushButton):
                if widget.text().lower() == 'shift':
                    shift_button = widget
                    break
                    
            if shift_button:
                shift_button.setStyleSheet(self.get_special_button_style(self.shift_btn_color))
        
        # 콜백 함수가 설정되어 있으면 호출
        if self.on_next_pressed:
            self.on_next_pressed()
            
    def update_keyboard_labels(self):
        for row_buttons, row_keys in zip(self.button_widgets, self.keys):
            for button, key in zip(row_buttons, row_keys):
                button.setText(key.upper() if self.is_uppercase else key.lower())

    def get_display_key(self, key):
        if self.is_uppercase:
            return key.upper()
        return key.lower()

    def get_button_style(self):
        return f"""
            QPushButton {{
                background-color: {self.button_bg_color};
                color: {self.button_text_color};
                border: none;
                border-radius: {self.button_radius}px;
            }}
            QPushButton:pressed {{
                background-color: {self.button_pressed_color};
            }}
        """

    def get_special_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: {self.button_text_color};
                border: none;
                border-radius: {self.button_radius}px;
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """

    def darken_color(self, color):
        # 색상 코드가 #RRGGBB 형식이라고 가정
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        return f'#{max(0, r-30):02X}{max(0, g-30):02X}{max(0, b-30):02X}'