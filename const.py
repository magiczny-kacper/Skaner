# Stałe wartości używane w programie, dla łatwiejszych późniejszych zmian

# Domyślne wartości początkowe
defSamples = 1000  # Ilość próbek
defSamplingPeriod = 10  # Okres próbkowania
definitValue = 10.0  # Wartośc początkowa
defendValue = 100.0  # Krok

# Stałe GUI

# Etykiety parametrów
sampNumLabRow = 3
sampNumLabCol = 0

sampIntLabRow = 0
sampIntLabCol = 0

iniValLabRow = 1
iniValLabCol = 0

endValLabRow = 2
endValLabCol = 0

xGenScaleLabelRow = 4
xGenScaleLabelCol = 0

# Pola do wpisania parametrów
sampNumEditRow = sampNumLabRow
sampNumEditCol = sampNumLabCol + 1

sampIntEditRow = sampIntLabRow
sampIntEditCol = sampIntLabCol + 1

iniValEditRow = iniValLabRow
iniValEditCol = iniValLabCol + 1

endValEditRow = endValLabRow
endValEditCol = endValLabCol + 1

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
