# -*- coding: cp1250 -*-
import numpy as np
from abaqus import *
from abaqusConstants import *
import odbAccess
import re
import datetime
import pickle

#Otwieranie i pobieranie dostępu do pliku odb
#Wartosc w nawiasie okresla sciezke do otwieranego pliku

odb = session.openOdb('D:\AbaqusWorkstation\9mmOK.odb')

#Liczba frame'ow w danym step'ie
#Wartosc step['Step-1'] nalezy ustawic zgodnie z nazwa symulowanego step'u
numberFrames = len(odb.steps['Step-1'].frames)

nodeNumb = 93100

def initStressOrStrainTable(number):

    return np.zeros((number,6,1))

stressOrStrainTable = initStressOrStrainTable(nodeNumb)


def strain(fileName, number):
    
    for fn in fileName:
        f = open(fn, 'r')
        lines = f.readlines()
        a = []
        for values in lines:
            a.append(values.split())
        
        numberOfNodes = number
        tab = []
        for num in range(1,numberOfNodes+1):
            for ln in a:
                if ln[0] == str(num):
                    tab.append(ln)
                    a.remove(ln)
                    break
        
        strTable = np.zeros((numberOfNodes,6))
        co1, co2, co3, co4, co5, co6 = [], [], [], [], [], []
        for tb in tab:
            co1.append(float(tb[5]))
            co2.append(float(tb[6]))
            co3.append(float(tb[7]))
            co4.append(float(tb[8]))
            co5.append(float(tb[9]))
            co6.append(float(tb[10]))
        
        global stressOrStrainTable
        stre = zip(co1, co2, co3, co4, co5, co6)
        strTable[:] = stre
        str3d = strTable[...,None]
        stressOrStrainTable = np.dstack((stressOrStrainTable, str3d))    
    
    return stressOrStrainTable


raportStress = []
raportStrain = []

for an in range(1,21):
	raportStress.append('D:\\Stary Komputer\\magisterka\\Raporty\\9mmdol\\Raporty\\s%s.rpt' % an)
	raportStrain.append('D:\\Stary Komputer\\magisterka\\Raporty\\9mmdol\\Raporty\\le%s.rpt' % an)

strainTable = strain(raportStrain, nodeNumb)
cycleTime = np.array([1])

with open('9mmdol.pickle', 'w') as f:
    pickle.dump([strainTable[:,:,:], cycleTime], f)

