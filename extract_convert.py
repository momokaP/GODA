import sys

from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont

import demucs.separate
from basic_pitch.inference import predict_and_save

###################################################################
#이 코드는 오픈소스 라이브러리가 낳으시고 챗gpt가 길러주신 코드입니다#
###################################################################

class DemucsThread(QThread):
    #gpt의 도움
    finished = pyqtSignal()

    def __init__(self, input_file, output_directory):
        super().__init__()
        self.input_file = input_file
        self.output_directory = output_directory

    def run(self):
        demucs.separate.main(["--mp3", "-o", self.output_directory, "-n", "htdemucs_6s", self.input_file])
        self.finished.emit()
        
#########################################################################################################

class basic_pitch_Thread(QThread):
    #gpt의 도움
    finished = pyqtSignal()
    
    def __init__(self, input_file, output_directory):
        super().__init__()
        self.input_file = [input_file]
        self.output_directory = output_directory

    def run(self):
        print(self.input_file, self.output_directory)
        predict_and_save(self.input_file, self.output_directory, 1,0,0,0)
        self.finished.emit()
          
#########################################################################################################

class extract_convert(QMainWindow):
    def __init__(self):
        super().__init__()
        self.modify_win = None
        self.convert_win = None
        self.piano_win = None
        self.piano_window = None
        self.font = QFont()
        self.font.setPointSize(12)
        self.create_ui()
        
    def showDialog1(self):
        fname, _ = QFileDialog.getOpenFileName(self, '파일 선택', '/home')
        self.before_label_demucs.setText(fname)
        
    def showDialog2(self):
        fname = QFileDialog.getExistingDirectory(self, '폴더 선택', '/home')
        self.after_label_demucs.setText(fname)
        
    def showDialog11(self):
        fname, _ = QFileDialog.getOpenFileName(self, '파일 선택', '/home')
        self.before_label_basic.setText(fname)
        
    def showDialog22(self):
        fname = QFileDialog.getExistingDirectory(self, '폴더 선택', '/home')
        self.after_label_basic.setText(fname)
        
    def start_conversion(self):
        #챗gpt 도움
        if self.before_label_demucs.text() != " ":
         
            input_file = self.before_label_demucs.text()
            output_directory = self.after_label_demucs.text()
            
            self.demucs_thread = DemucsThread(input_file, output_directory)  # 스레드 초기화

            self.demucs_thread.start()
            
    def start_conversion_basic_pitch(self):
        #챗gpt 도움
        if self.before_label_basic.text() != " ":

            input_file = self.before_label_basic.text()
            output_directory = self.after_label_basic.text()
                
            self.basic_pitch_Thread = basic_pitch_Thread(input_file, output_directory)  # 스레드 초기화
            
            self.basic_pitch_Thread.start()
            
    def sliderPressed(self):
        self.Pressed_scroll = True
        
    def create_ui(self):
        # PyQt 윈도우 생성
        self.setWindowTitle("음원분리와 mid로 변환")
        self.setGeometry(100, 100, 800, 600)
        
        # 탭 위젯 생성
        tab_widget = QTabWidget(self)
        
        # 탭 추가
        tab2 = QWidget()
        tab3 = QWidget()
        
        tab_widget.addTab(tab2, "음원 분리")
        tab_widget.addTab(tab3, "mp3 파일을 midi 파일로 변환")
        
        self.setCentralWidget(tab_widget)

        # 레이아웃
        
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        main2_top_layout = QVBoxLayout()
        main2_top_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        main2_layout = QVBoxLayout()
        main2_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        main3_top_layout = QVBoxLayout()
        main3_top_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        main3_layout = QVBoxLayout()
        main3_layout.setAlignment(Qt.AlignHCenter)
        
        ############################# 음원 분리 탭
        
        info_label_demucs = QLabel("음악을 bass, drums, guitar, piano, vocals, others로 분리합니다", self)
        info_label_demucs.setFixedSize(600, 30)
        info_label_demucs.setAlignment(Qt.AlignCenter)
        info_label_demucs.setFont(self.font)
        
        btn1 = QPushButton('음원 분리할 파일 선택', self)
        btn1.clicked.connect(self.showDialog1)
        btn1.setFixedSize(400, 40)
        btn1.setFont(self.font)
        
        btn2 = QPushButton('음원 분리한 파일을 저장할 폴더 선택', self)
        btn2.clicked.connect(self.showDialog2)
        btn2.setFixedSize(400, 40)
        btn2.setFont(self.font)
        
        btn3 = QPushButton('음원 분리 (.mp3)', self)
        btn3.clicked.connect(self.start_conversion)
        btn3.setFixedSize(400, 40)
        btn3.setFont(self.font)

        self.before_label_demucs = QLineEdit(self)
        self.before_label_demucs.setText(" ")
        self.before_label_demucs.setFixedSize(400, 40)
        self.before_label_demucs.setAlignment(Qt.AlignCenter)
        self.before_label_demucs.setFont(self.font)
        
        self.after_label_demucs = QLineEdit(self)
        self.after_label_demucs.setText("./")
        self.after_label_demucs.setFixedSize(400, 40)
        self.after_label_demucs.setAlignment(Qt.AlignCenter)
        self.after_label_demucs.setFont(self.font)
        
        main2_layout.addWidget(btn1)
        main2_layout.addWidget(self.before_label_demucs)
        main2_layout.addWidget(btn2)
        main2_layout.addWidget(self.after_label_demucs)
        main2_layout.addWidget(btn3)
        #
        main2_top_layout.addWidget(info_label_demucs)
        tab2_layout.addLayout(main2_top_layout)
        tab2_layout.addLayout(main2_layout)
        
        ############################# midi변환 탭
        
        info_label_basic = QLabel("mp3파일을 midi파일로 변환합니다 (띄어쓰기가 없어야 합니다)", self)
        info_label_basic.setFixedSize(600, 30)
        info_label_basic.setAlignment(Qt.AlignCenter)
        info_label_basic.setFont(self.font)
        
        btn1 = QPushButton('midi로 변환할 파일 선택', self)
        btn1.clicked.connect(self.showDialog11)
        btn1.setFixedSize(400, 40)
        btn1.setFont(self.font)
        
        btn2 = QPushButton('midi로 변환한 파일을 저장할 폴더 선택', self)
        btn2.clicked.connect(self.showDialog22)
        btn2.setFixedSize(400, 40)
        btn2.setFont(self.font)
        
        btn3 = QPushButton('midi로 변환', self)
        btn3.clicked.connect(self.start_conversion_basic_pitch)
        btn3.setFixedSize(400, 40)
        btn3.setFont(self.font)

        self.before_label_basic = QLineEdit(self)
        self.before_label_basic.setText(" ")
        self.before_label_basic.setFixedSize(400, 40)
        self.before_label_basic.setAlignment(Qt.AlignCenter)
        self.before_label_basic.setFont(self.font)
        
        self.after_label_basic = QLineEdit(self)
        self.after_label_basic.setText("./")
        self.after_label_basic.setFixedSize(400, 40)
        self.after_label_basic.setAlignment(Qt.AlignCenter)
        self.after_label_basic.setFont(self.font)
        
        main3_layout.addWidget(btn1)
        main3_layout.addWidget(self.before_label_basic)
        main3_layout.addWidget(btn2)
        main3_layout.addWidget(self.after_label_basic)
        main3_layout.addWidget(btn3)
        
        main3_top_layout.addWidget(info_label_basic)
        tab3_layout.addLayout(main3_top_layout)
        tab3_layout.addLayout(main3_layout)
        
        # Tkinter 이벤트 루프 시작
        self.show()

    def closeEvent(self, event):
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = extract_convert()
    sys.exit(app.exec_())