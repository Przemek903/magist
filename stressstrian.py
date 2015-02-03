# -*- coding: cp1250 -*-
import re
import datetime

filenam = ['D:\\AbaqusWorkstation\\ab18.rpt', 'D:\\AbaqusWorkstation\\abkjbaqus.rpt']

def stressAndStrain(fileName, stepName, partName, setName):

    for fn in fileName:
        f = open(fn, 'r')
        lines = f.readlines()
        a = []
        for values in lines:
            a.append(values.split())
        
        numberOfNodes = countNumberOfNodes(partName, stepName, setName)
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
            co1.append(float(tb[9]))
            co2.append(float(tb[10]))
            co3.append(float(tb[11]))
            co4.append(float(tb[12]))
            co5.append(float(tb[13]))
            co6.append(float(tb[14]))
        
        global stressOrStrainTable
        stre = zip(co1, co2, co3, co4, co5, co6)
        strTable[:] = stre
        str3d = strTable[...,None]
        stressOrStrainTable = np.dstack((stressOrStrainTable, str3d))    
    
    return stressOrStrainTable
