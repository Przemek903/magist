# -*- coding: cp1250 -*-
"""

Skrypt otwierający plik wyjściowy programu ABAQUS ODB i generujący raporty
poszczególnych wartości:
- przemieszczen linowych
- odksztalcen
- naprezen
w badanym obiekcie

"""
import sys

sys.path = sys.path + ['D:\\python\\Lib\\idlelib', 'C:\\Windows\\system32\\python26.zip', 'D:\\python\\DLLs',\
                       'D:\\python\\lib', 'D:\\python\\lib\\plat-win', 'D:\\python\\lib\\lib-tk', 'D:\\python',\
                       'D:\\python\\lib\\site-packages']

import numpy as np
import scipy.io as sio
from abaqus import *
from abaqusConstants import *
import odbAccess
import re

#Otwieranie i pobieranie dostępu do pliku odb
#Wartosc w nawiasie okresla sciezke do otwieranego pliku

odb = session.openOdb('D:\WorkstationAbqus\modelKomory.odb')

#Liczba frame w danym step'ie
#Wartosc step['Obciazenie'] nalezy ustawic zgodnie z nazwa badanego step'u
numberFrames = len(odb.steps['Step-1'].frames)



def countNumberOfElements(partName, stepName):
    firstFrame = odb.steps[stepName].frames[0]
    stress = firstFrame.fieldOutputs['S']
    elementS = odb.rootAssembly.instances[partName]
    centerStress = stress.getSubset(region=elementS)
    numberOfElements = len(centerStress.values)
    return numberOfElements


def countNumberOfNodes(partName, stepName, setName):
    firstFrame = odb.steps[stepName].frames[0]
    displacement = firstFrame.fieldOutputs['U']
    nodeS = odb.rootAssembly.instances[partName].nodeSets[setName]
    centerDisplacement = displacement.getSubset(region=nodeS)
    numberOfNodes = len(centerDisplacement.values)
    return numberOfNodes



def initDispOrCoordTable (stepName, partName, setName):
    nodeNumbers = countNumberOfNodes(partName, stepName, setName)
    return np.zeros((nodeNumbers,3,1))

def initStressOrStrainTable(stepName, partName, setName):
    nodeNumbers = countNumberOfNodes(partName, stepName, setName)
    return np.zeros((nodeNumbers,6,1))

dispOrCoordTable = initDispOrCoordTable ('Step-1', 'FANTOM-1', 'SET-1' )
stressOrStrainTable = initStressOrStrainTable('Step-1', 'FANTOM-1', 'SET-1')



def createElementTable(inpFileName, stepName, partName):
    f = open(inpFileName, 'r')
    lines = f.readlines()
    elementPosition = lines.index('*Element, type=C3D4H\n')
    elementTableOfLines = lines[elementPosition+1 : elementPosition + 1 + countNumberOfElements(partName, stepName)] # 3300 = numberOfElements
    b = "".join(elementTableOfLines)
    elemTable = re.findall(r'\b\d+\b', b)
    elemTable = map(int, elemTable)
    
    col1, col2, col3, col4 = elemTable[1::5], elemTable[2::5], elemTable[3::5], elemTable[4::5]
    elem = np.array(zip(col1, col2, col3, col4))
    return elem


def stressAndStrain(stepName, fieldOut, partName):    

    for num in range(12,14):    #range(numberFrames)
        #Aktualny frame w danym step'ie
        currentFrame = odb.steps[stepName].frames[num]
        
        #Wyliczanie liczby wezlow 
        numberOfNodes = countNumberOfNodes(partName, stepName)
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

    for num in range(numberFrames):
        #Aktualny frame w danym step'ie
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





stressTable = stressAndStrain('Step-1', 'S', 'FANTOM-1' )
stressOrStrainTable = initStressOrStrainTable('Step-1', 'FANTOM-1', 'SET-1' )
strainTable = stressAndStrain('Step-1', 'LE', 'FANTOM-1' )
dispTable = dispAndCoord('Step-1', 'U', 'FANTOM-1', 'SET-1' )
dispOrCoordTable = initDispOrCoordTable ('Step-1', 'FANTOM-1', 'SET-1' )
coordTable = dispAndCoord('Step-1', 'COORD', 'FANTOM-1', 'SET-1' )
elementTable = createElementTable('D:\\WorkstationAbqus\\modelKomory.inp', 'Step-1', 'FANTOM-1')

fileName = np.array(['modelKomory.odb'])

units = np.array([[([u's'], [u'mm'], [u'N'], [u'rad'], [u'rad'])]], dtype=[('time', 'O'),\
                        ('distance', 'O'), ('force', 'O'), ('pressure', 'O'), ('rotation', 'O')])

cycleTime = np.array([1])

loads = np.array([[([[40]],)]], dtype=[('Displacement', 'O')])

sio.savemat('displ.mat', {'displacement':dispTable[:,:,1:], 'stress':stressTable[:,:,1:], 'strain': strainTable[:,:,1:], 'Coordinate': coordTable[:,:,1:],\
                          'filename':fileName, 'units':units, 'cycletime':cycleTime, 'Loads':loads, 'Elements':elementTable })


