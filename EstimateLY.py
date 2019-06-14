import os, sys, time
import numpy
import ROOT

FileEm = './Data/PPO_1.5gL_Em_300_600nm_20170613.txt'
FileABS = './Data/Transparency_ABS.txt'
FileSDS = './Data/Transparency_SDS.txt'

#check if files exist
if(not(os.path.exists(FileEm))):
    print 'No such a file: %s' %(FileEm)
    print 'please confirm the file path name'
    sys.exit()
    pass

if(not(os.path.exists(FileABS))):
    print 'No such a file: %s' %(FileABS)
    print 'please confirm the file path name'
    sys.exit()
    pass

if(not(os.path.exists(FileSDS))):
    print 'No such a file: %s' %(FileSDS)
    print 'please confirm the file path name'
    sys.exit()
    pass

#read data files
tmpEmArray = numpy.loadtxt(FileEm, skiprows = 18, unpack = True)
tmpABSArray = numpy.loadtxt(FileABS, skiprows = 1, unpack = True)
tmpSDSArray = numpy.loadtxt(FileSDS, skiprows = 1, unpack = True)

#array for wavelength
WaveArray = numpy.array([i/10.0 for i in xrange(3500, 5000, 1)])

#Transparency@9cm -> @1cm
tmpABSArray[1] = (1.0/100.0)* tmpABSArray[1]

for i in xrange(len(tmpABSArray[1])):
    if(tmpABSArray[1][i] > 0.0):
        tmpABSArray[1][i] = 100.0* tmpABSArray[1][i]**(1./9.)
    else:
        tmpABSArray[1][i] = 0.0
        pass
    pass

tmpSDSArray[1] = (1.0/100.0)* tmpSDSArray[1]

for i in xrange(len(tmpSDSArray[1])):
    if(tmpSDSArray[1][i] > 0.0):
        tmpSDSArray[1][i] = 100.0* tmpSDSArray[1][i]**(1./9.)
    else:
        tmpSDSArray[1][i] = 0.0
        pass
    pass

#interpolation
EmArray = numpy.interp(WaveArray, tmpEmArray[0], tmpEmArray[1])
ABSArray = numpy.interp(WaveArray, tmpABSArray[0], tmpABSArray[1])
SDSArray = numpy.interp(WaveArray, tmpSDSArray[0], tmpSDSArray[1])

SumABS = numpy.sum(EmArray* ABSArray)
SumSDS = numpy.sum(EmArray* SDSArray)

R_LY = SumSDS/SumABS

print 'Estimator of LY(LAS) = %.5f' %(SumABS)
print 'Estimator of LY(SDS) = %.5f' %(SumSDS)
print 'Ratio of LY(SDS/LAS) = %.5f' %(R_LY)

#draw graphs
#set canvas
c1 = ROOT.TCanvas('c1', 'c1', 0, 0, 1067, 750)

c1.SetFillColor(0)
c1.SetGridx()
c1.SetGridy()
#c1.SetLogy()

MinWave = WaveArray[0]
MaxWave = WaveArray[-1]

MinY = 0.0
MaxY = 110.0

#normalize emission spec
EmArray = 100.0* (EmArray/numpy.max(EmArray))

#emission spec
gEm = ROOT.TGraph(len(WaveArray), WaveArray, EmArray)

gEm.SetTitle('Emission Spec. from PPO and Transparency of ABS/SDS')
gEm.GetXaxis().SetTitle('Wavelength [nm]')
gEm.GetXaxis().SetTitleFont(132)
gEm.GetXaxis().SetTitleOffset(1.1)
gEm.GetXaxis().SetLabelFont(132)
gEm.GetYaxis().SetTitle('a.u.')
gEm.GetYaxis().SetTitleFont(132)
gEm.GetYaxis().SetTitleOffset(0.8)
gEm.GetYaxis().SetLabelFont(132)
gEm.GetXaxis().SetLimits(MinWave, MaxWave)
gEm.SetMinimum(MinY)
gEm.SetMaximum(MaxY)

gEm.SetMarkerColor(2)
gEm.SetMarkerStyle(8)
gEm.SetMarkerSize(.6)
gEm.SetLineColor(2)
gEm.SetLineWidth(3)

gEm.Draw('apl')

#transparency
gABS = ROOT.TGraph(len(WaveArray), WaveArray, ABSArray)

gABS.SetMarkerColor(4)
gABS.SetMarkerStyle(8)
gABS.SetMarkerSize(.6)
gABS.SetLineColor(4)
gABS.SetLineWidth(3)

gABS.Draw('plsame')

gSDS = ROOT.TGraph(len(WaveArray), WaveArray, SDSArray)

gSDS.SetMarkerColor(6)
gSDS.SetMarkerStyle(8)
gSDS.SetMarkerSize(.6)
gSDS.SetLineColor(6)
gSDS.SetLineWidth(3)

gSDS.Draw('plsame')

c1.Update()
