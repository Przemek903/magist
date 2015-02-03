def initStressAndStrain(stepName, fieldOut, partName, setName):
    currentFrame = odb.steps[stepName].frames[0]
    numberOfNodes = countNumberOfNodes(partName, stepName, setName)
    arrayNumberOfNodes = range(1, numberOfNodes+1 )
        
        
    stress = currentFrame.fieldOutputs[fieldOut]        
    centerStress = stress.getSubset(position=ELEMENT_NODAL)
        
        
    strTable = np.zeros((numberOfNodes,6))
    co1 = []

    for nd in arrayNumberOfNodes: 
        count = 0
        for v in centerStress.values:
            if nd == v.nodeLabel:
                count = count + 1
            else:
                continue
                
        co1.append(count)
        global initialCountTable
        initialCountTable = co1
    return initialCountTable


global initial
initial = initStressAndStrain(stepName, fieldOut, partName, setName)

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
    
    for num in range(numberFrames):
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
                elif count == initial[nd-1]:
                    break
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
        print "Jestem framem %s" % num
        print datetime.datetime.now()
    return stressOrStrainTable
