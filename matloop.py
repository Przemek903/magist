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
#import gui

#Otwieranie i pobieranie dostępu do pliku odb
#Wartosc w nawiasie okresla sciezke do otwieranego pliku

#graphic()
odb = session.openOdb('D:\WorkstationAbqus\modelKomory.odb')

#Liczba frame w danym step'ie
#Wartosc step['Obciazenie'] nalezy ustawic zgodnie z nazwa badanego step'u
numberFrames = len(odb.steps['Step-1'].frames)


firstFrame = odb.steps['Step-1'].frames[0]
displacement = firstFrame.fieldOutputs['U']
nodeS = odb.rootAssembly.instances['FANTOM-1'].nodeSets['SET-1']
centerDisplacement = displacement.getSubset(region=nodeS)
nodeNumbers = len(centerDisplacement.values)
dispTable = np.zeros((nodeNumbers,3,1))

#Plik file jest plikiem w ktorym zapisywane sa wyniki 
file = open("D:\magisterka\Python Abaqus praca\model.txt", 'w+b')

for num in range(numberFrames):
        #Aktualny frame w danym step'ie
        currentFrame = odb.steps['Step-1'].frames[num]
        
        #Zmienna displacement przechowuje wartosc przemieszczen 'U' w ostatnim frame'ie\
        # w badanym step'ie
        # Zmienna displacement przechowuje wartosc naprezen 'S'
        
        coor = currentFrame.fieldOutputs['COORD']
        displacement = currentFrame.fieldOutputs['U']
        stress = currentFrame.fieldOutputs['S']
        strain = currentFrame.fieldOutputs['LE']
        #pressure = currentFrame.fieldOutputs['P']
        
        #Zmienna nodeS przechowuje referencje do wybranego nodeSets( zadanego set'u), 
        #instance odnosi sie wybranej czesci
        #Zmienna elementS przechowuje referencje do wybranego elementSets. konieczne jest \
        # tu ustawienie setu elementow
        
        nodeS = odb.rootAssembly.instances['FANTOM-1'].nodeSets['SET-1']
        elementS = odb.rootAssembly.instances['FANTOM-1'].elementSets['SET-2']
        
        #Zmienna centerDisplacement przechowuje referencje do przemieszczen w konkretnym\
        # set'iec
        #Zmienna centerStress przechowuje referencje do przemieszczen
        
        centerDisplacement = displacement.getSubset(region=nodeS)
        centerStress = stress.getSubset(region=elementS)
        centerStrain = strain.getSubset(region=elementS)
        centerCoor = coor.getSubset(region=nodeS)
        
        nodeNumbers = len(centerDisplacement.values)
        displacementTable = np.zeros((nodeNumbers,3))
        col1, col2, col3 = [], [], []
        
        for v in centerDisplacement.values:
            col1.append(v.data[0])
            col2.append(v.data[1])
            col3.append(v.data[2])
        
        disp = zip(col1, col2, col3)
        displacementTable[:] = disp
        disp3d = displacementTable[...,None]
        #dispTable = np.array((nodeNumbers,3,numberFrames))
        dispTable = np.dstack((dispTable,disp3d))
        

a = dispTable[:,:,1:]
sio.savemat('displ.mat', {'disp':a})
