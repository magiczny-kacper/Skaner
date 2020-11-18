# Stałe wartości używane w programie, dla łatwiejszych późniejszych zmian

WindowTitle = "Skaner"

# Domyślne wartości początkowe
DefaultSamples = 1000  # Ilość próbek
DefaultSamplingPeriod = 10  # Okres próbkowania
DefaultInitialValue = 10.0  # Wartośc początkowa
DefaultEndValue = 100.0  # Krok

# Stałe GUI

# Etykiety parametrów
SampleNumberLabelRow = 3
SampleNumberLabelCol = 0

SamplingPeriodLabelRow = 0
SamplingPeriodLabelCol = 0

InitialValueLabelRow = 1
InitialValueLabelCol = 0

EndValueLabelRow = 2
EndValueLabelCol = 0

xGenScaleLabelRow = 4
xGenScaleLabelCol = 0

# Pola do wpisania parametrów
sampNumEditRow = SampleNumberLabelRow
sampNumEditCol = SampleNumberLabelCol + 1

SamplingPeriodEditRow = SamplingPeriodLabelRow
SamplingPeriodEditCol = SamplingPeriodLabelCol + 1

InitialValueEditRow = InitialValueLabelRow
InitialValueEditCol = InitialValueLabelCol + 1

EndValueEditRow = EndValueLabelRow
EndValueEditCol = EndValueLabelCol + 1

sampXScaleRow = xGenScaleLabelRow
sampXScaleCol = xGenScaleLabelCol + 1

# Aktualne wartości X i Y
maxLabelRow = 0
maxLabelCol = 0

minLabelRow = 1
minLabelCol = 0

currXLabRow = 2
currXLabCol = 0

currYLabRow = 3
currYLabCol = 0
# Progress bar
prgBarRow = 4
prgBarCol = 0


# Przyciski
startBtnRow = 0
startBtnCol = 0

stopBtnRow = 1
stopBtnCol = 0

xGenLabelRow = 0
xGenLabelCol = 2

saveXBtnRow = xGenLabelRow + 1
saveXBtnCol = xGenLabelCol

readXBtnRow = saveXBtnRow + 1
readXBtnCol = saveXBtnCol

genXBtnRow = readXBtnRow + 1
genXBtnCol = readXBtnCol

# Wybór skali wykresu
pltXsclRow = 1
pltXsclCol = 0

pltYsclRow = 2
pltYsclCol = 0

pltGridRow = 4
pltGridCol = 0

# Umieszczenie wykresu
canvWid = 5
canvHght = 4
canvDpi = 100

canvRow = 6
canvCol = 0
canvRowDim = 6
canvColDim = 6

# Opracje na plikach - etykieta i przyciski
saveConfBtnRow = 3
saveConfBtnCol = 0

openConfBtnRow = 4
openConfBtnCol = 0

maxPlotCount = 5
lineColors = ['red', 'green', 'blue', 'skyblue', 'olive']

if maxPlotCount > len(lineColors):
    raise ValueError("Ther are more lines than line colors defined")
