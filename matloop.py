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

#Otwieranie i pobieranie dostępu do pliku odb
#Wartosc w nawiasie okresla sciezke do otwieranego pliku

odb = session.openOdb('D:\WorkstationAbqus\modelKomory.odb')

#Liczba frame w danym step'ie
#Wartosc step['Obciazenie'] nalezy ustawic zgodnie z nazwa badanego step'u
numberFrames = len(odb.steps['Step-1'].frames)



def initDispOrCoordTable (stepName, fieldOut, partName, setName):
    firstFrame = odb.steps[stepName].frames[0]
    displacement = firstFrame.fieldOutputs[fieldOut]
    nodeS = odb.rootAssembly.instances[partName].nodeSets[setName]
    centerDisplacement = displacement.getSubset(region=nodeS)
    nodeNumbers = len(centerDisplacement.values)
    return np.zeros((nodeNumbers,3,1))

def initStressOrStrainTable(stepName, fieldOut, partName, setName):
    firstFrame = odb.steps[stepName].frames[0]
    stress = firstFrame.fieldOutputs[fieldOut]
    elementS = odb.rootAssembly.instances[partName].elementSets[setName]
    centerStress = stress.getSubset(region=elementS)
    elementNumbers = len(centerStress.values)
    return np.zeros((elementNumbers,6,1))

dispOrCoordTable = initDispOrCoordTable ('Step-1', 'U', 'FANTOM-1', 'SET-1' )
stressOrStrainTable = initStressOrStrainTable('Step-1', 'S', 'FANTOM-1', 'SET-2' )



def stressAndStrain(stepName, fieldOut, partName, setName ):    

    for num in range(numberFrames):
        #Aktualny frame w danym step'ie
        currentFrame = odb.steps[stepName].frames[num]
        
        stress = currentFrame.fieldOutputs[fieldOut]        
        
        elementS = odb.rootAssembly.instances[partName].elementSets[setName]
        
        centerStress = stress.getSubset(region=elementS)
        
        elementNumbers = len(centerStress.values)
        strTable = np.zeros((elementNumbers,6))
        co1, co2, co3, co4, co5, co6 = [], [], [], [], [], []
        
        for v in centerStress.values:
            co1.append(v.data[0])
            co2.append(v.data[1])
            co3.append(v.data[2])
            co4.append(v.data[3])
            co5.append(v.data[4])
            co6.append(v.data[5])
        
        global stressOrStrainTable
        #global dispTable
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

stressTable = stressAndStrain('Step-1', 'S', 'FANTOM-1', 'SET-2' )
stressOrStrainTable = initStressOrStrainTable('Step-1', 'S', 'FANTOM-1', 'SET-2' )
strainTable = stressAndStrain('Step-1', 'LE', 'FANTOM-1', 'SET-2' )
dispTable = dispAndCoord('Step-1', 'U', 'FANTOM-1', 'SET-1' )
dispOrCoordTable = initDispOrCoordTable ('Step-1', 'U', 'FANTOM-1', 'SET-1' )
coordTable = dispAndCoord('Step-1', 'COORD', 'FANTOM-1', 'SET-1' )

fileName = np.array(['modelKomory.odb'])

units = np.array([[([u's'], [u'mm'], [u'N'], [u'rad'], [u'rad'])]], dtype=[('time', 'O'),\
                        ('distance', 'O'), ('force', 'O'), ('pressure', 'O'), ('rotation', 'O')])

cycleTime = np.array([1])

loads = np.array([[([[40]],)]], dtype=[('Displacement', 'O')])

sio.savemat('displ.mat', {'displacement':dispTable[:,:,1:], 'stress':stressTable[:,:,1:], 'strain': strainTable[:,:,1:], 'Coordinate': coordTable[:,:,1:],\
                          'filename':fileName, 'units':units, 'cycletime':cycleTime, 'Loads':loads })


