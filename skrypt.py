# -*- coding: cp1250 -*-
"""

Skrypt otwierający plik wyjściowy programu ABAQUS ODB i generujący raporty
poszczególnych wartości:
- przemieszczen linowych
- odksztalcen
- naprezen
w badanym obiekcie

"""

from abaqus import *
from abaqusConstants import *
import odbAccess

#Otwieranie i pobieranie dostępu do pliku odb
#Wartosc w nawiasie okresla sciezke do otwieranego pliku
odb = session.openOdb('D:\WorkstationAbqus\plyta.odb')

#Liczba frame w danym step'ie
#Wartosc step['Obciazenie'] nalezy ustawic zgodnie z nazwa badanego step'u
numberFrames = len(odb.steps['Obciazenie'].frames)

#Ostatni frame w danym step'ie
lastFrame = odb.steps['Obciazenie'].frames[-1]

#Zmienna displacement przechowuje wartosc przemieszczen 'U' w ostatnim frame'ie/
# w badanym step'ie
# Zmienna displacement przechowuje wartosc naprezen 'S'
displacement = lastFrame.fieldOutputs['U']
stress = lastFrame.fieldOutputs['S']

#Zmienna nodeS przechowuje referencje do wybranego nodeSets( zadanego set'u), 
#instance odnosi sie wybranej czesci
#Zmienna elementS przechowuje referencje do wybranego elementSets. konieczne jest /
# tu ustawienie setu elementow.
nodeS = odb.rootAssembly.instances['TARCZA-1'].nodeSets['SET-1']
elementS = odb.rootAssembly.instances['TARCZA-1'].elementSets['SET-2']

#Zmienna centerDisplacement przechowuje referencje do przemieszczen w konkretnym/
# set'iec
#Zmienna centerStress przechowuje referencje do przemieszczen
centerDisplacement = displacement.getSubset(region=nodeS)
centerStress = stress.getSubset(region=elementS)

#petla wyswietlajaca wartosc przemieszczen w wezlach( wartosci w
#jednostkach wymiarowych
for v in centerDisplacement.values:
    print v.nodeLabel, ": X: ", v.data[0], " Y: ", v.data[1]#, " Z: ", v.data[2]

#petla wyswietlajaca wartosc naprezen w wezlach( wartosci w
#jednostkach wymiarowych
for v in centerStress.values:
    print v.elementLabel, ": Sxx(S11): ", v.data[0], " Syy(S22): ", v.data[1], " Szz(S33): ", v.data[2], ": Sxy(S12): ", v.data[3]#, " Sxz(S13): ", v.data[4], " Syz(S23): ", v.data[5]    

