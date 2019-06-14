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

Parser.add_argument('-NFilter',
                    dest = 'NofFilter',
                    default = 10,
                    type = int,
                    help = 'order of filter')

Parser.add_argument('-Filter',
                    action = 'store_true',
                    dest = 'isFilter',
                    help = 'filtering or not')

Parser.add_argument('-Test',
                    action = 'store_true',
                    dest = 'isTest',
                    help = 'test mode')

args = Parser.parse_args()

FileIN = args.FileIN
FileOUT = args.FileOUT
NofFilter = args.NofFilter
isFilter = args.isFilter
isTest = args.isTest

if(FileIN is None):
    print 'please select input file with option -i'
    sys.exit()
    pass

fin = open(FileIN)

#impedance
R_imp = 50.0

#time array for graph
SamplingRate = 3.2e+9 #3.2 GS/s
dt = (1.0/SamplingRate)* 1.0e9 #sec -> nsec

dtArray = numpy.array([i* dt for i in xrange(1025)])

#peak search and analyze adc, fill tree
ADC = numpy.zeros(1, dtype = float)
Pedestal = numpy.zeros(1, dtype = float)
TimeStamp = numpy.zeros(1, dtype = float)
DecayT = numpy.zeros(1, dtype = float)

#variables for Pulse Shape Discrimination
Tail = numpy.zeros(1, dtype = float)
Ratio = numpy.zeros(1, dtype = float)
PeakHeight = numpy.zeros(1, dtype = float)
AmpSample = numpy.zeros(1, dtype = float)
Power1 = numpy.zeros(1, dtype = float)
Power2 = numpy.zeros(1, dtype = float)

if(isTest):
    fTree = ROOT.TFile('test.root', 'RECREATE')
else:
    if(FileOUT is None):
        fTree = ROOT.TFile('hoge.root', 'RECREATE')
    else:
        fTree = ROOT.TFile(FileOUT, 'RECREATE')
        pass
    pass

tr = ROOT.TTree('tr', 'tree of ADC')

tr.Branch('ADC', ADC, 'ADC/D')
tr.Branch('Pedestal', Pedestal, 'Pedestal/D')
tr.Branch('TimeStamp', TimeStamp, 'TimeStamp/D')
tr.Branch('DecayT', DecayT, 'DecayT/D')
tr.Branch('Tail', Tail, 'Tail/D')
tr.Branch('Ratio', Ratio, 'Ratio/D')
tr.Branch('PeakHeight', PeakHeight, 'PeakHeight/D')
tr.Branch('AmpSample', AmpSample, 'AmpSample/D')
tr.Branch('Power1', Power1, 'Power1/D')
tr.Branch('Power2', Power2, 'Power2/D')

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

#range of Waveform
MinGate = 96
MaxGate = 288

#Amplitude of sample for PGA
#NSample = 160 #50nsec
#NSample = 128 #40nsec
NSample = 96 #30nsec

Scale1 = 32
Scale2 = 768

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

#filter for moving average
Filter = numpy.ones(NofFilter)/float(NofFilter)

#shifting arrays for DWT
ShiftArray1_Low, ShiftArray1_High = ShiftArray(Scale1)
ShiftArray2_Low, ShiftArray2_High = ShiftArray(Scale2)

#------- Analysis part ------------#
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

    if(isTest):
        if(N > 1000):
            break
        pass

    if(not(isWave)):
        continue

    #noise event rejection
    if(len(numpy.where(WaveArray > 0.01)[0]) > 0):
        continue
    
    #moving average for noise reduction if want
    if(isFilter):
        FWaveArray = numpy.convolve(WaveArray, Filter, mode = 'same')
        pass        
    
    #peak search
    Norder = 200
    PeakSearch = argrelmin(FWaveArray, order = Norder)[0]

    if(len(PeakSearch) <= 0):
        continue
    
    PeakArray = WaveArray[PeakSearch]
    PeakIndex = (numpy.where(WaveArray == numpy.min(PeakArray)))[0][0]
    
    #--------- analysis to get waveform information ---------# 
    #calc pedestal
    PedestalIndex = int(PeakIndex/2.0)
    PedestalArray = WaveArray[PedestalIndex - 10:PedestalIndex + 10]
    
    if(len(PedestalArray) > 0):
        Pedestal[0] = (numpy.mean(PedestalArray))
    else:
        Pedestal[0] = (numpy.mean(WaveArray[PedestalIndex:PedestalIndex + 10]))
        pass
    
    #calc ADC count after subtracting pedestal
    WaveArray = WaveArray - Pedestal
    
    if(PeakIndex >= MinGate):
        ADC[0] = (numpy.abs(numpy.sum(WaveArray[PeakIndex-MinGate:PeakIndex+MaxGate])))
    else:
        ADC[0] = (numpy.abs(numpy.sum(WaveArray[0:PeakIndex+MaxGate])))
        pass

    #convert ADC sum -> charge
    ADC[0] = ADC[0]* (dt/R_imp)* 1.0e+3 #nC -> pC
    
    #timestamp
    TimeStamp[0] = Time

    #graph for fitting
    gWave = ROOT.TGraph(len(dtArray), dtArray, WaveArray)
    
    #fitting waveform to get decay constant
    MinFit = dtArray[numpy.where(WaveArray < 0.50* WaveArray[PeakIndex])[0][-1]]
    MaxFit = MinFit + 50.0
    
    fFit = ROOT.TF1('fFit', '[0]*exp(-(x - %f)/[1]) + [2]' %(MinFit), MinFit, MaxFit)
    
    fFit.SetParameter(0, WaveArray[PeakIndex])
    fFit.SetParameter(1, 5.0)
    fFit.SetParameter(2, Pedestal[0])
    
    gWave.Fit('fFit', 'RQ0')
    
    #get analysis results
    DecayT[0] = fFit.GetParameter(1)

    #calc tail region and its ratio to ADC
    Tail[0] = (numpy.abs(numpy.sum(WaveArray[PeakIndex+MinGate:PeakIndex+MaxGate])))
    Ratio[0] = Tail[0]/ADC[0]
    
    #get peak hight of waveform
    PeakHeight[0] = WaveArray[PeakIndex]

    #amplitude of sample after peak
    if(PeakIndex + NSample < 1024):
        AmpSample[0] = FWaveArray[PeakIndex + NSample]
    else:
        AmpSample[0] = FWaveArray[-1]
        pass
    
    #Discrete Wavelet Transformation
    DWT1 = DWT_Haar(ShiftArray1_Low, ShiftArray1_High, WaveArray)
    DWT2 = DWT_Haar(ShiftArray2_Low, ShiftArray2_High, WaveArray)

    SumWT1 = numpy.sum(numpy.square(DWT1))
    SumWT2 = numpy.sum(numpy.square(DWT2))
    
    Power1[0] = (1.0/(1024.0 - Scale1))* SumWT1
    Power2[0] = (1.0/(1024.0 - Scale2))* SumWT2

    tr.Fill()
    
    if(N%10000 == 0):
        print 'Number of Data: %d is processed' %(N)
        pass
    
    pass

fTree.Write()
fTree.Close()
