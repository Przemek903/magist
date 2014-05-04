# -*- coding: cp1250 -*-
"""

Skrypt otwierający plik wyjściowy programu ABAQUS ODB, oraz plik wejsciowy INP  i generujący raporty
poszczególnych wartości:
- przemieszczen linowych
- odksztalcen
- naprezen
w badanym modelu

"""

# importy wykorzystywanych w skrypcie modulow
import sys

# zmiana sciezki systemowej programu ABAQUS w celu umozliwienia korzystania z modulow numpy i scipy
sys.path = sys.path + ['D:\\python\\Lib\\idlelib', 'C:\\Windows\\system32\\python26.zip', 'D:\\python\\DLLs',\
                       'D:\\python\\lib', 'D:\\python\\lib\\plat-win', 'D:\\python\\lib\\lib-tk', 'D:\\python',\
                       'D:\\python\\lib\\site-packages']

import numpy as np
import scipy.io as sio
from abaqus import *
from abaqusConstants import *
import odbAccess
import re
import datetime

#Otwieranie i pobieranie dostępu do pliku odb
#Wartosc w nawiasie okresla sciezke do otwieranego pliku

odb = session.openOdb('D:\WorkstationAbqus\modelKomory.odb')

#Liczba frame'ow w danym step'ie
#Wartosc step['Step-1'] nalezy ustawic zgodnie z nazwa symulowanego step'u
numberFrames = len(odb.steps['Step-1'].frames)



def countNumberOfElements(partName, stepName):
    """
        Dane wejsciowe:
        partName - nazwa czesci modelu
        stepName - nazwa kroku analizy

        Opis dzialania:
        Funkcja zlicza liczbe elementow w badanym modelu

        Dane wyjsciowe:
        numberOfElements - liczba elementow
    """
    firstFrame = odb.steps[stepName].frames[0]
    stress = firstFrame.fieldOutputs['S']
    elementS = odb.rootAssembly.instances[partName]
    centerStress = stress.getSubset(region=elementS)
    numberOfElements = len(centerStress.values)
    return numberOfElements


def countNumberOfNodes(partName, stepName, setName):
    """
        Dane wejsciowe:
        partName - nazwa czesci modelu
        stepName - nazwa kroku analizy
        setName  - nazwa set'u analizy

        Opis dzialania:
        Funkcja zlicza liczbe wezlow w badanym modelu

        Dane wyjsciowe:
        numberOfElements - liczba wezlow
    """    
    firstFrame = odb.steps[stepName].frames[0]
    displacement = firstFrame.fieldOutputs['U']
    nodeS = odb.rootAssembly.instances[partName].nodeSets[setName]
    centerDisplacement = displacement.getSubset(region=nodeS)
    numberOfNodes = len(centerDisplacement.values)
    return numberOfNodes



def initDispOrCoordTable (stepName, partName, setName):
    """
        Dane wejsciowe:
        partName - nazwa czesci modelu
        stepName - nazwa kroku analizy
        setName  - nazwa set'u analizy

        Opis dzialania:
        Funkcja generuje wypelniona zerami tablice trojwymiarowa o wymiarach [nodeNumbers - liczbaWezlow][3-liczba wspolrzednych np. przemieszczen 'U'][1] 

        Dane wyjsciowe:
        Tablica trojwymiarowa [nodeNumbers][3][1]
    """
    nodeNumbers = countNumberOfNodes(partName, stepName, setName)
    return np.zeros((nodeNumbers,3,1))

def initStressOrStrainTable(stepName, partName, setName):
    """
        Dane wejsciowe:
        partName - nazwa czesci modelu
        stepName - nazwa kroku analizy
        setName  - nazwa set'u analizy

        Opis dzialania:
        Funkcja generuje wypelniona zerami tablice trojwymiarowa o wymiarach [nodeNumbers - liczbaWezlow][6-liczba wspolrzednych np. odksztalcen 'LE'][1] 

        Dane wyjsciowe:
        Tablica trojwymiarowa [nodeNumbers][6][1]
    """
    nodeNumbers = countNumberOfNodes(partName, stepName, setName)
    return np.zeros((nodeNumbers,6,1))

dispOrCoordTable = initDispOrCoordTable ('Step-1', 'FANTOM-1', 'SET-1' )
stressOrStrainTable = initStressOrStrainTable('Step-1', 'FANTOM-1', 'SET-1')



def createElementTable(inpFileName, stepName, partName):
    """
        Dane wejsciowe:
        inpFileName - nazwa pliku wejsciowego .inp
        stepName - nazwa kroku analizy
        partName - nazwa czesci modelu

        Opis dzialania:
        Funkcja generuje tablice wezlow wchodzacych w sklad kazdego z elementow 

        Dane wyjsciowe:
        Tablica dwuwymiarowa [elementNumbers][4]
    """
    f = open(inpFileName, 'r')
    lines = f.readlines()
    elementPosition = lines.index('*Element, type=C3D4H\n')
    elementTableOfLines = lines[elementPosition+1 : elementPosition + 1 + countNumberOfElements(partName, stepName)] 
    b = "".join(elementTableOfLines)
    elemTable = re.findall(r'\b\d+\b', b)
    elemTable = map(int, elemTable)
    
    col1, col2, col3, col4 = elemTable[1::5], elemTable[2::5], elemTable[3::5], elemTable[4::5]
    elem = np.array(zip(col1, col2, col3, col4))
    return elem



def createAmplitudeTable(inpFileName, ampName):
    """
        Dane wejsciowe:
        inpFileName - nazwa pliku wejsciowego .inp
        ampName - nazwa wykorzystywanego zakresu amplitud w symulacji

        Opis dzialania:
        Funkcja generuje jednowymiarowa tablice z kolejnymi warosciami amplitud wykorzystywanymi w symulacji. Wymiki są przeskalowane z przedzialu <0,1>.
        Wartosc 1 oznacza maksymalna amplitude wykorzystywana w symulacji.

        Dane wyjsciowe:
        Tablica djednowymiarowa [liczbaAmplitod]
    """
    f = open(inpFileName, 'r')
    lines = f.readlines()
    ampPosition = lines.index('*Amplitude, name=%s\n' % (ampName) )
    ampTempTableOfLines = lines[ampPosition : ]
    ampTableOfLines = ampTempTableOfLines[ 1 : ampTempTableOfLines.index('** \n') ]
    b = "".join(ampTableOfLines)
    ampTable = re.findall(r'\d+.\d+', b)
    ampTable = map(float, ampTable)
    amp = np.array(zip(ampTable))
    return amp



def stressAndStrain(stepName, fieldOut, partName, setName):
    """
        Dane wejsciowe:
        stepName - nazwa kroku analizy
        fieldOut - nazwa danych wyjsciowych, ktorych wyniki chcemy uzyskac
        partName - nazwa czesci modelu
        setName  - nazwa set'u analizy

        Opis dzialania:
        Funkcja generuje tablice trojwymiarowa o wymiarach [nodeNumbers - liczbaWezlow][6-liczba wspolrzednych np. odksztalcen 'LE']
        [numberOfFrames - liczba frame'ow w symulacji]
        Funkcja generuje tablice dwuwymiarowa dla kazdego frame, a nastepnie 'skleja' te tablice tworzac wyjsciaowa tablice trojwymiarowa.   

        Dane wyjsciowe:
        Tablica trojwymiarowa [nodeNumbers][6][numberOfFrames]
    """
    
    for num in range(12,14):    #range(numberFrames)
        #Aktualny frame w danym step'ie
        currentFrame = odb.steps[stepName].frames[num]
        
        #Wyliczanie liczby wezlow 
        numberOfNodes = countNumberOfNodes(partName, stepName, setName)
        arrayNumberOfNodes = range(1, numberOfNodes+1 )
        
        
        stress = currentFrame.fieldOutputs[fieldOut]        
        centerStress = stress.getSubset(position=ELEMENT_NODAL)
        
        
        strTable = np.zeros((numberOfNodes,6))
        co1, co2, co3, co4, co5, co6 = [], [], [], [], [], []
        
        for nd in arrayNumberOfNodes:
            suma11, suma22, suma33, suma12, suma13, suma23 = 0,0,0,0,0,0
            count = 0
            for v in centerStress.values:
                if nd == v.nodeLabel:
                    suma11 = suma11 + v.data[0]
                    suma22 = suma22 + v.data[1]
                    suma33 = suma33 + v.data[2]
                    suma12 = suma12 + v.data[3]
                    suma13 = suma13 + v.data[4]
                    suma23 = suma23 + v.data[5]
                    count = count + 1
                else:
                    continue
                
            co1.append(suma11/count)
            co2.append(suma22/count)
            co3.append(suma33/count)
            co4.append(suma12/count)
            co5.append(suma13/count)
            co6.append(suma23/count)
        
        global stressOrStrainTable
        stre = zip(co1, co2, co3, co4, co5, co6)
        strTable[:] = stre
        str3d = strTable[...,None]
        stressOrStrainTable = np.dstack((stressOrStrainTable, str3d))
    return stressOrStrainTable


def dispAndCoord(stepName, fieldOut, partName, setName ):
    """
        Dane wejsciowe:
        stepName - nazwa kroku analizy
        fieldOut - nazwa danych wyjsciowych, ktorych wyniki chcemy uzyskac
        partName - nazwa czesci modelu
        setName  - nazwa set'u analizy

        Opis dzialania:
        Funkcja generuje tablice trojwymiarowa o wymiarach [nodeNumbers - liczbaWezlow][3-liczba wspolrzednych np. przemieszczen 'U']
        [numberOfFrames - liczba frame'ow w symulacji]
        Funkcja generuje tablice dwuwymiarowa dla kazdego frame, a nastepnie 'skleja' te tablice tworzac wyjsciaowa tablice trojwymiarowa.   

        Dane wyjsciowe:
        Tablica trojwymiarowa [nodeNumbers][6][numberOfFrames]
    """
    
    for num in range(numberFrames):
        currentFrame = odb.steps[stepName].frames[num]
        
        displacement = currentFrame.fieldOutputs[fieldOut]        
        
        nodeS = odb.rootAssembly.instances[partName].nodeSets[setName]
        
        centerDisplacement = displacement.getSubset(region=nodeS)
        
        nodeNumbers = len(centerDisplacement.values)
        displacementTable = np.zeros((nodeNumbers,3))
        col1, col2, col3 = [], [], []
        
        for v in centerDisplacement.values:
            col1.append(v.data[0])
            col2.append(v.data[1])
            col3.append(v.data[2])
        
        global dispOrCoordTable
        disp = zip(col1, col2, col3)
        displacementTable[:] = disp
        disp3d = displacementTable[...,None]
        dispOrCoordTable = np.dstack((dispOrCoordTable,disp3d))
    return dispOrCoordTable



stressTable = stressAndStrain('Step-1', 'S', 'FANTOM-1', 'SET-1' )
stressOrStrainTable = initStressOrStrainTable('Step-1', 'FANTOM-1', 'SET-1' )
strainTable = stressAndStrain('Step-1', 'LE', 'FANTOM-1', 'SET-1' )
dispTable = dispAndCoord('Step-1', 'U', 'FANTOM-1', 'SET-1' )
dispOrCoordTable = initDispOrCoordTable ('Step-1', 'FANTOM-1', 'SET-1' )
coordTable = dispAndCoord('Step-1', 'COORD', 'FANTOM-1', 'SET-1' )
elementTable = createElementTable('D:\\WorkstationAbqus\\modelKomory.inp', 'Step-1', 'FANTOM-1')
amplitudeTable = createAmplitudeTable('D:\\WorkstationAbqus\\modelKomory.inp', 'Amp-1')

today = datetime.datetime.now()
dateTable = [today.year, today.month, today.day, today.hour, today.minute, today.second]

fileName = np.array(['modelKomory.odb'])

units = np.array([[([u's'], [u'mm'], [u'N'], [u'rad'], [u'rad'])]], dtype=[('time', 'O'),\
                        ('distance', 'O'), ('force', 'O'), ('pressure', 'O'), ('rotation', 'O')])

cycleTime = np.array([1])

loads = np.array([[([[40]],)]], dtype=[('Displacement', 'O')])

# wygenerowanie pliku .mat 
sio.savemat('displ.mat', {'displacement':dispTable[:,:,1:], 'stress':stressTable[:,:,1:], 'strain': strainTable[:,:,1:], 'Coordinate': coordTable[:,:,1:],\
                          'filename':fileName, 'units':units, 'cycletime':cycleTime, 'Loads':loads, 'Elements':elementTable, 'Amplitude':amplitudeTable,\
                          'CreationTime':dateTable })


