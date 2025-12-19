from numpy import uint8, ndarray as NDArray
from picamera2 import Picamera2, Preview
import os

# Fix Qt plugin path conflict between opencv and PyQt5
if 'QT_QPA_PLATFORM_PLUGIN_PATH' not in os.environ:
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/usr/lib/aarch64-linux-gnu/qt5/plugins'

import cv2
from cv2.typing import MatLike
from typing import Optional

class Camera:
    def __init__(self, width: int, height: int, format: str, show_preview: bool = False):
        self.width = width
        self.height = height
        self.format = format
        self.picam2 = Picamera2()
        
        # Start preview if requested
        if show_preview:
            # Set DISPLAY for VNC if not already set
            if 'DISPLAY' not in os.environ:
                os.environ['DISPLAY'] = ':0'
            
            self.picam2.start_preview(Preview.QTGL)

        
        # Configure camera with better settings for indoor/varied lighting
        config = self.picam2.create_preview_configuration(
            main={"size": (width, height), "format": format}
        )
        self.picam2.configure(config)
        
        # Set camera controls for better image quality
        self.picam2.set_controls({
            "AwbEnable": True,           # Auto white balance
            "AeEnable": True,            # Auto exposure
            "AwbMode": 0,                # Auto white balance mode (0 = auto)
            "Brightness": 0.0,           # Brightness adjustment (-1.0 to 1.0)
            "Contrast": 1.5,             # Contrast (0.0 to 2.0, 1.0 = normal)
            "ExposureValue": 0.0,        # Exposure compensation (-8.0 to 8.0)
        })
        
        self.picam2.start()
        self.current_frame: Optional[NDArray] = None
        self.current_gray: Optional[NDArray] = None
        self.current_destination: Optional[tuple[int,int]] = None
        self.qr_detector = cv2.QRCodeDetector()
        self.current_qr: Optional[MatLike] = None

    def get_frame(self) -> 'Camera':
        self.current_frame = self.picam2.capture_array()
        return self

    def get_gray(self) -> 'Camera':
        self.current_gray = None
        if self.current_frame is not None:
            self.current_gray = self.current_frame[:self.height, :self.width]
        return self
    
    def detect_qr(self) -> 'Camera':
        self.current_qr = None
        if self.current_gray is None:
            return self
        retval, pts = self.qr_detector.detect(self.current_gray)
        if retval and pts is not None and len(pts) > 0:
            try:
                data, decoded_pts, _ = self.qr_detector.detectAndDecode(self.current_gray, pts)
                if data and len(data.strip()) > 0:
                    print(f"QR positions: {decoded_pts}")
                    self.current_qr = decoded_pts
            except cv2.error:
                pass
        return self
    
    def get_qr_center(self) -> 'Camera':
        self.current_destination = None
        if self.current_qr is None:
            return self
        pts = self.current_qr.astype(int).reshape(-1, 2)
        center_x = int(pts[:, 0].mean())
        center_y = int(pts[:, 1].mean())
        self.current_destination = (center_x, center_y)
        print(f"QR center: {self.current_destination}")
        return self
        