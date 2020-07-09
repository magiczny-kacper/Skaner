import random
import math
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import PyQt5.QtCore
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import \
    QLabel, \
    QGridLayout, \
    QLineEdit, \
    QPushButton, \
    QHBoxLayout, \
    QMessageBox, \
    QApplication, \
    QWidget, \
    QComboBox, \
    QFileDialog, \
    QCheckBox, \
    QButtonGroup, \
    QProgressBar

import const

matplotlib.use('Qt5Agg')

'''
    Funkcja używana do pobrania danych dla wykresu. 
    Tutaj powinna znaleźć się komunikacja z urządzeniami.
    Funkcja wywoływana jest cyklicznie.
    Powinna zwaracać dane do pokazania na wykresie.
'''


'''
    Klasa widżetu wykresu
'''


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

    def clearPlot(self):
        self.axes = self.fig.clear()
        self.axes = self.fig.add_subplot(111)

    def setXscale(self, scale):
        self.axes.set_xscale(scale)

    def setYscale(self, scale):
        self.axes.set_yscale(scale)

    def setYlim(self, min, max):
        if min == max:
            self.axes.set_ylim(min)
        else:
            self.axes.set_ylim(min, max)


'''
    Klasa głównego okna aplikacji.
'''


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Skaner")
        self.__index = 0
        self.__samples = const.defSamples
        self.__samplingPeriod = const.defSamplingPeriod
        self.__initValue = const.definitValue
        self.__step = const.defStep
        self.maxval = 0.0
        self.minval = 0.0

        # Etykiety, umieszczone obok pół wpisywania danych
        samplesNumberLabel = QLabel("Ilość punktów na wykresie:", self)
        samplingIntervalLabel = QLabel("Okres próbkowania [ms]:", self)
        initValueLabel = QLabel("Wartość początkowa:", self)
        deltaValueLabel = QLabel("Krok:", self)

        # Etykiety wyświetlania współrzędnych ostatniego punktu
        self.currentXlabel = QLabel("x = 0", self)
        self.currentYlabel = QLabel('y = 0', self)

        # Layout Tabelaryczny
        Tlayout = QGridLayout()

        # Dodanie etykiet jako widgety do layoutu
        Tlayout.addWidget(samplesNumberLabel,
                          const.sampNumLabRow, const.sampNumLabCol)
        Tlayout.addWidget(samplingIntervalLabel,
                          const.sampIntLabRow, const.sampIntLabCol)
        Tlayout.addWidget(initValueLabel, const.iniValLabRow,
                          const.iniValLabCol)
        Tlayout.addWidget(deltaValueLabel, const.delValLabRow,
                          const.delValLabCol)
        Tlayout.addWidget(self.currentXlabel, const.currXLabRow,
                          const.currXLabCol, const.currXLabRowDim, const.currXLabColDim)
        Tlayout.addWidget(self.currentYlabel, const.currYLabRow,
                          const.currYLabCol, const.currYLabRowDim, const.currYLabColDim)

        # Pola do wpisania danych
        self.samplesNumberEdit = QLineEdit()
        self.samplingIntervalEdit = QLineEdit()
        self.initValueEdit = QLineEdit()
        self.deltaValueEdit = QLineEdit()
        Tlayout.addWidget(self.samplesNumberEdit,
                          const.sampNumEditRow, const.sampNumEditCol)
        Tlayout.addWidget(self.samplingIntervalEdit,
                          const.sampIntEditRow, const.sampIntEditCol)
        Tlayout.addWidget(self.initValueEdit,
                          const.iniValEditRow, const.iniValEditCol)
        Tlayout.addWidget(self.deltaValueEdit,
                          const.delValEditRow, const.delValEditCol)

        self.samplesNumberEdit.setText("0")
        self.samplingIntervalEdit.setText("0")
        self.initValueEdit.setText("0")
        self.deltaValueEdit.setText("0")

        # Przyciski do startu i zatrzymania działania
        self.startBtn = QPushButton("Start", self)
        self.startBtn.clicked.connect(self.start_plot)
        self.stopBtn = QPushButton("Stop", self)
        self.stopBtn.clicked.connect(self.stop_plot)
        self.clearBtn = QPushButton("Wyczyść", self)

        self.clearBtn.clicked.connect(self.clear_plot)

        Tlayout.addWidget(self.startBtn, const.startBtnRow, const.startBtnCol)
        Tlayout.addWidget(self.stopBtn, const.stopBtnRow, const.stopBtnCol)
        Tlayout.addWidget(self.clearBtn, const.clrBtnRow, const.clrBtnCol)

        self.plotXscale = QComboBox(self)
        self.plotXscale.addItem('X: Liniowa')
        self.plotXscale.addItem('X: Logarytmiczna')
        Tlayout.addWidget(self.plotXscale, const.pltXsclRow,
                          const.pltXsclCol, const.pltXsclRowDim, const.pltXsclColDim)

        self.plotYscale = QComboBox(self)
        self.plotYscale.addItem('Y: Liniowa')
        self.plotYscale.addItem('Y: Logarytmiczna')
        Tlayout.addWidget(self.plotYscale, const.pltYsclRow,
                          const.pltYsclCol, const.pltYsclRowDim, const.pltYsclColDim)

        self.progressBar = QProgressBar(self)
        Tlayout.addWidget(self.progressBar, const.prgBarRow, const.prgBarCol)

        # Okno wykresu
        self.canvas = MplCanvas(self, width=const.canvWid,
                                height=const.canvHght, dpi=const.canvDpi)
        Tlayout.addWidget(self.canvas, const.canvRow,
                          const.canvCol, const.canvRowDim, const.canvColDim)
        self.setLayout(Tlayout)
        self.show()
        self.xdata = []
        self.ydata = []
        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_ref = None
        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = PyQt5.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

    def increment_index(self):
        self.__index += 1

    def get_index(self):
        return self.__index

    def update_plot(self):
        # Drop off the first y element, append a new one.
        index = self.get_index()
        data = self.getData()
        currx = "X = 0"
        curry = "Y = 0"
        self.progressBar.setValue(index)
        if index > 0:
            self.ydata[index - 1] = data
            if data > self.maxval:
                self.maxval = data
            elif data < self.minval:
                self.minval = data
            currx = "X = " + "{:.5f}".format(self.xdata[self.get_index() - 1])
            curry = "Y = " + "{:.5f}".format(self.ydata[self.get_index() - 1])
            curridx = "idx = " + str(self.get_index())
        else:
            self.maxval = data
            self.minval = data
        self.increment_index()
        self.currentYlabel.setText(curry)
        self.currentXlabel.setText(currx)
        self.canvas.setYlim(self.minval, self.maxval)
        # Note: we no longer need to clear the axis.
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.canvas.axes.plot(self.xdata, self.ydata, 'r')
            self._plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_ydata(self.ydata)
        # Trigger the canvas to update and redraw.
        self.canvas.draw()
        if index == self.__samples:
            self.stop_plot()
            QMessageBox.information(
                self, "Info", "Zakończono.", QMessageBox.Ok)

    def start_plot(self):
        try:
            self.__samples = int(self.samplesNumberEdit.text())
            self.__samplingPeriod = int(self.samplingIntervalEdit.text())
            self.__initValue = float(self.initValueEdit.text())
            self.__step = float(self.deltaValueEdit.text())
            dataok = True
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane.", QMessageBox.Ok)
            dataok = False
        if dataok:
            if self.__samplingPeriod > 0:
                if self.__samples > 0 and self.__step != 0.0:
                    self.xdata = list(self.__initValue + i *
                                      self.__step for i in range(self.__samples))
                    dataok = True
            else:
                dataok = False

            if dataok:
                if self.__samplingPeriod < 10:
                    QMessageBox.warning(
                        self, "Uwaga!", "Uwaga, okres próbkowania niżzy niż 10 ms, może powodować niepoprawną pracę programu.")
                self.samplingIntervalEdit.setReadOnly(True)
                self.samplesNumberEdit.setReadOnly(True)
                self.initValueEdit.setReadOnly(True)
                self.deltaValueEdit.setReadOnly(True)
                self.progressBar.setMaximum(self.__samples)
                self.progressBar.setValue(0)
                self.plotXscale.setEnabled(False)
                self.plotYscale.setEnabled(False)
                self.clearBtn.setEnabled(False)
                self.startBtn.setEnabled(False)
                self.clear_plot()
                if self.plotXscale.currentIndex() == 0:
                    self.canvas.setXscale('linear')
                elif self.plotXscale.currentIndex() == 1:
                    self.canvas.setXscale('log')
                if self.plotYscale.currentIndex() == 0:
                    self.canvas.setYscale('linear')
                elif self.plotYscale.currentIndex() == 1:
                    self.canvas.setYscale('log')

                self.ydata = [0.0 for i in range(self.__samples)]
                self.timer.setInterval(self.__samplingPeriod)
                try:
                    self.update_plot()
                    self.timer.start()
                except:
                    QMessageBox.warning(self, "Błąd", "Błąd.", QMessageBox.Ok)
                    self.stop_plot()
            else:
                QMessageBox.warning(
                    self, "Błąd", "Błędne dane.", QMessageBox.Ok)

    def stop_plot(self):
        self.canvas.axes.autoscale(enable=True, axis='y')
        self.timer.stop()
        self.plotXscale.setEnabled(True)
        self.plotYscale.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.clearBtn.setEnabled(True)
        self.samplingIntervalEdit.setReadOnly(False)
        self.samplesNumberEdit.setReadOnly(False)
        self.initValueEdit.setReadOnly(False)
        self.deltaValueEdit.setReadOnly(False)

    def clear_plot(self):
        self.__index = 0
        self.minval = 0.0
        self.maxval = 0.0
        self.canvas.clearPlot()
        self._plot_ref = None

    def getData(self):
        index = self.get_index()
        if index == 0:
            x = random.random()
            '''
                Wyśli dane do urządzenia i nie odbieraj nic.
            '''
        elif index > 0:
            x = math.log(self.xdata[index - 1])
            '''
                Pobierz dane z urządzenia z poprzedniego pomiaru i wyślij kolejną nastawę
            '''
        return x


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    okno = MainWindow()
    sys.exit(app.exec_())
