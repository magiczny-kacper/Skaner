import random
import math
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib as mpl
import matplotlib.figure as mpl_fig
import matplotlib.animation as anim

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
    QGroupBox, \
    QPlainTextEdit

import json
import csv

import const

matplotlib.use('Qt5Agg')

'''
    Klasa widżetu wykresu
'''
lineCount = 5

lineColors = ['red', 'green', 'blue', 'skyblue', 'olive']


class MplCanvas(FigureCanvas, anim.FuncAnimation):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        FigureCanvas.__init__(self, mpl_fig.Figure())

        self.axes = self.figure.subplots()
        self.annMax = None
        self.annMin = None
        self.maxY = 0
        self.minY = 0
        self.plotref = []
        self.axLegends = ["a", "b", "c", "d", "e"]

    def plotData(self, xdata, ydata, lines):
        if len(self.plotref) == 0:
            for i in range(lines):
                if len(self.axLegends) >= i + 1:
                    axlabel = self.axLegends[i]
                else:
                    axlabel = None

                plot_refs = self.axes.plot(
                    xdata, ydata[0], lineColors[i], label=axlabel)

                legend = self.axes.legend(loc='upper center', bbox_to_anchor=(
                    0.5, 1.05), ncol=3, fancybox=True, shadow=True)
                self.plotref.append(plot_refs[0])
                self.plotref[i].set_ydata(ydata[i])
        else:
            for i in range(lines):
                plot_refs = self.axes.plot(
                    xdata, ydata[0], lineColors[i])
                self.plotref[i].set_ydata(ydata[i])

        self.draw()
        return

    def clearPlot(self):
        self.axes = self.figure.clear()
        self.plotref = []
        self.draw()
        self.axes = self.figure.subplots()

    def setAxisLabels(self, xlegend, ylegend):
        self.axes.set_xlabel(xlegend)
        self.axes.set_ylabel(ylegend)

    def setAxesLegend(self, legends):
        self.axLegends = []
        self.axLegends = legends

    def setXscale(self, scale):
        self.axes.set_xscale(scale)

    def setYscale(self, scale):
        self.axes.set_yscale(scale)

    def setYlim(self, min, max):
        if min != max:
            # if min == max:
            #    self.axes.set_ylim(min)
            # else:
            if min > 0:
                minn = min * 0.9
            else:
                minn = min * 1.1

            if max > 0:
                maxx = max * 1.1
            else:
                maxx = max * 0.9
            self.axes.set_ylim(minn, maxx)
            self.axes.plot()
            self.maxY = maxx
            self.minY = minn

    def setPlotGrid(self, gridType, gridAxis):
        self.axes.grid(False)
        self.axes.grid(gridType, which='both', axis=gridAxis)

    def setAutoscale(self, state, ax):
        self.axes.autoscale(state, ax)

    def saveToPNG(self, filename):
        self.figureCpy = self.figure
        self.figure.savefig(filename, dpi=100, format='png')


'''
    Klasa głównego okna aplikacji.
'''


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle(const.WindowTitle)

        self.VariablesInit()

        self.ctrlButtonsGroup = QGroupBox("Kontrola")
        self.ctrlButtonsGroup.setLayout(self.ControlBoxInit())

        self.plotSaveButtonsGroup = QGroupBox("Zapis przebiegu")
        self.plotSaveButtonsGroup.setLayout(self.PlotSaveBoxInit())

        self.dataParametersGroup = QGroupBox("Nastawy")
        self.dataParametersGroup.setLayout(self.RuntimeSettingsBoxInit())

        self.plotSettingsGroup = QGroupBox("Ustawienia wykresu")
        self.plotSettingsGroup.setLayout(self.PlotControlBoxInit())

        self.currentDataGroup = QGroupBox("Wartości")
        self.currentDataGroup.setLayout(self.ValuesBoxInit())

        # Layout Tabelaryczny
        Tlayout = QGridLayout()

        Tlayout.addWidget(self.ctrlButtonsGroup, 0, 0)
        Tlayout.addWidget(self.plotSaveButtonsGroup, 0, 1)
        Tlayout.addWidget(self.dataParametersGroup, 0, 2)
        Tlayout.addWidget(self.plotSettingsGroup, 0, 3)
        Tlayout.addWidget(self.currentDataGroup, 0, 4)

        # Okno wykresu
        self.canvas = MplCanvas(self, width=const.canvWid,
                                height=const.canvHght, dpi=const.canvDpi)
        Tlayout.addWidget(self.canvas, const.canvRow,
                          const.canvCol, const.canvRowDim, const.canvColDim)
        self.setLayout(Tlayout)

        self.timer = PyQt5.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

        self.showMaximized()
        return

    def VariablesInit(self):
        self.__index = 0
        self.ConfigUpdate(const.DefaultConfiguration)
        self.maxval = 0.0
        self.maxval_x = 0.0
        self.minval = 0.0
        self.minval_x = 0.0
        self.XreadFromFile = False
        self.xdata = []
        self.ydata = []
        self._plot_ref = None

        return

    def ControlBoxInit(self):
        retLayout = QGridLayout()
        self.startBtn = QPushButton("&Start", self)
        self.startBtn.setStyleSheet("background-color:lightgreen")
        self.startBtn.clicked.connect(self.start_plot)
        self.stopBtn = QPushButton("Stop", self)
        self.stopBtn.setStyleSheet("background-color:red")
        self.stopBtn.clicked.connect(self.stop_plot)
        self.saveConfBtn = QPushButton("Zapisz", self)
        self.openConfBtn = QPushButton("Wczytaj", self)
        self.saveConfBtn.clicked.connect(self.saveConfigFile)
        self.openConfBtn.clicked.connect(self.openConfigFile)

        retLayout.addWidget(
            self.startBtn, const.startBtnRow, const.startBtnCol)
        retLayout.addWidget(self.stopBtn, const.stopBtnRow, const.stopBtnCol)
        retLayout.addWidget(QLabel("Plik ustawień"), 2, 0)
        retLayout.addWidget(self.saveConfBtn,
                            const.saveConfBtnRow, const.saveConfBtnCol)
        retLayout.addWidget(self.openConfBtn,
                            const.openConfBtnRow, const.openConfBtnCol)

        return retLayout

    def PlotSaveBoxInit(self):
        retLayout = QGridLayout()
        self.saveToPicBtn = QPushButton("Zapisz PNG", self)
        self.saveToPicBtn.clicked.connect(self.savePlotToPic)
        retLayout.addWidget(self.saveToPicBtn, 0, 0)
        return retLayout

    def RuntimeSettingsBoxInit(self):
        retLayout = QGridLayout()

        samplesNumberLabel = QLabel("Ilość punktów:", self)
        samplingIntervalLabel = QLabel("Okres próbkowania [ms]:", self)
        initValueLabel = QLabel("Wartość początkowa:", self)
        endValueLabel = QLabel("Wartość końcowa:", self)
        xGenScaleLabel = QLabel("Generowanie X:")
        self.xGenLabel = QLabel("Brak X")

        self.samplesNumberEdit = QLineEdit()
        self.samplingIntervalEdit = QLineEdit()
        self.initValueEdit = QLineEdit()
        self.endValueEdit = QLineEdit()
        self.samplesNumberEdit.setText(
            str(self.Configuration['SamplesNumber']))
        self.samplingIntervalEdit.setText(
            str(self.Configuration['SamplingPeriod']))
        self.initValueEdit.setText(str(self.Configuration['InitialValue']))
        self.endValueEdit.setText(str(self.Configuration['EndValue']))

        self.genXbtn = QPushButton("Generuj X")
        self.genXbtn.clicked.connect(self.genXmethod)
        self.saveXBtn = QPushButton("Zapisz X", self)
        self.saveXBtn.clicked.connect(self.savexToFile)
        self.readXBtn = QPushButton("Wczytaj X", self)
        self.readXBtn.clicked.connect(self.readxFromFile)

        self.plotGrid = QComboBox(self)
        self.plotGrid.addItem('Brak')
        self.plotGrid.addItem('Tylko X')
        self.plotGrid.addItem('Tylko Y')
        self.plotGrid.addItem('X i Y')
        self.plotGrid.currentIndexChanged.connect(self.changePlotGrid)

        self.sampXGenCombo = QComboBox(self)
        self.sampXGenCombo.addItem('Liniowo')
        self.sampXGenCombo.addItem('Logarytmicznie')

        retLayout.addWidget(samplesNumberLabel,
                            const.SampleNumberLabelRow, const.SampleNumberLabelCol)
        retLayout.addWidget(samplingIntervalLabel,
                            const.SamplingPeriodLabelRow, const.SamplingPeriodLabelCol)
        retLayout.addWidget(initValueLabel, const.InitialValueLabelRow,
                            const.InitialValueLabelCol)
        retLayout.addWidget(
            endValueLabel, const.EndValueLabelRow, const.EndValueLabelCol)
        retLayout.addWidget(xGenScaleLabel, const.xGenScaleLabelRow,
                            const.xGenScaleLabelCol)
        retLayout.addWidget(self.samplesNumberEdit,
                            const.sampNumEditRow, const.sampNumEditCol)
        retLayout.addWidget(self.samplingIntervalEdit,
                            const.SamplingPeriodEditRow, const.SamplingPeriodEditCol)
        retLayout.addWidget(self.initValueEdit,
                            const.InitialValueEditRow, const.InitialValueEditCol)
        retLayout.addWidget(self.endValueEdit,
                            const.EndValueEditRow, const.EndValueEditCol)
        retLayout.addWidget(self.sampXGenCombo,
                            const.sampXScaleRow, const.sampXScaleCol)
        retLayout.addWidget(self.saveXBtn,
                            const.saveXBtnRow, const.saveXBtnCol)
        retLayout.addWidget(self.readXBtn,
                            const.readXBtnRow, const.readXBtnCol)
        retLayout.addWidget(self.genXbtn,
                            const.genXBtnRow, const.genXBtnCol)
        retLayout.addWidget(self.xGenLabel, const.xGenLabelRow,
                            const.xGenLabelCol)
        return retLayout

    def PlotControlBoxInit(self):
        retLayout = QGridLayout()

        self.plotLegendsEdit = QPlainTextEdit()
        self.plotLegendsEdit.setToolTip(
            'Tu wpisz legendy oddzielone średnikiem.')

        self.xLegendEdit = QLineEdit()
        self.yLegendEdit = QLineEdit()

        self.plotXscale = QComboBox(self)
        self.plotXscale.addItem('X: Liniowa')
        self.plotXscale.addItem('X: Logarytmiczna')

        self.plotYscale = QComboBox(self)
        self.plotYscale.addItem('Y: Liniowa')
        self.plotYscale.addItem('Y: Logarytmiczna')

        self.plotCntEdit = QLineEdit(self)

        retLayout.addWidget(QLabel("Ilość przebiegów:"), 0, 0)
        retLayout.addWidget(QLabel("Legenda X"), 1, 0)
        retLayout.addWidget(QLabel("Legenda Y"), 2, 0)

        retLayout.addWidget(QLabel("Siatka"), 3, 0)
        retLayout.addWidget(self.plotGrid, 3, 1)

        retLayout.addWidget(self.plotCntEdit, 0, 1)

        retLayout.addWidget(self.xLegendEdit, 1, 1)
        retLayout.addWidget(self.yLegendEdit, 2, 1)

        retLayout.addWidget(self.plotXscale, 4, 0)
        retLayout.addWidget(self.plotYscale, 4, 1)

        retLayout.addWidget(QLabel("Legendy serii"), 0, 2)
        retLayout.addWidget(self.plotLegendsEdit, 1, 2, 4, 1)

        return retLayout

    def ValuesBoxInit(self):
        retLayout = QGridLayout()

        self.currentXlabel = QLabel("x = 0", self)
        self.currentYlabel = QLabel('y = 0', self)
        self.maxLabel = QLabel("MAX: x = 0; y = 0", self)
        self.minLabel = QLabel("MIN: x = 0; y = 0", self)
        self.progressBar = QProgressBar(self)

        retLayout.addWidget(
            self.maxLabel, const.maxLabelRow, const.maxLabelCol)
        retLayout.addWidget(
            self.minLabel, const.minLabelRow, const.minLabelCol)
        retLayout.addWidget(self.currentXlabel,
                            const.currXLabRow, const.currXLabCol)
        retLayout.addWidget(self.currentYlabel,
                            const.currYLabRow, const.currYLabCol)
        retLayout.addWidget(self.progressBar, const.prgBarRow, const.prgBarCol)

        return retLayout

    def LockEdits(self):
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
        return

    def UnlockEdits(self):
        self.samplingIntervalEdit.setReadOnly(False)
        self.samplesNumberEdit.setReadOnly(False)
        self.initValueEdit.setReadOnly(False)
        self.endValueEdit.setReadOnly(False)
        self.plotXscale.setEnabled(True)
        self.plotYscale.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.openConfBtn.setEnabled(True)
        self.sampXGenCombo.setEnabled(True)
        return

    def ConfigUpdateFromGUI(self):
        dataok = False
        try:
            self.Configuration['SamplesNumber'] = int(
                self.samplesNumberEdit.text())
            self.Configuration['SamplingPeriod'] = int(
                self.samplingIntervalEdit.text())
            self.Configuration['InitialValue'] = float(
                self.initValueEdit.text())
            self.Configuration['EndValue'] = float(self.endValueEdit.text())
            self.__step = (
                self.Configuration['EndValue'] - self.Configuration['InitialValue']) / self.Configuration['SamplesNumber']
            self.Configuration['SamplesNumber'] += 1
            dataok = True
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane.", QMessageBox.Ok)

        return dataok

    def ConfigUpdate(self, newConfig):
        self.Configuration = newConfig
        return True

    def increment_index(self):
        self.__index += 1
        return

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
            self.ydata[0][index - 1] = data[0]
            self.ydata[1][index - 1] = data[1]
            self.ydata[2][index - 1] = data[2]
            self.ydata[3][index - 1] = data[3]
            self.ydata[4][index - 1] = data[4]

            extrData = self.findMinMax(data)

            if extrData[0] > self.maxval:
                self.maxval = extrData[0]
                self.maxval_x = self.xdata[index - 1]
                maxxupdt = True
            else:
                maxxupdt = False

            if extrData[1] < self.minval:
                self.minval = extrData[1]
                self.minval_x = self.xdata[index - 1]
                minupdt = True
            else:
                minupdt = False

            curridx = "idx = " + str(self.get_index())
            currx = "X = " + \
                "{:.5f}".format(self.xdata[self.get_index() - 1])
            curry = "Y = " + \
                "{:.5f}".format(self.ydata[0][self.get_index() - 1])
        else:
            self.maxval = data[0]
            self.minval = data[0]
            maxxupdt = True
            minupdt = True
            self.canvas.setAxisLabels(
                self.xLegendEdit.text(), self.yLegendEdit.text())

        self.increment_index()
        self.currentYlabel.setText(curry)
        self.currentXlabel.setText(currx)

        if maxxupdt == True:
            maxx = "MAX: X=" + \
                "{:.5f}".format(self.maxval_x) + " Y=" + \
                "{:.5f}".format(self.maxval)
            self.maxLabel.setText(maxx)

        if minupdt == True:
            minx = "MIN: X=" + \
                "{:.5f}".format(self.minval_x) + " Y=" + \
                "{:.5f}".format(self.minval)
            self.minLabel.setText(minx)

        self.canvas.setYlim(self.minval, self.maxval)
        self.canvas.plotData(self.xdata, self.ydata, lineCount)

        if index == self.__samples:
            self.stop_plot()
            QMessageBox.information(
                self, "Info", "Zakończono.", QMessageBox.Ok)
        return

    def start_plot(self):
        self.clear_plot()
        dataok = self.ConfigUpdateFromGUI()
        legends = []
        legends = self.plotLegendsEdit.toPlainText().split(';')
        self.canvas.setAxesLegend(legends)

        if dataok:
            if self.Configuration['SamplingPeriod'] > 0:
                if self.Configuration['SamplesNumber'] > 0 and self.__step != 0.0:
                    if self.XreadFromFile == False:
                        self.genXmethod()
                    else:
                        self.__samples = len(self.xdata)
                        self.samplesNumberEdit.setText(str(self.__samples))

                    dataok = True
            else:
                dataok = False

            if dataok:
                if self.__samplingPeriod < 10:
                    QMessageBox.warning(
                        self, "Uwaga!", "Uwaga, okres próbkowania niżzy niż 10 ms, może powodować niepoprawną pracę programu.")
                self.LockEdits()
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
                self.canvas.setAxisLabels(
                    self.xLegendEdit.text(), self.yLegendEdit.text())
                # Tablica na wartości Y
                self.ydata = []
                for j in range(10):
                    self.ydata.append([0.0 for i in range(self.__samples)])

                self.timer.setInterval(self.__samplingPeriod)

                try:
                    self.update_plot()
                except Exception as e:
                    QMessageBox.warning(
                        self, "Błąd", "Nieoczekiwany błąd.", QMessageBox.Ok)
                    print(e)
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
        return

    def stop_plot(self):
        self.canvas.axes.autoscale(enable=True, axis='y')
        self.timer.stop()
        self.UnlockEdits()
        return

    def clear_plot(self):
        self.__index = 0
        self.minval = 0.0
        self.maxval = 0.0
        self.canvas.clearPlot()
        self._plot_ref = None
        return

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
        return

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
        return

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
        return

    def savexToFile(self):
        if len(self.xdata) != 0:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog

            dialogBox = QFileDialog()
            dialogBox.setWindowTitle("Zapisz X do pliku")
            dialogBox.setNameFilters(
                ["Plik CSV (*.csv)"])
            dialogBox.setDefaultSuffix('csv')
            dialogBox.setAcceptMode(QFileDialog.AcceptSave)
            if dialogBox.exec_() == QFileDialog.Accepted:
                filename = dialogBox.selectedFiles()[0]
                with open(filename, 'w', newline='') as xfile:
                    wr = csv.writer(xfile)
                    for i in self.xdata:
                        wr.writerow([i])
        else:
            QMessageBox.warning(
                self, "Błąd", "X nie został jeszcze wygenerowany.", QMessageBox.Ok)
        return

    def readxFromFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        dialogBox = QFileDialog()
        dialogBox.setWindowTitle("Zapisz X do pliku")
        dialogBox.setNameFilters(["Plik CSV (*.csv)"])
        dialogBox.setDefaultSuffix('csv')
        dialogBox.setAcceptMode(QFileDialog.AcceptOpen)
        if dialogBox.exec_() == QFileDialog.Accepted:
            filename = dialogBox.selectedFiles()[0]
            with open(filename, newline='') as xfile:
                reader = csv.reader(xfile)
                self.xdata = [float(row[0]) for row in reader]

                self.XreadFromFile = True
                self.xGenLabel.setText("X wczytany")
        return

    def genXmethod(self):
        self.XreadFromFile = False
        try:
            self.__samples = int(self.samplesNumberEdit.text())
            self.__initValue = float(self.initValueEdit.text())
            self.__endValue = float(self.endValueEdit.text())
            self.__step = (self.__endValue - self.__initValue) / self.__samples
            self.__samples = self.__samples + 1

            if self.sampXGenCombo.currentIndex() == 0:
                self.xdata = list(self.__initValue + i *
                                  self.__step for i in range(self.__samples))
            elif self.sampXGenCombo.currentIndex() == 1:
                x1 = math.log10(self.__initValue)
                x2 = math.log10(self.__endValue)
                i = []
                for j in range(self.__samples):
                    i.append(x1 + j * ((x2 - x1)/(self.__samples - 1)))
                self.xdata = list(math.pow(10.0, j) for j in i)
            self.xGenLabel.setText("X wygenerowany")
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane.", QMessageBox.Ok)
        return

    def getData(self):
        index = self.get_index()

        if index == 0:
            '''
                Pierwszy obieg, nie ma jeszcze żadnych danych pomiarowych.
                Wyśli dane do urządzenia i nie odbieraj nic.
            '''
            pomiar = [0.0, 0.0, 0.0, 0.0, 0.0]

        elif index > 0:
            pomiar = []
            '''
                Pobierz dane z urządzenia z poprzedniego pomiaru i wyślij kolejną nastawę
            '''
            pomiar.append(
                math.cos(self.xdata[index - 1] * 10 * random.random()))
            pomiar.append(
                math.cos(self.xdata[index - 1] * 0.5 * random.random()))
            pomiar.append(
                math.cos(self.xdata[index - 1] * random.random()))
            pomiar.append(
                math.cos(self.xdata[index - 1] * 2 * random.random()))
            pomiar.append(
                math.cos(self.xdata[index - 1] * 0.1 * random.random()))

        return pomiar

    def findMinMax(self, data):
        minimum = min(data)
        maximum = max(data)
        return [maximum, minimum]

    def savePlotToPic(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        dialogBox = QFileDialog()
        dialogBox.setWindowTitle("Zapisz przebiegi do pliku")
        dialogBox.setNameFilters(["Obraz PNG (*.png)"])
        dialogBox.setDefaultSuffix('png')
        dialogBox.setAcceptMode(QFileDialog.AcceptSave)
        if dialogBox.exec_() == QFileDialog.Accepted:
            filename = dialogBox.selectedFiles()[0]
            self.canvas.saveToPNG(filename)
        return


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    okno = MainWindow()
    sys.exit(app.exec_())
