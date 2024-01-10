import io
import sys
from functools import partial

from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QPoint, Qt, QEvent, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow, QMessageBox

template = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>724</width>
    <height>420</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QPushButton" name="PB_start_game">
    <property name="geometry">
     <rect>
      <x>370</x>
      <y>0</y>
      <width>51</width>
      <height>31</height>
     </rect>
    </property>
    <property name="text">
     <string>старт</string>
    </property>
   </widget>
   <widget class="QSpinBox" name="SB_size_x">
    <property name="geometry">
     <rect>
      <x>0</x>
      <y>0</y>
      <width>151</width>
      <height>31</height>
     </rect>
    </property>
    <property name="value">
     <number>10</number>
    </property>
   </widget>
   <widget class="QSpinBox" name="SB_size_y">
    <property name="geometry">
     <rect>
      <x>200</x>
      <y>0</y>
      <width>141</width>
      <height>31</height>
     </rect>
    </property>
    <property name="value">
     <number>10</number>
    </property>
   </widget>
   <widget class="QPushButton" name="PB_back">
    <property name="geometry">
     <rect>
      <x>530</x>
      <y>0</y>
      <width>81</width>
      <height>31</height>
     </rect>
    </property>
    <property name="text">
     <string>Отмена</string>
    </property>
   </widget>
   <widget class="QLabel" name="size_label">
    <property name="geometry">
     <rect>
      <x>0</x>
      <y>30</y>
      <width>131</width>
      <height>16</height>
     </rect>
    </property>
    <property name="text">
     <string>Размер стороны</string>
    </property>
   </widget>
   <widget class="QLabel" name="label">
    <property name="geometry">
     <rect>
      <x>200</x>
      <y>30</y>
      <width>131</width>
      <height>16</height>
     </rect>
    </property>
    <property name="text">
     <string>Кол-во бомб</string>
    </property>
   </widget>
   <widget class="QLabel" name="win_label">
    <property name="geometry">
     <rect>
      <x>430</x>
      <y>200</y>
      <width>321</width>
      <height>51</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <family>NSimSun</family>
      <pointsize>16</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Ты победил!</string>
    </property>
   </widget>
   <widget class="QLabel" name="try_label">
    <property name="geometry">
     <rect>
      <x>430</x>
      <y>10</y>
      <width>41</width>
      <height>16</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <family>Perpetua</family>
      <pointsize>10</pointsize>
      <weight>75</weight>
      <bold>true</bold>
     </font>
    </property>
    <property name="text">
     <string>Жизни: </string>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>724</width>
     <height>18</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>


'''


class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)
        # self.setupUi(self)

    def change_image(self, tempB):
        if tempB.value:
            tempB.value = 0
            tempB.setIcon(self.icon)
        else:
            tempB.value = 1
            tempB.setIcon(self.flag)
        self.repaint()
        # Получаем текущую картинку кнопки в виде QPixmap

    def setFunc(self):  # создаем все нужное для подготовки
        self.l = QLabel()
        self.l.setGeometry(50, 50, 10, 10)
        self.l.setText("123123132")
        self.try_label.setVisible(False)
        self.win_label.setVisible(False)
        self.PB_back.setVisible(False)
        self.PB_start_game.clicked.connect(self.startGame)
        self.PB_back.clicked.connect(self.back_event)
        self.setWindowTitle('Сапёр')
        self.show()

    redempt = None

    def back_event(self):
        # кнопка спасения (появляется при открытии поля с бомбой)
        if self.redempt:
            self.redempt.setVisible(True)
        self.PB_back.setVisible(False)
        self.NotGAMEStop = True

        for x in self.GAMEFIELDB:
            for y in x:
                y.setEnabled(True)

    SIZE = QPoint(0, 0)
    GAMEFIELDB = []
    GAMEFIELDLabel = []
    SIZEPB = 50
    empties = 0
    countBomb = 0
    attempts = 4

    def getColor(self, i, j):  # присваиваем цвет каждому лейблу в зависимости от кол-ва бомб вокруг этого лейбла
        colors = {
            -1: "FF0000",
            0: "FFFFFF",
            1: "FF00FF",
            2: "FFFF00",
            3: "00FF00",
            4: "00FFFF",
            5: "008080",
            6: "000080",
            7: "800000",
            8: "000000",
        }
        return colors[self.tabel[i][j]]

    def startGame(self):
        self.back_event()

        tempX = self.size().width()
        tempY = self.size().height() - 50 - 70
        # отступ для спинбоксов и кнопки старта
        minTemp = min(tempX, tempY)
        print(minTemp)
        self.SIZEPB = int(minTemp / int(self.SB_size_x.value()))
        pixmap = QPixmap('but.png')
        self.pixmap = pixmap.scaled(QSize(self.SIZEPB, self.SIZEPB), Qt.KeepAspectRatio)
        self.icon = QIcon(pixmap.scaled(QSize(self.SIZEPB, self.SIZEPB), Qt.KeepAspectRatio))

        pixmap2 = QPixmap('a.png')
        self.pixmap2 = pixmap2.scaled(QSize(self.SIZEPB, self.SIZEPB), Qt.KeepAspectRatio)
        self.flag = QIcon(pixmap2.scaled(QSize(self.SIZEPB, self.SIZEPB), Qt.KeepAspectRatio))
        self.SIZE = QPoint(0, 0)
        for x in self.GAMEFIELDB:
            for y in x:
                try:
                    # y.deleteLater()
                    y.setVisible(False)
                except:
                    pass
                del (y)
        for x in self.GAMEFIELDLabel:
            for y in x:
                # y.deleteLater()
                y.setVisible(False)
                del (y)

        self.GAMEFIELDB = []
        self.GAMEFIELDLabel = []

        self.SIZE = QPoint(int(self.SB_size_x.value()), int(self.SB_size_x.value()))
        self.countBomb = self.SB_size_y.value()
        self.tabel = self.defuse(self.SIZE.x(), int(self.countBomb))
        for i in range(self.SIZE.x()):
            tempFIELDB = []
            tempFIELDL = []
            for j in range(self.SIZE.y()):
                # создаем лейблы и потом их покрываем кнопками
                tempL = QLabel(self.centralwidget)
                tempL.setAlignment(Qt.AlignCenter)
                if self.tabel[i][j] != 0:
                    tempL.setText(str(self.tabel[i][j]))
                    if self.tabel[i][j] == -1:
                        tempL.setPixmap(QPixmap("b.png"))
                        tempL.setScaledContents(True)
                tempL.setGeometry(QtCore.QRect(self.SIZEPB * i, 80 + self.SIZEPB * j, self.SIZEPB, self.SIZEPB))
                tempL.setStyleSheet("background-color: #" + f"{self.getColor(i, j)}" + "; border: 1px solid black;")
                # tempL.show()
                tempFIELDL.append(tempL)
                tempB = QtWidgets.QPushButton(self.centralwidget)
                tempB.setGeometry(QtCore.QRect(self.SIZEPB * i, 80 + self.SIZEPB * j, self.SIZEPB, self.SIZEPB))
                tempB.clicked.connect(partial(self.coordinate, i, j))
                tempB.setStyleSheet('background-color: #808080; ')
                tempB.installEventFilter(self)

                tempB.setIconSize(QSize(self.SIZEPB, self.SIZEPB))
                tempB.value = 0
                tempB.setIcon(self.icon)
                # tempB.setIcon(self.flag)

                tempFIELDB.append(tempB)
            self.GAMEFIELDB.append(tempFIELDB)
            self.GAMEFIELDLabel.append(tempFIELDL)
        for i in range(self.SIZE.x()):
            for j in range(self.SIZE.y()):
                self.GAMEFIELDLabel[i][j].show()
                self.GAMEFIELDB[i][j].show()
                pass

    def coordinate(self, i, j):
        print(f"Button clicked at position ({i}, {j})")
        # self.GAMEFIELDB[i][j].deleteLater()

    def find_neighbors_no_diagonal(self, matrix, i, j, visited=None):
        # функция возвращает массив с координатами клеток, у которых по соседству нет бомб
        if visited is None:
            visited = set()

        rows = len(matrix)
        cols = len(matrix[0])

        neighbors = []

        # Проверяем чтобы координаты были в пределах матрицы
        if 0 <= i < rows and 0 <= j < cols and (i, j) not in visited:
            visited.add((i, j))

            # Если текущая ячейка содержит 0, добавляем ее в результат
            if matrix[i][j] == 0:
                neighbors.append((i, j))

                # Перебираем только горизонтальных и вертикальных соседей
                for x, y in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
                    neighbors.extend(self.find_neighbors_no_diagonal(matrix, x, y, visited))

        return neighbors

    NotGAMEStop = True

    # def error(self):
    #     error = QMessageBox()
    #     error.setWindowTitle('Вы проиграли')
    #     error.setText('Вы использовали все жизни, ')
    #     error.setIcon(QMessageBox.Warning)
    #     error.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    #     error.exec_()
    def show_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle('Вы проиграли')
        msg.setText('Вы использовали все жизни!')
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()

    def eventFilter(self, obj, event):
        global attempts
        I = 0
        J = 0
        for i in range(self.SIZE.x()):
            for j in range(self.SIZE.y()):
                if obj == self.GAMEFIELDB[i][j]:
                    I = i
                    J = j

        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if self.NotGAMEStop:
                obj.setVisible(False)
            counter = 0
            for x in self.GAMEFIELDB:
                for y in x:
                    if y.isVisible():
                        counter += 1

            # if counter == 1:
            #     if self.tabel[I][J] != 0:
            #         self.tabel = self.defuse(self.SIZE.x(), int(self.countBomb))

            if counter == int(self.SIZE.x()) * int(self.SIZE.x()) - 1:
                if self.tabel[I][J] != 0:
                    self.startGame()
                    self.eventFilter(obj, event)
                    # return

            if counter == self.countBomb:
                self.win_label.setVisible(True)
                print("Победа")
                for x in self.GAMEFIELDB:
                    for y in x:
                        y.setVisible(False)
                # end = QMessageBox()
                # end.setWindowTitle('Конец игры')
                # end.setIcon(QMessageBox.Close)
                # end.setText('Поздравляем, Вы разминировали поле!')
                # end.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

                # end.exec()

            if self.tabel[I][J] == -1 and self.NotGAMEStop:
                attempts -= 1
                self.try_label.setText('Жизни: ' + str(attempts))
                if not self.try_label.setVisible():
                    self.try_label.setVisible(True)
                if attempts == 0:
                    self.show_popup()
                    # error = QMessageBox()
                    # error.setWindowTitle('Вы проиграли')
                    # error.setText('Вы использовали все жизни, ')
                    # error.setIcon(QMessageBox.Warning)
                    # error.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    # error.exec_()
                    # self.error()

                print(f"Ура умер! ({I}, {J})")
                self.NotGAMEStop = False
                self.PB_back.setVisible(True)
                self.redempt = obj
                for x in self.GAMEFIELDB:
                    for y in x:
                        y.setEnabled(False)
            # only trying
            # else:
            # empties += 1
            # pass
            if self.NotGAMEStop:
                a = self.find_neighbors_no_diagonal(self.tabel, I, J)
                for x in a:
                    # self.GAMEFIELDB[x[0]][x[1]].deleteLater()
                    self.GAMEFIELDB[x[0]][x[1]].setVisible(False)

        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            # obj.setStyleSheet("background-color: #000000; border: 1px solid black;")
            self.change_image(obj)

            print(f"Flag clicked at position ({I}, {J})")
            # return True  #
        return super().eventFilter(obj, event)

    def defuse(self, x, countBomb):
        # countBomb=int(self.SB_size_y)
        y = x
        table = []
        for i in range(x):
            table.append([0] * y)

        count = 0
        while True:
            import random as r
            i = r.randint(0, y - 1)
            j = r.randint(0, y - 1)
            if table[i][j] == -1:
                continue
            else:
                table[i][j] = -1
                count += 1
            if count == countBomb:
                break

        for i in range(len(table)):
            for j in range(len(table[i])):
                bombTemp = 0
                if table[i][j] == -1:
                    continue
                ai = -1 if i != 0 else 0
                aj = -1 if j != 0 else 0
                bi = 1 if i != len(table) - 1 else 0
                bj = 1 if j != len(table) - 1 else 0
                for ii in range(ai, bi + 1, 1):
                    for jj in range(aj, bj + 1, 1):
                        if ii == 0 and jj == 0:
                            continue
                        if table[i + ii][j + jj] == -1:
                            bombTemp += 1
                table[i][j] = bombTemp

        return table


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Interface()
    # ex.initUI()
    ex.setFunc()
    ex.show()
    sys.exit(app.exec_())
