import numpy as np
import scipy.io as sio
import pickle

name = '9mmdolHyp.mat'

with open('9mmdol.pickle') as f:
    dispTable, stressTable, strainTable, coordTable, fileName, units, cycleTime, loads, elementTable, amplitudeTable, dateTable = pickle.load(f)

sio.savemat(name, {'displ9mdH':dispTable[:,:,1:], 'stress9mdH':stressTable[:,:,1:], 'strain9mdH': strainTable[:,:,1:], 'Coord9mdH': coordTable[:,:,1:],\
                          'filename9mdH':fileName, 'units':units, 'cycletime9mdH':cycleTime, 'Loads':loads, 'Elem9mdH':elementTable, 'Amplitude':amplitudeTable,\
                          'CreationTime9mdH':dateTable })
