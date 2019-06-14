import os, sys, time
import numpy
import ROOT
import argparse
from scipy.signal import argrelmin

#options
Parser = argparse.ArgumentParser(description = 'options')

Parser.add_argument('-i',
                    dest = 'FileIN',
                    default = None,
                    type = str,
                    help = 'input file')

Parser.add_argument('-ID',
                    dest = 'WaveID',
                    default = 0,
                    type = int,
                    help = 'id of waveform')

Parser.add_argument('-NFilter',
                    dest = 'NofFilter',
                    default = 10,
                    type = int,
                    help = 'order of filter')

Parser.add_argument('-Filter',
                    action = 'store_true',
                    dest = 'isFilter',
                    help = 'filtering or not')

args = Parser.parse_args()

FileIN = args.FileIN
WaveID = args.WaveID
NofFilter = args.NofFilter
isFilter = args.isFilter

if(FileIN == None):
    print 'please select input file with option -i'
    sys.exit()
    pass

fin = open(FileIN)

SamplingRate = 3.2e+9 #3.2 GS/s
dt = (1.0/SamplingRate)* 1.0e9 #sec -> nsec

N = 0

#read data and fill waveform into array
for line in (fin):

    line = line.rstrip()
    line = line.split(' ')
        
    if(len(line) > 100):
        line = numpy.float64(line)
        N += 1
        pass

    if(N > WaveID):
        break
    
    pass

WaveArray = numpy.array(line)
dtArray = numpy.array([i* dt for i in xrange(len(WaveArray))])

#moving average for noise reduction if want
if(isFilter):

    Filter = numpy.ones(NofFilter)/float(NofFilter)
    WaveArray = numpy.convolve(WaveArray, Filter, mode = 'same')

    pass

#peak search
Norder = 200
PeakSearch = argrelmin(WaveArray, order = Norder)[0]

if(len(PeakSearch) <= 0):
    print 'this waveform has no peak!: ID = %d' %(WaveID)
    sys.exit()
    pass
            
PeakArray = WaveArray[PeakSearch]
PeakIndex = (numpy.where(WaveArray == numpy.min(PeakArray)))[0][0]
dtPeakArray = dtArray[PeakSearch]

#calc pedestal
PedestalIndex = int(PeakIndex/2.0)
PedestalArray = WaveArray[PedestalIndex - 10:PedestalIndex + 10]
Pedestal = numpy.mean(PedestalArray)

#status message
print 'Waveform ID = %d' %(WaveID)

if(isFilter):
    print 'Moving averange for noise reduction: True'
    print 'order of filer = %d' %(NofFilter)
else:
    print 'Moving average for noise reduction: False'
    pass

#draw canvas
c1 = ROOT.TCanvas('c1', 'c1', 0, 0, 800, 750)

c1.SetFillColor(0)
c1.SetGridx()
c1.SetGridy()
#c1.SetLogy()
c1.Draw()

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetOptStat(0)

MinT = 0.0
MaxT = len(WaveArray)* dt

gWave = ROOT.TGraph(len(dtArray), dtArray, WaveArray)
gPeak = ROOT.TGraph(len(dtPeakArray), dtPeakArray, PeakArray)

gWave.SetTitle('Waveform')
gWave.GetXaxis().SetTitle('time [ns]')
gWave.GetXaxis().SetTitleFont(132)
gWave.GetXaxis().SetLabelFont(132)
gWave.GetXaxis().SetLimits(MinT, MaxT)
gWave.GetYaxis().SetTitle('Amplitude [mV]')
gWave.GetYaxis().SetTitleFont(132)
gWave.GetYaxis().SetTitleOffset(1.8)
gWave.GetYaxis().SetLabelFont(132)
gWave.GetYaxis().SetNoExponent(True)

gWave.SetLineColor(4)

gPeak.SetMarkerStyle(8)
gPeak.SetMarkerColor(2)
gPeak.SetMarkerSize(.8)

gWave.Draw('apl')
gPeak.Draw('psame')

#fitting with decay curve
#MinFit = dtArray[PeakIndex] + 5.0
MinFit = dtArray[numpy.where(WaveArray < 0.50* WaveArray[PeakIndex])[0][-1]]
MaxFit = MinFit + 50.0

fFit = ROOT.TF1('fFit', '[0]*exp(-(x - %f)/[1]) + [2]' %(MinFit), MinFit, MaxFit)

#initial value of fitting parameters
fFit.SetParameter(0, WaveArray[PeakIndex]) #constant
fFit.SetParameter(1, 5.0) #decay constant
fFit.SetParameter(2, Pedestal) #offset

gWave.Fit('fFit', 'R0')

MinRange = dtArray[PeakIndex]
MaxRange = MaxT

fExpo = ROOT.TF1('fExpo', '[0]*exp(-(x - %f)/[1]) + [2]' %(MinFit), MinRange, MaxRange)

fExpo.SetParameter(0, fFit.GetParameter(0)) #constant
fExpo.SetParameter(1, fFit.GetParameter(1)) #decay constant
fExpo.SetParameter(2, fFit.GetParameter(2)) #offset

fExpo.SetLineColor(2)
fExpo.SetLineStyle(2)
fExpo.SetLineWidth(3)

#fExpo.Draw('same')

c1.Update()
