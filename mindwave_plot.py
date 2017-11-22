import NeuroPy
from time import sleep
from numpy import *
import matplotlib as mpl
mpl.use('TKagg')
import pylab as PP
from digipot import DigiPot
#PP.ion()

# set default fonts
font = { 'family' : 'serif', \
        'size' : '15' }
mpl.rc('font', **font)
mpl.rc('axes', labelweight = 'bold') # needed for bold axis labels in more recent version of matplotlib

trace_size = 2048
current_trace = trace_size*[0]
xvals = arange(trace_size)

current_spectrum = 8*[1]
specx = arange(8)

fig,axs = PP.subplots(1,2,figsize=(12,4))
ax = axs[0]
ax2 = axs[1]

ax.set_ylim([-1024,1024])
PP.show(block=False)
background = fig.canvas.copy_from_bbox(ax.bbox) # cache the background
line1, = ax.plot(xvals,current_trace,'k-')
hist1 = ax2.bar(specx,current_spectrum,color='k',width=0.75)
background2 = fig.canvas.copy_from_bbox(ax2.bbox) # cache the background

#quit()
yscale_reset = 1024 


mypot = DigiPot.DigiPot()

# open and close the mindwave once; try to get around failed open
# on first try bug
mindwave =NeuroPy.NeuroPy("/dev/rfcomm0") # initialize the mindwave object
del(mindwave)
mindwave =NeuroPy.NeuroPy("/dev/rfcomm0") # initialize the mindwave object

redraw=False

def update_plot(trace):
    global redraw
    try:
        line1.set_ydata(trace)
    except:
        pass
    redraw = True

def update_bar(vals):
    hsum= sum(vals)
    [r.set_height(2*v/hsum) for r,v in zip(hist1,vals)]
    redraw = True

def midgamma_callback(value):
    vals = [mindwave.delta,mindwave.theta,mindwave.lowAlpha,mindwave.highAlpha,mindwave.lowBeta,mindwave.highBeta,mindwave.lowGamma, mindwave.midGamma]
    update_bar(vals)
            


def rawValue_callback(value):
    global current_trace
    if abs(value) < 8092:
        current_trace.append(value)
        current_trace.pop(0)
        update_plot(current_trace)

def meditation_callback(value):
    invalue = max([0,(value - 50)/50])**2
    mypot.set_wiper(invalue)
    # scale the meditation quantity from 0 to 1
    

mindwave.setCallBack("rawValue",rawValue_callback)
mindwave.setCallBack("midGamma",midgamma_callback)
mindwave.setCallBack("attention",meditation_callback)


#call start method
mindwave.start()

while True:

    fig.canvas.restore_region(background)    # restore background
    fig.canvas.restore_region(background2)    # restore background
    ax.draw_artist(line1)                   # redraw just the points
    [ax.draw_artist(r) for r in hist1]                   # redraw just the points
    fig.canvas.blit(ax.bbox)                # fill in the axes rectangle
    fig.canvas.blit(ax2.bbox)                # fill in the axes rectangle
    fig.canvas.flush_events()

    #fig.canvas.draw()
    if redraw:
        redraw=False
    try:
        #sleep(0.1)
        pass
    except KeyboardInterrupt:
        break
