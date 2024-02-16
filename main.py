# gerekli kutuphaneler
import sys
import cv2
import socket
import pymongo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from datetime import datetime, timedelta


class FaceDetectionThread(QThread):
    face_detected = pyqtSignal()

    def __init__(self, mongo_collection):
        super(FaceDetectionThread, self).__init__()
        self.mongo_collection = mongo_collection

    def save_data_to_mongo(self, data):
        if self.mongo_collection is not None:  
            self.mongo_collection.insert_one(data)

    def run(self):

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)

        while self.isRunning():
            ret, frame = cap.read()

            if not ret or frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)


            cv2.imshow('Face Detection', frame)
            

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


            if len(faces) > 0:
                self.face_detected.emit()

   
                timestamp = datetime.now()
                data = {
                    "timestamp": timestamp,
                    "face_coordinates": [(x, y, w, h) for (x, y, w, h) in faces]
                }
                self.save_data_to_mongo(data)

        cap.release()
        cv2.destroyAllWindows()

class WebBrowser(QMainWindow):
    def __init__(self):
        super(WebBrowser, self).__init__()


        self.mongo_client = pymongo.MongoClient("mongodb://brndagdln:sifre@localhost:27017/")
        self.mongo_db = self.mongo_client["Gedik"]
        self.mongo_collection = self.mongo_db["baglanti"]

        self.webview = QWebEngineView(self)
        self.setCentralWidget(self.webview)

        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction('Back', self)
        back_btn.setStatusTip('Back to previous page')
        back_btn.triggered.connect(self.webview.back)
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.setStatusTip('Forward to next page')
        forward_btn.triggered.connect(self.webview.forward)
        navbar.addAction(forward_btn)

        scan_btn = QAction('Scan', self)
        scan_btn.setStatusTip('Scan for ports')
        scan_btn.triggered.connect(self.scan_ports)
        navbar.addAction(scan_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.setStatusTip('Reload page')
        reload_btn.triggered.connect(self.webview.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.setStatusTip('Go home')
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        urlbar = QLineEdit()
        urlbar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(urlbar)

        go_btn = QPushButton('Go')
        go_btn.clicked.connect(self.navigate_to_url)
        navbar.addWidget(go_btn)

        scan_face_btn = QPushButton('Scan Face')
        scan_face_btn.clicked.connect(self.toggle_face_detection)
        navbar.addWidget(scan_face_btn)

        self.setWindowTitle('Web Browser')
        self.setGeometry(100, 100, 1024, 768)
        self.showMaximized()
        self.webview.setUrl(QUrl("http://www.google.com"))

        self.face_thread = FaceDetectionThread(self.mongo_collection)
        self.face_detection_running = False

    def closeEvent(self, event):
        if self.mongo_client:
            self.mongo_client.close()
        event.accept()

    def navigate_home(self):
        self.webview.setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        q = QUrl(self.sender().text())

        if q.scheme() == '':
            q.setScheme('http')

        self.webview.setUrl(q)

    def scan_ports(self):
        url = self.webview.url()
        if not url.isValid() or not url.scheme() == 'https':
            return

        host = url.host()
        ports = [21, 2280, 443, 3306]

        open_ports = []
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            sock.close()

        if open_ports:
            QMessageBox.information(self, "Port Scan Result", f"Open ports: {', '.join(map(str, open_ports))}")
        else:
            QMessageBox.information(self, "Port Scan Result", "No open ports found.")

    def toggle_face_detection(self):
        if not self.face_detection_running:
            self.face_thread.start()
            self.face_detection_running = True
        else:
            self.face_thread.quit()
            self.face_thread.wait()
            self.face_detection_running = False

    def handle_face_detected(self):
        QMessageBox.information(self, "Face Detection", "Face detected!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("WebBrowser")

    window = WebBrowser()
    window.show()
    sys.exit(app.exec_())
