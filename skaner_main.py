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
    QGroupBox


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
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
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
        else:
            # We have a reference, we can use it to update the data for that line.
            for i in range(lines):
                self.plotref[i].set_ydata(ydata[i])
        # Trigger the canvas to update and redraw.
        self.draw()

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
        if min == max:
            self.axes.set_ylim(min)
        else:
            if min > 0:
                minn = min * 0.9
            else:
                minn = min * 1.1

            if max > 0:
                maxx = max * 1.1
            else:
                maxx = max * 0.9
            self.axes.set_ylim(minn, maxx)
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
        # Inicjlizacja zmiennych
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Skaner")
        self.__index = 0
        self.__samples = const.defSamples
        self.__samplingPeriod = const.defSamplingPeriod
        self.__initValue = const.definitValue
        self.__endValue = const.defendValue
        self.maxval = 0.0
        self.maxval_x = 0.0
        self.minval = 0.0
        self.minval_x = 0.0
        self.XreadFromFile = False

        # Definicje etkiet w programie
        # Etykiety, umieszczone obok pół wpisywania danych
        samplesNumberLabel = QLabel("Ilość punktów:", self)
        samplingIntervalLabel = QLabel("Okres próbkowania [ms]:", self)
        initValueLabel = QLabel("Wartość początkowa:", self)
        endValueLabel = QLabel("Wartość końcowa:", self)
        xGenScaleLabel = QLabel("Generowanie X:")
        self.xGenLabel = QLabel("Brak X")

        # Etykiety wyświetlania współrzędnych ostatniego punktu
        self.currentXlabel = QLabel("x = 0", self)
        self.currentYlabel = QLabel('y = 0', self)
        self.maxLabel = QLabel("MAX: x = 0; y = 0", self)
        self.minLabel = QLabel("MIN: x = 0; y = 0", self)

        # Definicje pól wprowadzania tekstu w programie
        self.samplesNumberEdit = QLineEdit()
        self.samplingIntervalEdit = QLineEdit()
        self.initValueEdit = QLineEdit()
        self.endValueEdit = QLineEdit()
        self.samplesNumberEdit.setText(str(const.defSamples))
        self.samplingIntervalEdit.setText(str(const.defSamplingPeriod))
        self.initValueEdit.setText(str(const.definitValue))
        self.endValueEdit.setText(str(const.defendValue))
        self.xLegendEdit = QLineEdit()
        self.yLegendEdit = QLineEdit()

        self.lineLegendsEdit = []
        for i in range(lineCount):
            self.lineLegendsEdit.append(QLineEdit())
            self.lineLegendsEdit[i].setToolTip('Przebieg ' + str(i))

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
        self.genXbtn = QPushButton("Generuj X")
        self.genXbtn.clicked.connect(self.genXmethod)
        self.saveXBtn = QPushButton("Zapisz X", self)
        self.saveXBtn.clicked.connect(self.savexToFile)
        self.readXBtn = QPushButton("Wczytaj X", self)
        self.readXBtn.clicked.connect(self.readxFromFile)
        self.saveToPicBtn = QPushButton("Zapisz PNG", self)
        self.saveToPicBtn.clicked.connect(self.savePlotToPic)

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

        self.plotCntCombo = QComboBox(self)
        for i in range(5):
            if i == 0:
                suffix = " przebieg"
            else:
                suffix = " przebiegów"
            self.plotCntCombo.addItem(str(i + 1) + suffix)

        # Progres bar
        self.progressBar = QProgressBar(self)

        # Boxy na widgety
        self.plotSaveButtonsGroup = QGroupBox("Zapis przebiegu")
        grdLay = QGridLayout()
        grdLay.addWidget(self.saveToPicBtn, 0, 0)
        self.plotSaveButtonsGroup.setLayout(grdLay)

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
        grdLay.addWidget(self.saveXBtn,
                         const.saveXBtnRow, const.saveXBtnCol)
        grdLay.addWidget(self.readXBtn,
                         const.readXBtnRow, const.readXBtnCol)
        grdLay.addWidget(self.genXbtn,
                         const.genXBtnRow, const.genXBtnCol)
        grdLay.addWidget(self.xGenLabel, const.xGenLabelRow,
                         const.xGenLabelCol)
        self.dataParametersGroup.setLayout(grdLay)

        self.currentDataGroup = QGroupBox("Wartości")
        grdLay = QGridLayout()
        grdLay.addWidget(self.maxLabel, const.maxLabelRow, const.maxLabelCol)
        grdLay.addWidget(self.minLabel, const.minLabelRow, const.minLabelCol)
        grdLay.addWidget(self.currentXlabel,
                         const.currXLabRow, const.currXLabCol)
        grdLay.addWidget(self.currentYlabel,
                         const.currYLabRow, const.currYLabCol)
        grdLay.addWidget(self.progressBar, const.prgBarRow, const.prgBarCol)
        self.currentDataGroup.setLayout(grdLay)

        self.plotSettingsGroup = QGroupBox("Ustawienia wykresu")
        grdLay = QGridLayout()
        grdLay.addWidget(QLabel("Skala"), 0, 0)
        grdLay.addWidget(QLabel("Legenda X"), 0, 1)
        grdLay.addWidget(QLabel("Legenda Y"), 2, 1)
        grdLay.addWidget(self.xLegendEdit, 1, 1)
        grdLay.addWidget(self.yLegendEdit, 3, 1)
        grdLay.addWidget(self.plotXscale, const.pltXsclRow, const.pltXsclCol)
        grdLay.addWidget(self.plotYscale, const.pltYsclRow, const.pltYsclCol)
        grdLay.addWidget(QLabel("Siatka"), 3, 0)
        grdLay.addWidget(self.plotGrid, const.pltGridRow, const.pltGridCol)
        grdLay.addWidget(self.plotCntCombo, 4, 1)

        for i in range(lineCount):
            grdLay.addWidget(self.lineLegendsEdit[i], i, 3)

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

    def start_plot(self):
        self.clear_plot()
        try:
            self.__samples = int(self.samplesNumberEdit.text())
            self.__samplingPeriod = int(self.samplingIntervalEdit.text())
            self.__initValue = float(self.initValueEdit.text())
            self.__endValue = float(self.endValueEdit.text())
            self.__step = (self.__endValue - self.__initValue) / self.__samples
            self.__samples = self.__samples + 1
            legends = []
            for i in range(lineCount):
                legends.append(self.lineLegendsEdit[i].text())
            self.canvas.setAxesLegend(legends)
            dataok = True
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Błędne dane.", QMessageBox.Ok)
            dataok = False
        if dataok:
            if self.__samplingPeriod > 0:
                if self.__samples > 0 and self.__step != 0.0:
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
        #self.canvas.setAutoscale(True, 'both')

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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    okno = MainWindow()
    sys.exit(app.exec_())
