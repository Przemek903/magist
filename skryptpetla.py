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
odb = session.openOdb('D:\WorkstationAbqus\modelKomory.odb')

#Liczba frame w danym step'ie
#Wartosc step['Obciazenie'] nalezy ustawic zgodnie z nazwa badanego step'u
numberFrames = len(odb.steps['Step-1'].frames)



#Plik file jest plikiem w ktorym zapisywane sa wyniki 
file = open("D:\magisterka\Python Abaqus praca\model.txt", 'w+b')

for num in range(numberFrames):
        #Aktualny frame w danym step'ie
        currentFrame = odb.steps['Step-1'].frames[num]
        
        #Zmienna displacement przechowuje wartosc przemieszczen 'U' w ostatnim frame'ie\
        # w badanym step'ie
        # Zmienna displacement przechowuje wartosc naprezen 'S'
        
        displacement = currentFrame.fieldOutputs['U']
        stress = currentFrame.fieldOutputs['S']
        strain = currentFrame.fieldOutputs['LE']
        
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
        
        file.write( "\nFrame: %s" % num + '\n' )
        
        #petla wyswietlajaca wartosc przemieszczen w wezlach( wartosci w
        #jednostkach wymiarowych
        for v in centerDisplacement.values:
            file.write( "Node nr. %s   X: %s   Y: %s   Z: %s \n" % (v.nodeLabel, v.data[0], v.data[1], v.data[2]) + '\n' )
        
        #petla wyswietlajaca wartosc naprezen w Elementach( wartosci w
        #jednostkach wymiarowych
        for v in centerStress.values:
            file.write( "Element nr. %s   Sxx(S11): %s   Syy(S22): %s   Szz(S33): %s    Sxy(S12): %s   Sxz(S13): %s   Syz(S23): %s" %\
                        (v.elementLabel, v.data[0], v.data[1], v.data[2], v.data[3], v.data[4], v.data[5]) + '\n' )
        
        #petla wyswietlajaca wartosc odksztalcen w elementach( wartosci w
        #jednostkach wymiarowych
        for v in centerStress.values:
            file.write( "Element nr. %s   Exx(S11): %s   Eyy(S22): %s   Ezz(S33): %s    Exy(S12): %s   Exz(S13): %s   Eyz(S23): %s" %\
                        (v.elementLabel, v.data[0], v.data[1], v.data[2], v.data[3], v.data[4], v.data[5]) + '\n' )  


