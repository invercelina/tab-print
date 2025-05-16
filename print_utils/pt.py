from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont, QFontMetrics
from .device_functions import get_device_list, get_device_id, open_device, print_image, close_device
from .cffi_defs import ffi, lib, SMART_OPENDEVICE_BYID, PAGE_FRONT, PANELID_BLACK

class PrinterThread(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, file_name=None):
        super().__init__()
        self.file_name = file_name
        self.text = "Hello, World!"  # 기본 텍스트 설정

    def calculate_appropriate_font_width(self, text, max_width=208):
        if not text:
            return 25
        if len(text) * 25 < max_width:
            font_width = 25
        else:
            font_width = max(1, int(max_width / len(text)) + 4)

        uppercase_count = sum(1 for c in text if c.isupper())
        uppercase_ratio = uppercase_count / len(text) if text else 0

        if uppercase_ratio >= 0.5:
            font_width = max(1, font_width - 1)
        if uppercase_ratio >= 0.8:
            font_width = max(1, font_width - 1)

        return font_width

    def run(self):
        try:
            result, printer_list = get_device_list()
            if result != 0:
                self.error.emit("프린터 목록 가져오기 실패")
                return

            device_index = 0
            device_id = get_device_id(printer_list, device_index)

            result, device_handle = open_device(device_id, SMART_OPENDEVICE_BYID)
            if result != 0:
                self.error.emit("장치 열기 실패")
                return

            try:
                font_name = "Pretendard"
                font_size = 14
                font_width = self.calculate_appropriate_font_width(self.text)

                def draw_text_at(y_pos):
                    draw_info = ffi.new("DRAWTEXT2INFO*")
                    draw_info.x = 220
                    draw_info.y = y_pos
                    draw_info.cx = 208
                    draw_info.cy = 100
                    draw_info.rotate = 0
                    draw_info.align = 0x01 | 0x10  # 가운데 정렬
                    draw_info.fontHeight = font_size
                    draw_info.fontWidth = font_width
                    draw_info.style = 0x01  # FONT_BOLD
                    draw_info.color = 0x000000
                    draw_info.option = 0  # TEXT_NOFIT

                    font_encoded = font_name.encode("utf-16-le")
                    ffi.memmove(draw_info.szFaceName, font_encoded, min(len(font_encoded), 64))

                    text_w = ffi.new("wchar_t[]", self.text)
                    result = lib.SmartComm_DrawText2(
                        device_handle,
                        PAGE_FRONT,
                        PANELID_BLACK,  # 흑백 패널
                        draw_info,
                        text_w
                    )
                    return result

                # 첫 번째 줄 출력
                if draw_text_at(413) != 0:
                    self.error.emit("첫 번째 텍스트 그리기 실패")
                    return

                # 두 번째 줄 출력
                if draw_text_at(476) != 0:
                    self.error.emit("두 번째 텍스트 그리기 실패")
                    return

                result = print_image(device_handle)
                if result != 0:
                    self.error.emit("이미지 인쇄 실패")
                    return

                self.finished.emit()

            finally:
                close_device(device_handle)

        except Exception as e:
            self.error.emit(f"인쇄 중 오류 발생: {str(e)}")
