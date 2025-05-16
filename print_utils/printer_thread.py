from PySide6.QtCore import QThread, Signal, QPointF, QRectF, Qt
from PySide6.QtGui import QFont, QPainter, QFont
from PySide6.QtPrintSupport import QPrinter
# from PySide6.QtCore import QPointF

class PrinterThread(QThread):
    finished = Signal()
    error = Signal(str)
    # preview_ready = Signal(object)  # 미리보기 이미지 전달용
    
    def __init__(self, file_name = None):
        super().__init__()
        self.file_name = file_name
        self.text = "Hello, World!"  # 기본 텍스트 설정
    
    def run(self):
        try:
            printer = QPrinter()
            painter = QPainter()
            
            if painter.begin(printer):
                # 텍스트 영역을 QRectF로 정의 (x, y, width, height)
                text_rect1 = QRectF(74, 130, 133-74, 20)
                text_rect2 = QRectF(74, 150, 133-74, 20)
                
                # 정렬 옵션 설정 (가운데 정렬)
                alignment = Qt.AlignCenter
                
                # 텍스트 자동 크기 조절 함수
                def fit_text_to_rect(rect, text, max_size=10, min_size=2):
                    # 최적 폰트 크기 찾기
                    size = max_size
                    font = QFont("Pretendard", size)
                    painter.setFont(font)
                    
                    # 텍스트 너비가 사각형 너비보다 클 경우 폰트 크기 줄이기
                    while painter.fontMetrics().horizontalAdvance(text) > rect.width() and size > min_size:
                        size -= 0.5
                        font.setPointSizeF(size)
                        painter.setFont(font)
                    
                    return font
                
                # 각 텍스트 영역에 맞게 폰트 크기 조절하여 출력
                for rect in [text_rect1, text_rect2]:
                    font = fit_text_to_rect(rect, self.text)
                    painter.setFont(font)
                    painter.drawText(rect, alignment, self.text)
                
                painter.end()
                self.finished.emit()
            else:
                self.error.emit("프린터를 초기화할 수 없습니다.")
                
        except Exception as e:
            self.error.emit(f"인쇄 중 오류 발생: {str(e)}")
        