import re
import numpy as np

def createElementTable(inpFileName):
    f = open(inpFileName, 'r')
    lines = f.readlines()
    elementPosition = lines.index('*Element, type=C3D4H\n')
    elementTableOfLines = lines[elementPosition+1 : elementPosition + 1 + countNumberOfElements()] # 3300 = numberOfElements
    b = "".join(elementTableOfLines)
    elemTable = re.findall(r'\b\d+\b', b)
    elemTable = map(int, elemTable)

    col1, col2, col3, col4 = elemTable[1::5], elemTable[2::5], elemTable[3::5], elemTable[4::5]
    elem = np.array(zip(col1, col2, col3, col4))
    return elem


def countNumberOfElements(partName, stepName):
    currentFrame = odb.steps[stepName].frames[0]
    stress = currentFrame.fieldOutputs['S']
    elementS = odb.rootAssembly.instances[partName]
    centerStress = stress.getSubset(region=elementS)
    numberOfElements = len(centerStress.values)
    return numberOfElements


def countNumberOfNodes(partName, stepName):
    currentFrame = odb.steps[stepName].frames[0]
    displacement = currentFrame.fieldOutputs['U']
    nodeS = odb.rootAssembly.instances[partName]
    centerDisplacement = displacement.getSubset(region=nodeS)
    numberOfNodes = len(centerDisplacement.values)
    return numberOfNodes
