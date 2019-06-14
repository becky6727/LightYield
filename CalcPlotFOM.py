import os, sys, time
import ROOT
import numpy
import argparse

parser = argparse.ArgumentParser(description = 'options')

parser.add_argument('-i',
                    type = str,
                    dest = 'FileIN',
                    nargs = '+',
                    help = 'input root files')

parser.add_argument('-bg',
                    type = str,
                    dest = 'FileBG',
                    nargs = 1,
                    help = 'input root files, bg')

parser.add_argument('-p',
                    action = 'store_true',
                    dest = 'isFigOut',
                    help = 'Figure file is created')

args = parser.parse_args()

FileIN = args.FileIN
isFigOut = args.isFigOut
FileBG = args.FileBG

if(len(FileIN) <= 0):
    sys.exit()
    pass

if(len(FileBG) <= 0):
    sys.exit()
    pass

tr = []
RFile = []

for i in range(len(FileIN)):
    tmp = ROOT.TFile(FileIN[i])
    RFile.append(tmp)
    pass

for i in range(len(RFile)):
    tmp = RFile[i].Get('tr')
    tr.append(tmp)
    pass

#background file
RFileBG = ROOT.TFile(FileBG[0])
trBG = RFileBG.Get('tr')

#----------------------------------#
####### calc Figure of Merit #######
#----------------------------------#

#set histgrams
#Ratio of tail to total
MinRatio = 0.0
MaxRatio = 0.3
RatioBin = 0.003
NofRatioBin = int((MaxRatio - MinRatio)/RatioBin)

hRatio = []

for i in range(len(tr)):

    #metric
    tmp = ROOT.TH1D('hRatio_%d' %(i), 'Ratio of Tail to Total Pulse',
                    NofRatioBin, MinRatio, MaxRatio)
    
    tr[i].Draw('Ratio>>hRatio_%d' %(i), '', 'Q0')
    
    hRatio.append(tmp)
    
    pass

hRatioBG = ROOT.TH1D('hRatioBG', '', NofRatioBin, MinRatio, MaxRatio)
trBG.Draw('Ratio>>hRatioBG', '', 'Q0')

#PGA
MinPeakRatio = 0.0
MaxPeakRatio = 20.0
PeakRatioBin = 0.10
NofPeakRatioBin = int((MaxPeakRatio - MinPeakRatio)/PeakRatioBin)

hPeak = []

for i in range(len(tr)):

    #peak height
    tmp = ROOT.TH1D('hPeak_%d' %(i), 'Ratio of Peak Height to Amplitude after 30 nsec',
                    NofPeakRatioBin, MinPeakRatio, MaxPeakRatio)
    
    tr[i].Draw('(-PeakHeight)/(-AmpSample)>>hPeak_%d' %(i), '', 'Q0')
    
    hPeak.append(tmp)
    
    pass

hPeakBG = ROOT.TH1D('hPeakBG', '', NofPeakRatioBin, MinPeakRatio, MaxPeakRatio)
trBG.Draw('(-PeakHeight)/(-AmpSample)>>hPeakBG', '', 'Q0')

#DWT
MinMetric = 0.0
MaxMetric = 160.0
MetricBin = 1.0
NofMetricBin = int((MaxMetric - MinMetric)/MetricBin)

hMetric = []

for i in range(len(tr)):

    #metric
    tmp = ROOT.TH1D('hMetric_%d' %(i), 'Ratio of Power2 to Power1',
                    NofMetricBin, MinMetric, MaxMetric)
    
    tr[i].Draw('(Power2/Power1)>>hMetric_%d' %(i), '', 'Q0')
    
    hMetric.append(tmp)
    
    pass

hMetricBG = ROOT.TH1D('hMetricBG', '', NofMetricBin, MinMetric, MaxMetric)
trBG.Draw('(Power2/Power1)>>hMetricBG', '', 'Q0')

#analyze histgrams, and then get FOM
Sig = 0.0
Noise = 0.0

RatioArray = numpy.zeros(NofRatioBin - 1, dtype = float)
FOM_Ratio = [[] for i in xrange(len(hRatio))]
tmp_Ratio = numpy.zeros(NofRatioBin - 1, dtype = float)

for i in xrange(len(hRatio)):

    for j in xrange(NofRatioBin - 1):

        Sig = hRatio[i].Integral(j + 1, NofRatioBin)
        Noise = hRatioBG.Integral(j + 1, NofRatioBin)

        if(Noise > 0.0):
            tmp_Ratio[j] = Sig/numpy.sqrt(Noise) 
        else:
            tmp_Ratio[j] = 0.0
            pass

        RatioArray[j] = MinRatio + (j + 1)* RatioBin
        
        #for debug
        #print MinRatio + (j + 1)* RatioBin, Sig, Noise, FOM_Ratio[j]
        
        pass

    RatioArray = numpy.array(RatioArray)
    FOM_Ratio[i] = tmp_Ratio
    
    pass

PeakArray = numpy.zeros(NofPeakRatioBin - 1, dtype = float)
FOM_PGA = [[] for i in xrange(len(hPeak))]
tmp_PGA = numpy.zeros(NofPeakRatioBin - 1, dtype = float)

for i in xrange(len(hPeak)):

    for j in xrange(NofPeakRatioBin - 1):

        Sig = hPeak[i].Integral(j + 1, NofPeakRatioBin)
        Noise = hPeakBG.Integral(j + 1, NofPeakRatioBin)

        if(Noise > 0.0):
            tmp_PGA[j] = Sig/numpy.sqrt(Noise) 
        else:
            tmp_PGA[j] = 0.0
            pass
        
        PeakArray[j] = MinPeakRatio + (j + 1)* PeakRatioBin
            
        #for debug
        #print MinPeakRatio + (j + 1)* PeakRatioBin, Sig, Noise, FOM_PGA[j]
        
        pass

    PeakArray = numpy.array(PeakArray)
    FOM_PGA[i] = tmp_PGA
    
    pass

MetricArray = numpy.zeros(NofMetricBin - 1, dtype = float)
FOM_DWT = [[] for i in xrange(len(hMetric))]
tmp_DWT = numpy.zeros(NofMetricBin - 1, dtype = float)

for i in xrange(len(hMetric)):

    for j in xrange(NofMetricBin - 1):

        Sig = hMetric[i].Integral(j + 1, NofMetricBin)
        Noise = hMetricBG.Integral(j + 1, NofMetricBin)

        if(Noise > 0.0):
            tmp_DWT[j] = Sig/numpy.sqrt(Noise) 
        else:
            tmp_DWT[j] = 0.0
            pass

        MetricArray[j] = MinMetric + (j + 1)* MetricBin

        #for debug
        #print MinMetric + (j + 1)* MetricBin, Sig, Noise, FOM_DWT[j]
        
        pass
    
    MetricArray = numpy.array(MetricArray)
    FOM_DWT[i] = tmp_DWT
    
    pass

#------------------------#
######## draw FOM ########
#------------------------#
c1 = ROOT.TCanvas('c1', 'c1', 0, 0, 900, 1000)

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTitleFont(132, '')
ROOT.gStyle.SetTitleFont(132, 'XYZ')
ROOT.gStyle.SetLabelFont(132, '')
ROOT.gStyle.SetLabelFont(132, 'XYZ')

c1.SetFillColor(0)
#c1.SetGridx()
#c1.SetGridy()
#c1.SetLogy()
c1.Divide(1, 3)
#Tail-to-Peak charge ratio
Ncanvas = 1

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

#variables
MinFOM = 0.0
MaxFOM = 400.0

gFOM_Ratio = ROOT.TGraph(len(RatioArray), RatioArray, FOM_Ratio[0])

gFOM_Ratio.SetTitle('Figure of Merit, Ratio')
gFOM_Ratio.GetXaxis().SetTitle('Ratio of Tail to Total Pulse')
gFOM_Ratio.GetXaxis().SetTitleFont(132)
gFOM_Ratio.GetXaxis().SetTitleOffset(1.1)
gFOM_Ratio.GetXaxis().SetLabelFont(132)
gFOM_Ratio.GetYaxis().SetTitle('FOM')
gFOM_Ratio.GetYaxis().SetTitleFont(132)
gFOM_Ratio.GetYaxis().SetTitleOffset(0.5)
gFOM_Ratio.GetYaxis().SetLabelFont(132)
gFOM_Ratio.GetXaxis().SetLimits(MinRatio, MaxRatio)
gFOM_Ratio.SetMinimum(MinFOM)
gFOM_Ratio.SetMaximum(MaxFOM)

gFOM_Ratio.SetMarkerColor(2)
gFOM_Ratio.SetMarkerStyle(8)
gFOM_Ratio.SetMarkerSize(.6)
gFOM_Ratio.SetLineColor(2)
gFOM_Ratio.SetLineWidth(2)

gFOM_Ratio.Draw('apl')

#draw latex
Xtxt = 0.20
Ytxt = MaxFOM* 0.65
TxtMargin = 0.10* Ytxt

Latex = ROOT.TLatex()

Latex.SetTextSize(.050)
Latex.SetTextColor(2)

Latex.DrawLatex(Xtxt, Ytxt, FileIN[0])

Latex.SetTextColor(3)
Latex.DrawLatex(Xtxt, Ytxt - TxtMargin, FileBG[0])

#PGA
Ncanvas = 2

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

gFOM_PGA = ROOT.TGraph(len(PeakArray), PeakArray, FOM_PGA[0])

gFOM_PGA.SetTitle('Figure of Merit, PGA')
gFOM_PGA.GetXaxis().SetTitle('Ratio of Peak to Discrimination Amplitude')
gFOM_PGA.GetXaxis().SetTitleFont(132)
gFOM_PGA.GetXaxis().SetTitleOffset(1.1)
gFOM_PGA.GetXaxis().SetLabelFont(132)
gFOM_PGA.GetYaxis().SetTitle('FOM')
gFOM_PGA.GetYaxis().SetTitleFont(132)
gFOM_PGA.GetYaxis().SetTitleOffset(0.5)
gFOM_PGA.GetYaxis().SetLabelFont(132)
gFOM_PGA.GetXaxis().SetLimits(MinPeakRatio, MaxPeakRatio)
gFOM_PGA.SetMinimum(MinFOM)
gFOM_PGA.SetMaximum(MaxFOM)

gFOM_PGA.SetMarkerColor(2)
gFOM_PGA.SetMarkerStyle(8)
gFOM_PGA.SetMarkerSize(.6)
gFOM_PGA.SetLineColor(2)
gFOM_PGA.SetLineWidth(2)

gFOM_PGA.Draw('apl')

#DWT
Ncanvas = 3

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

gFOM_DWT = ROOT.TGraph(len(MetricArray), MetricArray, FOM_DWT[0])

gFOM_DWT.SetTitle('Figure of Merit, DWT')
gFOM_DWT.GetXaxis().SetTitle('Discimination Value (Power2/Power1)')
gFOM_DWT.GetXaxis().SetTitleFont(132)
gFOM_DWT.GetXaxis().SetTitleOffset(1.1)
gFOM_DWT.GetXaxis().SetLabelFont(132)
gFOM_DWT.GetYaxis().SetTitle('FOM')
gFOM_DWT.GetYaxis().SetTitleFont(132)
gFOM_DWT.GetYaxis().SetTitleOffset(0.5)
gFOM_DWT.GetYaxis().SetLabelFont(132)
gFOM_DWT.GetXaxis().SetLimits(MinMetric, MaxMetric)
gFOM_DWT.SetMinimum(MinFOM)
gFOM_DWT.SetMaximum(MaxFOM)

gFOM_DWT.SetMarkerColor(2)
gFOM_DWT.SetMarkerStyle(8)
gFOM_DWT.SetMarkerSize(.6)
gFOM_DWT.SetLineColor(2)
gFOM_DWT.SetLineWidth(2)

gFOM_DWT.Draw('apl')

c1.Update()

#-----------------------------#
######## show results #########
#-----------------------------#
RatioCut = RatioArray[numpy.where(FOM_Ratio[0] == numpy.max(FOM_Ratio[0]))]
MaxFOM_Ratio = numpy.max(FOM_Ratio[0])

PeakCut = PeakArray[numpy.where(FOM_PGA[0] == numpy.max(FOM_PGA[0]))]
MaxFOM_PGA = numpy.max(FOM_PGA[0])

print PeakCut

MetricCut = MetricArray[numpy.where(FOM_DWT[0] == numpy.max(FOM_DWT[0]))]
MaxFOM_DWT = numpy.max(FOM_DWT[0])

print 'Max of FOM(Ratio) = %3.3f at Ratio = %1.4f' %(MaxFOM_Ratio, RatioCut)
print 'Max of FOM(PGA) = %3.3f at Ratio = %1.4f' %(MaxFOM_PGA, PeakCut[0])
print 'Max of FOM(DWT) = %3.3f at Ratio = %1.4f' %(MaxFOM_DWT, MetricCut)
