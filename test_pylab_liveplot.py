#!/usr/bin/env python
import time
import numpy as np
import matplotlib
matplotlib.use('GTKAgg') # do this before importing pylab
from random import random

import matplotlib.pyplot as plt

fig = plt.figure()

ax = fig.add_subplot(111)

def animate():
    tstart = time.time()                 # for profiling
    x = np.linspace(0, 2*np.pi, 50)        # x-array
    line, = ax.plot(x, np.sin(x))

    y = [ random() for i in range(50)]

    for i in np.arange(1,20000):
        y = [np.sin(x[i % len(x)])+.3*(random()-.5)] + y
        y.pop()
        line.set_ydata(y)  # update the data

        fig.canvas.draw()                         # redraw the canvas
    print 'FPS:' , 200/(time.time()-tstart)
    raise SystemExit

import gobject
print 'adding idle'
gobject.idle_add(animate)
print 'showing'
plt.show()

