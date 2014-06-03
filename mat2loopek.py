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
lastFrame = odb.steps['Step-1'].frames[0]

displacement = lastFrame.fieldOutputs['U']
stress = lastFrame.fieldOutputs['S']


nodeS = odb.rootAssembly.instances['FANTOM-1'].nodeSets['SET-1']
centerDisplacement = displacement.getSubset(region=nodeS)
numberOfNodes = range(1, len(centerDisplacement.values)+1 )


centerStress = stress.getSubset(position=ELEMENT_NODAL)

tab = []

for nd in numberOfNodes:
    temp = []
    for v in centerStress.values:
        if nd == v.nodeLabel:
            temp.append(v.elementLabel)
        else:
            continue
    tab.append(temp)


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
    
    for num in range(19,21):    #range(numberFrames)
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
            for v in tab[nd-1]:
                    suma11 = suma11 + centerStress.values[v].data[0]
                    suma22 = suma22 + centerStress.values[v].data[1]
                    suma33 = suma33 + centerStress.values[v].data[2]
                    suma12 = suma12 + centerStress.values[v].data[3]
                    suma13 = suma13 + centerStress.values[v].data[4]
                    suma23 = suma23 + centerStress.values[v].data[5]
            
            
            co1.append(suma11/len(tab[nd-1]))
            co2.append(suma22/len(tab[nd-1]))
            co3.append(suma33/len(tab[nd-1]))
            co4.append(suma12/len(tab[nd-1]))
            co5.append(suma13/len(tab[nd-1]))
            co6.append(suma23/len(tab[nd-1]))
        
        global stressOrStrainTable
        stre = zip(co1, co2, co3, co4, co5, co6)
        strTable[:] = stre
        str3d = strTable[...,None]
        stressOrStrainTable = np.dstack((stressOrStrainTable, str3d))
    return stressOrStrainTable




sio.savemat('stress.mat', { 'stress':stressTable[:,:,1:] })
