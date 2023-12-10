import sys

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtWidgets import QFileDialog, QGraphicsRectItem, QApplication, QMainWindow, QWidget, QGridLayout
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtWidgets import QMessageBox, QGraphicsLineItem, QTabWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QPen, QColor, QFont

import pretty_midi
import sounddevice as sd

import numpy as np

import threading

###################################################################
#이 코드는 오픈소스 라이브러리가 낳으시고 챗gpt가 길러주신 코드입니다#
###################################################################

#########################################################################################################

class VerticalPiano(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vertical Piano")

        self.notes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.octave = 4

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.create_piano_layout()
        self.create_piano_buttons()
        self.Pressed_scroll = False
        
        self.create_octave_entry()

        self.show()

    def create_piano_layout(self):
        self.vertical_layout = QVBoxLayout(self.central_widget)
        
        self.horizontal_layout_top = QHBoxLayout(self.central_widget)
        self.horizontal_layout_mid = QHBoxLayout(self.central_widget)
        self.horizontal_layout_low = QHBoxLayout(self.central_widget)
        
        self.grid_layout = QGridLayout(self.central_widget)

    def create_octave_entry(self):
        
        self.octave_entry = QLineEdit(self)
        self.octave_entry.insert("4")  # Initial value
        self.octave_entry.setFixedWidth(200)
        
        button = QPushButton("옥타브 변환")
        button.clicked.connect(self.update_octave)
        
        self.grid_layout.addWidget(self.octave_entry,0,1)
        self.grid_layout.addWidget(button,0,2)
        
        self.vertical_layout.addLayout(self.grid_layout)

    def create_piano_buttons(self):
        
        self.note_buttons_mid = {}
        self.note_buttons_top = {}
        self.note_buttons_bottom = {}
        
        for i in range(-1, 2):
            for (note, note_name) in zip(self.notes, self.note_names):
                octave = self.octave + i
                note_label = f"{note_name}{octave}"
                
                button = QPushButton(note_label)
                button.clicked.connect(lambda state, n=note, tmb=i: self.play_note(n, tmb))
                
                if i==0 : 
                    self.horizontal_layout_mid.addWidget(button)
                    self.note_buttons_mid[note] = button
                elif i==-1 : 
                    self.horizontal_layout_top.addWidget(button)
                    self.note_buttons_top[note] = button
                else : 
                    self.horizontal_layout_low.addWidget(button)
                    self.note_buttons_bottom[note] = button
                
        self.vertical_layout.addLayout(self.horizontal_layout_top)
        self.vertical_layout.addLayout(self.horizontal_layout_mid)
        self.vertical_layout.addLayout(self.horizontal_layout_low)

        self.setFixedSize(1200,180)

    def play_note(self, note, tmb):
        # 챗gpt 도움
        octave = int(self.octave_entry.text()) + tmb
        if octave >= 8: octave = 8
        if octave <= 0: octave = 0
        frequency = 440 * 2 ** ((note + 12 * (octave + 1) - 69) / 12.0)
        duration = 0.5
        initial_volume = 1

        t = np.linspace(0, duration, int(44100 * duration), False)
        
        # 사인파를 그대로 두면 음이 끝날때 진폭이 남아있기 때문에 틱 소리가 난다
        # 이를 막기 위해서 시간이 갈 수록 사인파의 진폭을 줄인다
        decay_start = int(44100 * duration * (1 / 100))
        decay_factor = np.exp(-5 * (t[decay_start:] - t[decay_start]) / duration)

        signal = initial_volume * np.sin(2 * np.pi * frequency * t)
        signal[decay_start:] *= decay_factor

        sd.play(signal, samplerate=44100, blocking=True)

    def update_octave(self):
        try:
            if 9 > int(self.octave_entry.text()) >= 0:
                octave = int(self.octave_entry.text())

                # Update buttons
                for i in range(-1, 2):
                    for (note, note_name) in zip(self.notes, self.note_names):
                        note_label = f"{note_name}{octave + i}"  
                        if i==0 : self.note_buttons_mid[note].setText(note_label) # = note_label
                        elif i==-1 : self.note_buttons_top[note].setText(note_label)
                        else : self.note_buttons_bottom[note].setText(note_label)
            else:
                pass
        except ValueError:
            pass
        
#########################################################################################################

class MidiVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.modify_win = None
        self.convert_win = None
        self.piano_win = None
        self.piano_window = None
        self.font = QFont()
        self.font.setPointSize(12)
        self.create_ui()

    def load_and_visualize(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open MIDI File", "", "MIDI Files (*.midi *.mid);;All Files (*)")

        if file_path:
            self.midi_data = pretty_midi.PrettyMIDI(file_path)
            self.raw_midi_data = self.midi_data
            if self.raw_midi_data:
                self.visualize_midi()
            else:
                print("지원하지 않는 파일 형식입니다")
                pass
        else:
            print("파일 경로가 잘못 된 경로입니다")
            pass
            
    def modify_button_clicked(self):
        start = int(self.start_text_input.text())
        end = int(self.end_text_input.text())
        what_note = [ i for i in range(int(self.note_text_input.text()), int(self.note_text_input2.text())+1)]
        velocity = int(self.volume_text_input.text())
        
        for i,what in enumerate(what_note):
            if what > 127:
                what_note[i] = 127
            if what <= 0:
                what_note[i] = 0    
            
        if velocity > 127:
            velocity = 127 
        
        try:
            if velocity <=0:
                notes_to_remove = []
    
                for note in self.raw_midi_data.instruments[0].notes: 
                    if start <= int(note.start*100) < end and int(note.end*100) <= end:
                        for what in what_note:
                            if note.pitch==what:
                                notes_to_remove.append(note)

                for note in notes_to_remove:
                    self.raw_midi_data.instruments[0].notes.remove(note)
                    
            else:
                for note in self.raw_midi_data.instruments[0].notes:
                    if start <= int(note.start*100) < end and int(note.end*100) <= end:
                        for what in what_note:
                            if note.pitch==what:     
                                note.velocity = velocity
                else:
                    notes_to_remove = []
        
                    for note in self.raw_midi_data.instruments[0].notes: 
                        if start <= int(note.start*100) < end and int(note.end*100) <= end:
                            for what in what_note:
                                if note.pitch==what:
                                    notes_to_remove.append(note)

                    for note in notes_to_remove:
                        self.raw_midi_data.instruments[0].notes.remove(note)
                        
                    for what in what_note:
                        self.raw_midi_data.instruments[0].notes.append(
                            pretty_midi.Note(velocity=velocity, pitch=what, start=start/100, end=end/100)
                            )
                
            self.visualize_midi() 
        except:
            QMessageBox.warning(None, '경고', '먼저 mid file을 load하십시오.', QMessageBox.Ok)

    def modify_window(self):
        if not self.modify_win:
            
            self.modify_win = QMainWindow(self)
            self.modify_win.setWindowTitle('Note Modify')
            self.modify_win.setGeometry(200, 200, 350, 300)
            self.modify_win.setFixedSize(350, 300)
            
            start_label = QLabel('Start Time (ms)', self.modify_win)
            start_label.move(10, 20) 
            start_label.resize(150, 20)
            
            self.start_text_input = QLineEdit(self.modify_win)
            self.start_text_input.setText('0')
            self.start_text_input.move(200, 20)  
        
            end_label = QLabel('End Time (ms)', self.modify_win)
            end_label.move(10, 60)  
            end_label.resize(150, 20)
            
            self.end_text_input = QLineEdit(self.modify_win)
            self.end_text_input.setText('0')
            self.end_text_input.move(200, 60) 

            note_label = QLabel('strat Note (0~127)', self.modify_win)
            note_label.move(10, 100)  
            note_label.resize(150, 20)
            
            self.note_text_input = QLineEdit(self.modify_win)
            self.note_text_input.setText('0')
            self.note_text_input.move(200, 100) 
            self.note_text_input.textChanged.connect(self.onTextChanged)
            
            note_label2 = QLabel('end Note (0~127)', self.modify_win)
            note_label2.move(10, 140)  
            note_label2.resize(150, 20)
            
            self.note_text_input2 = QLineEdit(self.modify_win)
            self.note_text_input2.setText('0')
            self.note_text_input2.move(200, 140)  

            volume_label = QLabel('Volume (0~127)', self.modify_win)
            volume_label.move(10, 180)  
            volume_label.resize(150, 20)
            
            self.volume_text_input = QLineEdit(self.modify_win)
            self.volume_text_input.setText('0')
            self.volume_text_input.move(200, 180)  

            modify_button = QPushButton('Modify!', self.modify_win)
            modify_button.move(200, 220)  
            
            modify_button.clicked.connect(self.modify_button_clicked)

        # 이미 열려있는 창이면 활성화하고, 아니면 보여주기 gpt도움
        if not self.modify_win.isVisible():
            self.modify_win.show()
        else:
            self.modify_win.activateWindow()
            
    def onTextChanged(self,text):
        self.note_text_input2.setText(text)    
        
    def show_dialog(self):
        self.directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        self.directory_name_input.setText(f'{self.directory}')
        
    def convert_save(self):
        #챗gpt 도움
        try:
            output_midi_file_path = self.directory_name_input.text() + "/" + self.save_file_name_input.text()
            load_midi = pretty_midi.PrettyMIDI()
    
            # 악기 배정 일단 트랙 1개만 사용한다 
            # 이후에 여러 트랙을 나타낼 수 있으면 여러 트랙도 가능하도록 한다
            new_instrument = pretty_midi.Instrument(program=self.raw_midi_data.instruments[0].program)
    
            # 노트 추가
            for note in self.raw_midi_data.instruments[0].notes:
                new_instrument.notes.append(note)
    
            # 새로운 악기를 새로운 MIDI 파일에 추가
            load_midi.instruments.append(new_instrument)
                        
            # 수정된 MIDI 파일 저장
            load_midi.write(output_midi_file_path)
            QMessageBox.warning(None, '저장', '저장했습니다 확인해 보십시오.', QMessageBox.Ok)
        except:
            QMessageBox.warning(None, '경고', '먼저 mid file을 load하십시오.', QMessageBox.Ok)
            
    def convert_window(self):
        if not self.convert_win:
            
            self.convert_win = QMainWindow(self)
            self.convert_win.setWindowTitle('mid 파일 저장')
            self.convert_win.setGeometry(200, 200, 400, 300)
            self.convert_win.setFixedSize(400, 300)
            
            directory_name_label = QLabel('저장할 폴더를 선택하시오', self.convert_win)
            directory_name_label.move(60, 25)
            directory_name_label.resize(200, 20)
            
            directory_button = QPushButton('폴더 선택', self.convert_win)
            directory_button.move(240, 20)
            directory_button.clicked.connect(self.show_dialog)
            
            self.directory_name_input = QLineEdit(self.convert_win)
            self.directory_name_input.setText('./')
            self.directory_name_input.move(70, 60)
            self.directory_name_input.resize(250, 20)
            
            save_file_name_label = QLabel('저장할 .mid 파일 이름을 입력하시오', self.convert_win)
            save_file_name_label.move(70, 100)
            save_file_name_label.resize(250, 20)
            
            self.save_file_name_input = QLineEdit(self.convert_win)
            self.save_file_name_input.setText('i_am_file.mid')
            self.save_file_name_input.move(70, 140)
            self.save_file_name_input.resize(250, 20)

            modify_button = QPushButton('저장', self.convert_win)
            modify_button.move(140, 180)
            modify_button.clicked.connect(self.convert_save)

        # 이미 열려있는 창이면 활성화하고, 아니면 보여주기 챗gpt 도움
        if not self.convert_win.isVisible():
            self.convert_win.show()
        else:
            self.convert_win.activateWindow()

    def music_play(self):
        # 챗gpt 도움
        try:
            try:
                sd.stop()
                self.play_thread.join()
                self.timer.stop()
                self.graphics_scene.removeItem(self.music_line)
            except:
                pass
            
            self.Pressed_scroll = False
            notes = self.raw_midi_data.instruments[0].notes
            
            # 소리를 저장할 배열 초기화
            total_time = int(max(note.end for note in notes) * 1.1)
            signal = np.zeros((total_time * 44100,))
    
            # 각 노트를 소리로 변환하여 배열에 추가
            for note in notes:
                start_idx = int(note.start * 44100)
                end_idx = int(note.end * 44100)
                freq = pretty_midi.note_number_to_hz(note.pitch)
                duration = end_idx - start_idx
                
                #print(note.velocity, type(note.velocity))
                
                t = np.linspace(0, duration / 44100, duration)
                
                # sin 함수를 사용하여 노트를 소리로 변환
                #note_signal = 0.5 * np.sin(2 * np.pi * freq * t)
                note_signal = (note.velocity * 0.01) * np.sin(2 * np.pi * freq * t)
                
                # 사인파를 그대로 두면 음이 끝날때 진폭이 남아있기 때문에 틱 소리가 난다
                # 이를 막기 위해서 시간이 갈 수록 사인파의 진폭을 줄인다
                # 노트 끝에서 전체 레벨을 서서히 감소시키기
                fade_out = np.linspace(1, 0, len(note_signal))  # 노트 시간 동안 서서히 감소
                note_signal *= fade_out
                
                signal[start_idx:end_idx] += note_signal
                
            signal *= 0.5   
    
            # 소리 재생
            self.play_thread = threading.Thread(target=self.play_sound, args=(signal,), daemon=True)
            self.play_thread.start()
            
            self.music_line = QGraphicsLineItem(0, 0, 0, self.canvas_height)
            self.graphics_scene.addItem(self.music_line) 
            
            # 타이머 설정
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_line_position)
            self.timer.start(10)
            
        except:
            QMessageBox.warning(None, '경고', '먼저 mid file을 load하십시오.', QMessageBox.Ok)
        
    def update_line_position(self):
        # 챗gpt 도움
        # 시간에 따라 수직선의 위치 업데이트
        # 스크롤 이동은 영향 안 받지만 창 크기 조절을 계속 하면 이동 속도 느려짐
        
        try:
             self.music_line.setLine(self.music_line.line().x1() + 1, self.music_line.line().y1(),
                      self.music_line.line().x2() + 1, self.music_line.line().y2())
            
             self.horizontal_scrollbar = self.graphics_view.horizontalScrollBar()
             
             if self.music_line.line().x1() >=  (self.width()/2):
                 if self.Pressed_scroll == False:
                     self.horizontal_scrollbar.setValue( self.horizontal_scrollbar.value() + 1 )
             if self.music_line.line().x1() > self.canvas_width:
                 self.timer.stop()
        except:
            pass
        
    def play_sound(self, signal):
        try:
            sd.play(signal, samplerate=44100)
            sd.wait()  # 재생이 끝날 때까지 대기
            self.timer.stop()
        except:
            pass

    def music_stop(self):
        try:
            sd.stop()
            self.play_thread.join()
            self.timer.stop()
            self.graphics_scene.removeItem(self.music_line)
        except:
            QMessageBox.warning(None, '경고', '먼저 mid file을 load하십시오.', QMessageBox.Ok)

    def create_piano(self):
        # 챗gpt 도움
        if self.piano_window is None or not self.piano_window.isVisible():
            # 새 창이 없거나 닫혀 있을 때 새로운 창 생성
            self.piano_window = VerticalPiano()
            self.piano_window.show()
        else:
            # 이미 열려진 창이 있을 경우 맨 앞으로 가져오기
            self.piano_window.activateWindow()
            self.piano_window.raise_()
            
    def mousePressEvent(self, event):
        pos_in_scene = self.graphics_view.mapToScene(event.pos())
        items = self.graphics_scene.items(pos_in_scene, Qt.IntersectsItemBoundingRect)
        
        for i, item in enumerate(items):
            if not isinstance(item, QGraphicsRectItem):
                items.remove(items[i])
        
        if items:
            if len(items)>=2:
                top_item = items[0]
                rect = top_item.rect()
                if not rect.width()==self.raw_midi_data.get_piano_roll().shape[1]:
                    try:
                        self.start_text_input.setText(f'{int(rect.x())}')
                        self.end_text_input.setText(f'{int(rect.x()+rect.width())}')
                        self.note_text_input.setText(f'{abs( (int(pos_in_scene.y())) // self.note_height - self.start_end[1])}')
                    except:
                        pass
    def get_mouse_position(self, event):
        try:
            # 챗gpt 도움 Get the mouse position in scene coordinates
            pos_in_scene = self.graphics_view.mapToScene(event.pos())
            x_in_scene = int(pos_in_scene.x() / self.note_width)
            y_in_scene = int(pos_in_scene.y())
            
            if x_in_scene <= 0:
                x_in_scene=0
            if y_in_scene <= 0:
                y_in_scene=0    
            
            note_number = abs( (y_in_scene) // self.note_height - self.start_end[1])
            note_text = self.note_number_to_pitch(note_number)
            
            self.position_label.setText(f"note : {note_text} ({note_number}), time : {x_in_scene}ms")     
        except:
            pass
    def note_number_to_pitch(self, note_number):
        # MIDI 노트 번호를 음표 표기법으로 변환 챗gpt 도움
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        pitch_class = note_number % 12
        octave = note_number // 12 - 1
        return f"{note_names[pitch_class]}{octave}"
    
    def visualize_midi(self):
        self.irange = []
        self.start_end = []
        self.note_rect = []
        
        for i in range(self.raw_midi_data.get_piano_roll().shape[0]):
            is_second_row_all_zero = np.all(self.raw_midi_data.get_piano_roll()[i, :] == 0)
            if is_second_row_all_zero:
                self.irange.append('0')
            else:
                self.irange.append('1')

        for i in range(0, self.raw_midi_data.get_piano_roll().shape[0], 1):
            if self.irange[i] == '1':
                note_number_start = i
                self.start_end.append(note_number_start)
                break

        for i in range(self.raw_midi_data.get_piano_roll().shape[0] - 1, -1, -1):
            if self.irange[i] == '1':
                note_number_end = i
                self.start_end.append(note_number_end)
                break
            
        self.note_height = 20 # 세로 크기 조절
        self.note_width = 1 # 가로 크기 조절
        self.note_text_width = 50 # note text부분의 가로크기 조절
            
        self.canvas_height = (self.start_end[1] - self.start_end[0] + 1) * self.note_height
        self.canvas_width = self.raw_midi_data.get_piano_roll().shape[1]
        
        self.graphics_scene.clear()
        self.graphics_scene2.clear()
        self.graphics_scene.setSceneRect(0, 0, self.canvas_width * self.note_width, self.canvas_height)
        self.graphics_scene2.setSceneRect(0, 0, self.note_text_width, self.canvas_height)
        
        # 홀수 짝수에 다른 배경색 지정
        for i in range(self.start_end[1], self.start_end[0] - 1, -1):
            rect_width = self.canvas_width * self.note_width
            
            height_start_pos = (i - self.start_end[0]) * self.note_height
            rect_height = (1) * self.note_height
            
            rect_item = QGraphicsRectItem(0, height_start_pos, rect_width, rect_height)
            rect_item2 = QGraphicsRectItem(0, height_start_pos, self.note_text_width, rect_height)
            
            if i % 2 == 1 :
                brush = QBrush(QColor(210, 210, 210)) 
                pen = QPen(QColor(210, 210, 210))
            else:
                brush = QBrush(QColor(230, 230, 230))
                pen = QPen(QColor(230, 230, 230))
                
            rect_item.setBrush(brush)
            rect_item.setPen(pen)
            
            rect_item2.setBrush(brush)
            rect_item2.setPen(pen)
            
            self.graphics_scene.addItem(rect_item)
            self.graphics_scene2.addItem(rect_item2)
        
        # 노트 넘버 시각화    
        for note in self.raw_midi_data.instruments[0].notes:
            h = abs(note.pitch - self.start_end[1])
            
            # note.start, note.end는 초 단위이므로 밀리세크로 변환해주기 위해 100을 곱한다
            width_start_pos = int(note.start*100) * self.note_width
            rect_width = ( int(note.end*100) - int(note.start*100) ) * self.note_width
            
            height_start_pos = h * self.note_height
            rect_height = (1) * self.note_height
            
            
            rect_item = QGraphicsRectItem(width_start_pos, height_start_pos, rect_width, rect_height)
            brush = QBrush(QColor(255, 255, 0)) 
            pen = QPen(QColor(150, 150, 0))
            rect_item.setBrush(brush)
            rect_item.setPen(pen)
            
            self.note_rect.append(rect_item)
            self.graphics_scene.addItem(rect_item)
        
        # 노트 넘버 텍스트 추가
        for i in range(self.start_end[1], self.start_end[0] - 1, -1):
            h = abs(i - self.start_end[1])
            note_number = i
            note_text = self.note_number_to_pitch(note_number)
            text_item = QGraphicsTextItem(note_text)
            text_item.setDefaultTextColor(Qt.black)
            text_item.setPos(0, h * self.note_height)
            self.graphics_scene2.addItem(text_item)
        
        # 1초 간격으로 세로선 그리기
        for sec in range(0, int(self.raw_midi_data.get_piano_roll().shape[1] / 100) + 1 ):
            x_position = sec * 100
            
            line = QGraphicsLineItem(x_position, 0, x_position, self.canvas_height)
            self.graphics_scene.addItem(line)  
            
        self.graphics_view.mouseMoveEvent = self.get_mouse_position
        self.graphics_view.setMouseTracking(True)
            
    def sliderPressed(self):
        self.Pressed_scroll = True
        
    def create_ui(self):
        # PyQt 윈도우 생성
        self.setWindowTitle("MID/MIDI 파일 편집기")
        self.setGeometry(100, 100, 800, 600)
        
        # 탭 위젯 생성
        tab_widget = QTabWidget(self)
        
        # 탭 추가
        tab1 = QWidget()
        
        tab_widget.addTab(tab1, "midi 파일 편집")
        
        self.setCentralWidget(tab_widget)

        # 레이아웃
        main_layout = QVBoxLayout(tab1)
        
        top_layout = QHBoxLayout()
        top_layout2 = QHBoxLayout()
        print_layout = QHBoxLayout()
        
        ############################# midi 파일 편집 탭

        # MIDI 파일 로드 및 시각화 버튼
        load_visualize_button = QPushButton("Load and Visualize MIDI", self)
        load_visualize_button.clicked.connect(self.load_and_visualize)
        top_layout.addWidget(load_visualize_button)
        load_visualize_button.setFixedSize(200, 30)

        # modify 버튼
        modify_button = QPushButton("Modify", self) 
        modify_button.clicked.connect(self.modify_window)
        top_layout.addWidget(modify_button)
        modify_button.setFixedSize(200, 30)

        # convert 버튼
        convert_button = QPushButton("Convert", self)
        convert_button.clicked.connect(self.convert_window)
        top_layout.addWidget(convert_button)
        convert_button.setFixedSize(200, 30)
        
        # piano 버튼
        piano_button = QPushButton("Piano", self)
        piano_button.clicked.connect(self.create_piano)
        top_layout.addWidget(piano_button)
        piano_button.setFixedSize(200, 30)

        # play 버튼
        play_button = QPushButton("Play", self)
        play_button.clicked.connect(self.music_play)
        top_layout2.addWidget(play_button)
        play_button.setFixedSize(200, 30)

        # stop 버튼
        stop_button = QPushButton("Stop", self)
        stop_button.clicked.connect(self.music_stop)
        top_layout2.addWidget(stop_button)
        stop_button.setFixedSize(200, 30)

        # 노트와 시간을 알려주는 부분
        self.position_label = QLabel("Note: 0 (0) Time: 0s", self)
        top_layout2.addWidget(self.position_label)
        self.position_label.setFixedSize(300, 30)
        self.position_label.setAlignment(Qt.AlignCenter)

        # graphics_view 추가
        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)
        
        # graphics_view 추가
        self.graphics_view2 = QGraphicsView(self)
        self.graphics_scene2 = QGraphicsScene(self)
        self.graphics_view2.setScene(self.graphics_scene2)
        self.graphics_view2.setFixedWidth(50)
        
        # Add a rectangle to the scene
        rect_item = QGraphicsRectItem(0, 0, 100, 100)
        # Set the fill color (inner color)
        brush = QBrush(QColor(255, 0, 0))  # Red color
        rect_item.setBrush(brush)
        
        # Set the border color
        pen = QPen(QColor(255, 0, 0))  # Green color
        rect_item.setPen(pen)
        
        self.graphics_scene.addItem(rect_item)
        
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        self.graphics_view2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # 수직 스크롤 바를 연결하여 스크롤을 동기화
        self.graphics_view.verticalScrollBar().valueChanged.connect(self.graphics_view2.verticalScrollBar().setValue)
        self.graphics_view2.verticalScrollBar().valueChanged.connect(self.graphics_view.verticalScrollBar().setValue)
        
        self.graphics_view.horizontalScrollBar().sliderPressed.connect(self.sliderPressed)
        
        print_layout.addWidget(self.graphics_view2)
        print_layout.addWidget(self.graphics_view)
        
        # main_layout 추가
        main_layout.addLayout(top_layout)
        main_layout.addLayout(top_layout2)
        main_layout.addLayout(print_layout)
        
        self.graphics_view.mouseMoveEvent = self.get_mouse_position
        self.graphics_view.mousePressEvent = self.mousePressEvent
        self.graphics_view.setMouseTracking(True)
        
        # Tkinter 이벤트 루프 시작
        self.show()

    def closeEvent(self, event):
        if self.piano_window is not None:
            self.piano_window.close()
        try:
            sd.stop()
            self.play_thread.join()   
        except:
            pass
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MidiVisualizer()
    sys.exit(app.exec_())