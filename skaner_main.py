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
    QProgressBar, \
    QGroupBox

import json

import const

matplotlib.use('Qt5Agg')

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

    def setPlotGrid(self, gridType, gridAxis):
        self.axes.grid(False)
        self.axes.grid(gridType, which='both', axis=gridAxis)

    def setAutoscale(self, state, ax):
        self.axes.autoscale(state, ax)


'''
    Klasa głównego okna aplikacji.
'''


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        # Inicjlizacja zmiennych
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Skaner")
        self.__index = 0
        self.__samples = const.defSamples
        self.__samplingPeriod = const.defSamplingPeriod
        self.__initValue = const.definitValue
        self.__endValue = const.defendValue
        self.maxval = 0.0
        self.minval = 0.0

# Definicje etkiet w programie
        # Etykiety, umieszczone obok pół wpisywania danych
        samplesNumberLabel = QLabel("Ilość punktów:", self)
        samplingIntervalLabel = QLabel("Okres próbkowania [ms]:", self)
        initValueLabel = QLabel("Wartość początkowa:", self)
        endValueLabel = QLabel("Wartość końcowa:", self)
        xGenScaleLabel = QLabel("Generowanie X:")

        # Etykiety wyświetlania współrzędnych ostatniego punktu
        self.currentXlabel = QLabel("x = 0", self)
        self.currentYlabel = QLabel('y = 0', self)

# Definicje pól wprowadzania tekstu w programie
        self.samplesNumberEdit = QLineEdit()
        self.samplingIntervalEdit = QLineEdit()
        self.initValueEdit = QLineEdit()
        self.endValueEdit = QLineEdit()
        self.samplesNumberEdit.setText(str(const.defSamples))
        self.samplingIntervalEdit.setText(str(const.defSamplingPeriod))
        self.initValueEdit.setText(str(const.definitValue))
        self.endValueEdit.setText(str(const.defendValue))

# Definicje przycisków w programie
        self.startBtn = QPushButton("&Start", self)
        self.startBtn.setStyleSheet("background-color:lightgreen")
        self.startBtn.clicked.connect(self.start_plot)
        self.stopBtn = QPushButton("Stop", self)
        self.stopBtn.setStyleSheet("background-color:red")
        self.stopBtn.clicked.connect(self.stop_plot)

        # Przyciski do operacji na plikach
        self.saveConfBtn = QPushButton("Zapisz", self)
        self.openConfBtn = QPushButton("Wczytaj", self)
        self.saveConfBtn.clicked.connect(self.saveConfigFile)
        self.openConfBtn.clicked.connect(self.openConfigFile)

# Combo Boxy
        self.plotXscale = QComboBox(self)
        self.plotXscale.addItem('X: Liniowa')
        self.plotXscale.addItem('X: Logarytmiczna')

        self.plotYscale = QComboBox(self)
        self.plotYscale.addItem('Y: Liniowa')
        self.plotYscale.addItem('Y: Logarytmiczna')

        self.plotGrid = QComboBox(self)
        self.plotGrid.addItem('Brak')
        self.plotGrid.addItem('Tylko X')
        self.plotGrid.addItem('Tylko Y')
        self.plotGrid.addItem('X i Y')
        self.plotGrid.currentIndexChanged.connect(self.changePlotGrid)

        self.sampXGenCombo = QComboBox(self)
        self.sampXGenCombo.addItem('Liniowo')
        self.sampXGenCombo.addItem('Logarytmicznie')

# Progres bar
        self.progressBar = QProgressBar(self)

# Boxy na widgety
        self.dataParametersGroup = QGroupBox("Nastawy")
        grdLay = QGridLayout()
        grdLay.addWidget(samplesNumberLabel,
                         const.sampNumLabRow, const.sampNumLabCol)
        grdLay.addWidget(samplingIntervalLabel,
                         const.sampIntLabRow, const.sampIntLabCol)
        grdLay.addWidget(initValueLabel, const.iniValLabRow,
                         const.iniValLabCol)
        grdLay.addWidget(endValueLabel, const.endValLabRow, const.endValLabCol)
        grdLay.addWidget(xGenScaleLabel, const.xGenScaleLabelRow,
                         const.xGenScaleLabelCol)
        grdLay.addWidget(self.samplesNumberEdit,
                         const.sampNumEditRow, const.sampNumEditCol)
        grdLay.addWidget(self.samplingIntervalEdit,
                         const.sampIntEditRow, const.sampIntEditCol)
        grdLay.addWidget(self.initValueEdit,
                         const.iniValEditRow, const.iniValEditCol)
        grdLay.addWidget(self.endValueEdit,
                         const.endValEditRow, const.endValEditCol)
        grdLay.addWidget(self.sampXGenCombo,
                         const.sampXScaleRow, const.sampXScaleCol)
        self.dataParametersGroup.setLayout(grdLay)

        self.currentDataGroup = QGroupBox("Wartości")
        grdLay = QGridLayout()
        grdLay.addWidget(self.currentXlabel, const.currXLabRow,
                         const.currXLabCol, const.currXLabRowDim, const.currXLabColDim)
        grdLay.addWidget(self.currentYlabel, const.currYLabRow,
                         const.currYLabCol, const.currYLabRowDim, const.currYLabColDim)
        grdLay.addWidget(self.progressBar, const.prgBarRow, const.prgBarCol)
        self.currentDataGroup.setLayout(grdLay)

        self.plotSettingsGroup = QGroupBox("Ustawienia wykresu")
        grdLay = QGridLayout()
        grdLay.addWidget(QLabel("Skala"), 0, 0)
        grdLay.addWidget(self.plotXscale, const.pltXsclRow, const.pltXsclCol)
        grdLay.addWidget(self.plotYscale, const.pltYsclRow, const.pltYsclCol)
        grdLay.addWidget(QLabel("Siatka"), 3, 0)
        grdLay.addWidget(self.plotGrid, const.pltGridRow, const.pltGridCol)
        self.plotSettingsGroup.setLayout(grdLay)

        self.ctrlButtonsGroup = QGroupBox("Kontrola")
        grdLay = QGridLayout()
        grdLay.addWidget(self.startBtn, const.startBtnRow, const.startBtnCol)
        grdLay.addWidget(self.stopBtn, const.stopBtnRow, const.stopBtnCol)
        grdLay.addWidget(QLabel("Plik ustawień"), 2, 0)
        grdLay.addWidget(self.saveConfBtn,
                         const.saveConfBtnRow, const.saveConfBtnCol)
        grdLay.addWidget(self.openConfBtn,
                         const.openConfBtnRow, const.openConfBtnCol)
        self.ctrlButtonsGroup.setLayout(grdLay)

        self.confFileGroup = QGroupBox("Plik ustawień")
        grdLay = QGridLayout()

        self.confFileGroup.setLayout(grdLay)

# Layout Tabelaryczny
        Tlayout = QGridLayout()

        Tlayout.addWidget(self.dataParametersGroup, 0, 1)
        Tlayout.addWidget(self.currentDataGroup, 0, 3)
        Tlayout.addWidget(self.plotSettingsGroup, 0, 2)
        Tlayout.addWidget(self.ctrlButtonsGroup, 0, 0)

        # Okno wykresu
        self.canvas = MplCanvas(self, width=const.canvWid,
                                height=const.canvHght, dpi=const.canvDpi)
        Tlayout.addWidget(self.canvas, const.canvRow,
                          const.canvCol, const.canvRowDim, const.canvColDim)
        self.setLayout(Tlayout)

        self.xdata = []
        self.ydata = []
        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_ref = None
        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = PyQt5.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

        self.showMaximized()

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
            self.__endValue = float(self.endValueEdit.text())
            self.__step = (self.__endValue - self.__initValue) / self.__samples
            self.__samples = self.__samples + 1

            dataok = True
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane.", QMessageBox.Ok)
            dataok = False
        if dataok:
            if self.__samplingPeriod > 0:
                if self.__samples > 0 and self.__step != 0.0:
                    if self.sampXGenCombo.currentIndex() == 0:
                        self.xdata = list(self.__initValue + i *
                                          self.__step for i in range(self.__samples))
                    elif self.sampXGenCombo.currentIndex() == 1:
                        x1 = math.log10(self.__initValue)
                        x2 = math.log10(self.__endValue)
                        i = []
                        for j in range(self.__samples):
                            i.append(x1 + j * ((x2 - x1)/(self.__samples - 1)))

                        self.xdata = list(
                            math.pow(10.0, j) for j in i)

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
                self.endValueEdit.setReadOnly(True)
                self.progressBar.setMaximum(self.__samples)
                self.progressBar.setValue(0)
                self.plotXscale.setEnabled(False)
                self.plotYscale.setEnabled(False)
                self.startBtn.setEnabled(False)
                self.openConfBtn.setEnabled(False)
                self.sampXGenCombo.setEnabled(False)
                self.clear_plot()
                self.changePlotGrid()
                if self.plotXscale.currentIndex() == 0:
                    self.canvas.setXscale('linear')
                elif self.plotXscale.currentIndex() == 1:
                    self.canvas.setXscale('log')
                if self.plotYscale.currentIndex() == 0:
                    self.canvas.setYscale('linear')
                elif self.plotYscale.currentIndex() == 1:
                    self.canvas.setYscale('log')
                self.canvas.setAutoscale(True, 'both')
                # Tablica na wartości Y
                self.ydata = [0.0 for i in range(self.__samples)]
                self.timer.setInterval(self.__samplingPeriod)

                try:
                    self.update_plot()
                except:
                    QMessageBox.warning(
                        self, "Błąd", "Nieoczekiwany błąd.", QMessageBox.Ok)
                    self.stop_plot()

                try:
                    self.timer.start()
                except:
                    QMessageBox.warning(
                        self, "Błąd", "Wprowadź poprawny okres próbkowania", QMessageBox.Ok)
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
        self.openConfBtn.setEnabled(True)
        self.samplingIntervalEdit.setReadOnly(False)
        self.samplesNumberEdit.setReadOnly(False)
        self.initValueEdit.setReadOnly(False)
        self.endValueEdit.setReadOnly(False)
        self.sampXGenCombo.setEnabled(True)

    def clear_plot(self):
        self.__index = 0
        self.minval = 0.0
        self.maxval = 0.0
        self.canvas.clearPlot()
        self._plot_ref = None

    def changePlotGrid(self):
        gridOn = False
        gridAx = 'both'
        if self.plotGrid.currentIndex() == 1:
            gridOn = True
            gridAx = 'x'
        elif self.plotGrid.currentIndex() == 2:
            gridOn = True
            gridAx = 'y'
        elif self.plotGrid.currentIndex() == 3:
            gridOn = True
            gridAx = 'both'

        self.canvas.setPlotGrid(gridOn, gridAx)
        self.canvas.draw()
        self.canvas.setAutoscale(True, 'both')

    def saveConfigFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        dialogBox = QFileDialog()
        dialogBox.setWindowTitle("Zapisz plik konfiguracyjny")
        dialogBox.setNameFilters(
            ["Plik JSON (*.json)", "Plik tekstowy (*.txt)"])
        dialogBox.setDefaultSuffix('json')
        dialogBox.setAcceptMode(QFileDialog.AcceptSave)

        if dialogBox.exec_() == QFileDialog.Accepted:
            filename = dialogBox.selectedFiles()[0]
            config = {}
            config['sampling'] = []
            config['sampling'].append({
                'samplingPeriod': self.samplingIntervalEdit.text(),
                'firstValue': self.initValueEdit.text(),
                'lastValue': self.endValueEdit.text(),
                'sampleCount': self.samplesNumberEdit.text(),
                'xGen': self.sampXGenCombo.currentIndex()
            })
            config['plot'] = []
            config['plot'].append({
                'grids': self.plotGrid.currentIndex(),
                'xScale': self.plotXscale.currentIndex(),
                'yScale': self.plotYscale.currentIndex()
            })

            with open(filename, 'w') as outfile:
                json.dump(config, outfile, indent=4, sort_keys=True)

    def openConfigFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        dialogBox = QFileDialog()
        dialogBox.setWindowTitle("Wybierz plik konfiguracyjny")
        dialogBox.setNameFilters(
            ["Plik JSON (*.json)", "Plik tekstowy (*.txt)"])
        dialogBox.setDefaultSuffix('json')
        dialogBox.setAcceptMode(QFileDialog.AcceptOpen)

        if dialogBox.exec_() == QFileDialog.Accepted:
            filename = dialogBox.selectedFiles()[0]
            with open(filename) as jsonFile:
                data = json.load(jsonFile)
                try:
                    samplConf = data['sampling'][0]
                    self.samplingIntervalEdit.setText(
                        samplConf["samplingPeriod"])
                    self.initValueEdit.setText(samplConf["firstValue"])
                    self.endValueEdit.setText(samplConf["lastValue"])
                    self.samplesNumberEdit.setText(samplConf["sampleCount"])
                    self.sampXGenCombo.setCurrentIndex(samplConf["xGen"])
                except:
                    QMessageBox.warning(
                        self, "Błąd", "Błędne ustawienia próbkowania.", QMessageBox.Ok)

                try:
                    samplConf = data['plot'][0]
                    self.plotGrid.setCurrentIndex(samplConf['grids'])
                    self.plotXscale.setCurrentIndex(samplConf['xScale'])
                    self.plotYscale.setCurrentIndex(samplConf['yScale'])
                except Exception as e:
                    print(e)
                    QMessageBox.warning(
                        self, "Błąd", "Błędne ustawienia wykresu.", QMessageBox.Ok)

    def getData(self):
        index = self.get_index()
        if index == 0:
            '''
                Pierwszy obieg, nie ma jeszcze żadnych danych pomiarowych.
                Wyśli dane do urządzenia i nie odbieraj nic.
            '''
            pomiar = random.random()

        elif index > 0:
            '''
                Pobierz dane z urządzenia z poprzedniego pomiaru i wyślij kolejną nastawę
            '''
            pomiar = math.sin(self.xdata[index - 1]) * 10 + \
                random.random() + math.cos(self.xdata[index - 1] * 3)

        return pomiar


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    okno = MainWindow()
    sys.exit(app.exec_())
