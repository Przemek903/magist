# -*- coding: cp1250 -*-
from abaqus import *
from abaqusConstants import *
import odbAccess

#Otwieranie i pobieranie dostępu do pliku odb
#Wartosc w nawiasie okresla sciezke do otwieranego pliku
odb = session.openOdb('D:\WorkstationAbqus\modelKomory.odb')

#Liczba frame w danym step'ie
#Wartosc step['Obciazenie'] nalezy ustawic zgodnie z nazwa badanego step'u
numberFrames = len(odb.steps['Step-1'].frames)

#Ostatni frame w danym step'ie
lastFrame = odb.steps['Step-1'].frames[-1]

displacement = lastFrame.fieldOutputs['U']
stress = lastFrame.fieldOutputs['S']


nodeS = odb.rootAssembly.instances['FANTOM-1'].nodeSets['SET-1']
centerDisplacement = displacement.getSubset(region=nodeS)
numberOfNodes = range(1, len(centerDisplacement.values)+1 )


centerStress = stress.getSubset(position=ELEMENT_NODAL)

tab = []

for nd in numberOfNodes:
    suma = 0
    count = 0
    for v in centerStress.values:
        if nd == v.nodeLabel:
            suma = suma + v.data[0]
            count = count + 1
        else:
            continue
    tab.append(suma/count)
