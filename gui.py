# -*- coding: cp1250 -*-
import sys

from tkFileDialog import *
from Tkinter import *


window = Tk()
window.title("AbaqusToMATLAB")
window.geometry("550x400")


def showPath(filename):
    label = Label (window, text = filename).place(x = 200, y = 50)
    

def openFile():
    global filename
    filename = str(askopenfilename())
    showPath(filename)
    
    
yourPathLable = Label( window, text = u"Ścieżka do pliku:").place(x = 200, y = 30 )   
selectFileButton = Button(window, text = "Wybierz plik", command = openFile).place(x = 100, y = 40)

yourSelectPartLabel = Label( window, text = u"Wybierz part:").place(x = 50, y = 90 )

listBoxSp = Listbox( window, height = 5, width = 30 )
listBoxSp.insert(1, "PART-1")
listBoxSp.insert(2, "PART-2")
listBoxSp.place(x = 55, y = 120)

yourSelectnodeSetLabel = Label( window, text = u"Wybierz nodeSet:").place(x = 50, y = 220 )

listBoxSnS = Listbox( window, height = 5, width = 30 )
listBoxSnS.insert(1, "Set-1")
listBoxSnS.insert(2, "Set-2")
listBoxSnS.place(x = 55, y = 250)

yourSelectelementSetLabel = Label( window, text = u"Wybierz elementSet:").place(x = 300, y = 220 )

listBoxSeS = Listbox( window, height = 5, width = 30 )
listBoxSeS.insert(1, "Set-1")
listBoxSeS.insert(2, "Set-2")
listBoxSeS.place(x = 305, y = 250)

selectFileButton = Button(window, text = "Generuj wyniki").place(x = 230, y = 350)

window.mainloop()
