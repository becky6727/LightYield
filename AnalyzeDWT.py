import os, sys, time
import numpy
import ROOT
import argparse
from scipy.signal import argrelmin
import re

#options
Parser = argparse.ArgumentParser(description = 'options')

Parser.add_argument('-i',
                    dest = 'FileIN',
                    default = None,
                    type = str,
                    help = 'input file')

Parser.add_argument('-o',
                    dest = 'FileOUT',
                    default = None,
                    type = str,
                    help = 'output file')

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
FileOUT = args.FileOUT
WaveID = args.WaveID
NofFilter = args.NofFilter
isFilter = args.isFilter

if(FileIN is None):
    print 'please select input file with option -i'
    sys.exit()
    pass

fin = open(FileIN)

#time array for graph
SamplingRate = 3.2e+9 #3.2 GS/s
dt = (1.0/SamplingRate)* 1.0e9 #sec -> nsec

dtArray = numpy.array([i* dt for i in xrange(1025)])

#variables for Discrete Wavelet Transformation
ScalePower = numpy.zeros(1024, dtype = float)

if(FileOUT is None):
    fTree = ROOT.TFile('hoge.root', 'RECREATE')
else:
    fTree = ROOT.TFile(FileOUT, 'RECREATE')
    pass

tr = ROOT.TTree('tr', 'tree of ADC')

tr.Branch('ScalePower', ScalePower, 'ScalePower[1025]/D')

#variables for loop
StartTime = 0.0
Time = 0.0

Pattern = '(\d{2})h(\d{2})m(\d{2})s,(\d{3}).(\d{3}).(\d{3})ns'
Compile = re.compile(Pattern)

DayCount = 0.0
DateTimeBefore = 0

DateToTime = numpy.array([3600.0, 60.0, 1.0, 1.0e-3, 1.0e-6, 1.0e-9])

#number of data to be analyzed
N = 0

#-------- ShiftArray --------#
def ShiftArray(Scale):

    MinRange = Scale/2
    NofLoop = int(1024 - Scale)

    ShiftArray_Low = numpy.empty((NofLoop, 1024))
    ShiftArray_High = numpy.empty((NofLoop, 1024))

    for b in xrange(NofLoop):

        tmp1 = [1.0/numpy.sqrt(Scale) if (i >= b and i < b + MinRange) else 0 for i in xrange(1024)]
        tmp2 = [1.0/numpy.sqrt(Scale) if (i >= b + MinRange and i < b + Scale) else 0 for i in xrange(1024)]

        ShiftArray_Low[b] = tmp1
        ShiftArray_High[b] = tmp2
    
        pass

    return ShiftArray_Low, ShiftArray_High

#-------- DWT -----------#
def DWT_Haar(Shift_Low, Shift_High, Array):
    DWT = numpy.dot(Shift_Low, Array) - numpy.dot(Shift_High, Array)
    return numpy.array(DWT)

#------- Analysis part ------------#
isDetect = False

for line in (fin):

    line = line.rstrip()
    line = line.split(' ')

    isWave = False
    
    #get time
    if(line[1] == 'UnixTime'):

        DateTime = Compile.findall(line[26])
        DateTime = numpy.int64(DateTime[0])
        
        if(DateTime[0] - DateTimeBefore < 0):
            DayCount = DayCount + 1.0
            pass
        
        CurrentTime = 24.0* 60.0* 60.0* DayCount + numpy.sum(DateToTime* DateTime)
                
        if(StartTime > 0.0):
            Time = CurrentTime - StartTime
        else:
            Time = StartTime
            StartTime = CurrentTime
            pass
        
        DateTimeBefore = DateTime[0]
        
        pass

    #get waveform raw data
    if(len(line) > 100):
        WaveArray = numpy.float64(line)
        FWaveArray = WaveArray
        isWave = True
        N += 1
        pass
        
    if(not(isWave)):
        continue

    if(N == WaveID):
        isDetect = True
    else:
        continue

    #noise event rejection
    if(len(numpy.where(WaveArray > 0.01)[0]) > 0):
        continue

    #Discrete Wavelet Transformation
    for a in xrange(1, 1024):
        Low, High = ShiftArray(a)
        DWT = DWT_Haar(Low, High, WaveArray)
        ScalePower[a] = (1.0/(1024.0 - a))* numpy.sum(numpy.square(DWT))
        pass
    
    tr.Fill()

    if(isDetect):
        break
    
    pass

fTree.Write()
fTree.Close()
