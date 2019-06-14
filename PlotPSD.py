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

parser.add_argument('-p',
                    action = 'store_true',
                    dest = 'isFigOut',
                    help = 'Figure file is created')

args = parser.parse_args()

FileIN = args.FileIN
isFigOut = args.isFigOut

if(len(FileIN) <= 0):
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

c1 = ROOT.TCanvas('c1', 'c1', 0, 0, 1200, 1000)

ROOT.gStyle.SetOptStat(0)

c1.SetFillColor(0)
#c1.SetGridx()
#c1.SetGridy()
#c1.SetLogy()
c1.Divide(2, 3)

#Tail-to-Peak charge ratio
Ncanvas = 1

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

MinTail = 0.0
MaxTail = 2.0
TailBin = 0.01
NofTailBin = int((MaxTail - MinTail)/TailBin)

MinRatio = 0.0
MaxRatio = 0.3
RatioBin = 0.003
NofRatioBin = int((MaxRatio - MinRatio)/RatioBin)

hRatiovsTail = []

for i in range(len(tr)):
    
    tmp = ROOT.TH2D('hRatiovsTail_%d' %(i), 'Ratio vs Tail',
                    NofRatioBin, MinRatio, MaxRatio,
                    NofTailBin, MinTail, MaxTail)
    
    tr[i].Draw('Tail:Ratio>>hRatiovsTail_%d' %(i), '', 'Q0')

    hRatiovsTail.append(tmp)

    pass

for i in range(len(hRatiovsTail)):
    
    hRatiovsTail[i].GetXaxis().SetTitle('Ratio of Tail to Total Pulse')
    hRatiovsTail[i].GetXaxis().SetTitleFont(132)
    hRatiovsTail[i].GetXaxis().SetTitleOffset(1.1)
    hRatiovsTail[i].GetXaxis().SetLabelFont(132)
    hRatiovsTail[i].GetYaxis().SetTitle('Tail')
    hRatiovsTail[i].GetYaxis().SetTitleFont(132)
    hRatiovsTail[i].GetYaxis().SetTitleOffset(1.3)
    hRatiovsTail[i].GetYaxis().SetLabelFont(132)

    hRatiovsTail[i].SetMarkerColor(i + 2)

    if(i != 0):
        hRatiovsTail[i].Draw('same')
    else:
        hRatiovsTail[i].Draw('')
        pass

    pass

#charge ratio
Ncanvas = 2

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

hRatio = []

for i in range(len(tr)):

    #metric
    tmp = ROOT.TH1D('hRatio_%d' %(i), 'Ratio of Tail to Total Pulse',
                    NofRatioBin, MinRatio, MaxRatio)
    
    tr[i].Draw('Ratio>>hRatio_%d' %(i), '', 'Q0')
    
    hRatio.append(tmp)
    
    pass

Xtxt = 0.20
Ytxt = (hRatio[0].GetMaximum())* 0.65
TxtMargin = 0.10* Ytxt

Latex = ROOT.TLatex()

for i in range(len(hRatio)):
    
    hRatio[i].GetXaxis().SetTitle('Ratio of Tail to Total Pulse')
    hRatio[i].GetXaxis().SetTitleFont(132)
    hRatio[i].GetXaxis().SetTitleOffset(1.1)
    hRatio[i].GetXaxis().SetLabelFont(132)
    hRatio[i].GetYaxis().SetTitle('events/bin')
    hRatio[i].GetYaxis().SetTitleFont(132)
    hRatio[i].GetYaxis().SetTitleOffset(1.3)
    hRatio[i].GetYaxis().SetLabelFont(132)
    hRatio[i].SetMaximum(1.3* (hRatio[i].GetMaximum()))
    
    hRatio[i].SetMarkerColor(i + 2)
    hRatio[i].SetMarkerStyle(i + 8)
    hRatio[i].SetMarkerSize(.6)
    hRatio[i].SetLineColor(i + 2)
    hRatio[i].SetLineWidth(3)

    if(i != 0):
        hRatio[i].Draw('histsame')
    else:
        hRatio[i].Draw('hist')
        pass

    #draw latex
    Latex.SetTextSize(.035)
    Latex.SetTextColor(i + 2)

    Latex.DrawLatex(Xtxt, Ytxt, FileIN[i])
    
    Ytxt = Ytxt - TxtMargin

    pass

#PeakHeight vs Amp_sample
Ncanvas = 3

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

MinPeak = 0.0
MaxPeak = 0.5
PeakBin = 0.001
NofPeakBin = int((MaxPeak - MinPeak)/PeakBin)

MinAmp = 0.0
MaxAmp = 0.02
AmpBin = 0.0001
NofAmpBin = int((MaxAmp - MinAmp)/AmpBin)

MinPeakRatio = 0.0
MaxPeakRatio = 20.0
PeakRatioBin = 0.20
NofPeakRatioBin = int((MaxPeakRatio - MinPeakRatio)/PeakRatioBin)

hPeakAmp = []

for i in range(len(tr)):

    #peak height
    tmp = ROOT.TH2D('hPeakAmp_%d' %(i), 'Peak Height vs Discrimination Amplitude',
                    NofPeakRatioBin, MinPeakRatio, MaxPeakRatio,
                    NofPeakBin, MinPeak, MaxPeak)
    #tmp = ROOT.TH2D('hPeakAmp_%d' %(i), 'Peak Height vs Discrimination Amplitude',
    #                NofAmpBin, MinAmp, MaxAmp,
    #                NofPeakBin, MinPeak, MaxPeak)
    
    tr[i].Draw('(-PeakHeight):((-PeakHeight)/(-AmpSample))>>hPeakAmp_%d' %(i), '', 'Q0')
    #tr[i].Draw('(-PeakHeight):(-AmpSample)>>hPeakAmp_%d' %(i), '', 'Q0')
    
    hPeakAmp.append(tmp)
    
    pass

for i in range(len(hPeakAmp)):
    
    hPeakAmp[i].GetXaxis().SetTitle('Ratio of Peak to Discimination Amplitude')
    hPeakAmp[i].GetXaxis().SetTitleFont(132)
    hPeakAmp[i].GetXaxis().SetTitleOffset(1.1)
    hPeakAmp[i].GetXaxis().SetLabelFont(132)
    hPeakAmp[i].GetYaxis().SetTitle('Peak Height [mV]')
    hPeakAmp[i].GetYaxis().SetTitleFont(132)
    hPeakAmp[i].GetYaxis().SetTitleOffset(1.3)
    hPeakAmp[i].GetYaxis().SetLabelFont(132)

    hPeakAmp[i].SetMarkerColor(i + 2)

    if(i != 0):
        hPeakAmp[i].Draw('same')
    else:
        hPeakAmp[i].Draw('')
        pass

    pass

#1-D distribution of Ratio(Peak Height vs Amplitude)
Ncanvas = 4

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

hPeak = []

for i in range(len(tr)):

    #peak height
    tmp = ROOT.TH1D('hPeak_%d' %(i), 'Ratio of Peak Height to Amplitude after 30 nsec',
                    NofPeakRatioBin, MinPeakRatio, MaxPeakRatio)
    
    tr[i].Draw('(-PeakHeight)/(-AmpSample)>>hPeak_%d' %(i), '', 'Q0')
    
    hPeak.append(tmp)
    
    pass

for i in range(len(hPeak)):
    
    hPeak[i].GetXaxis().SetTitle('Ratio of Peak to Discrimination Amplitude')
    hPeak[i].GetXaxis().SetTitleFont(132)
    hPeak[i].GetXaxis().SetTitleOffset(1.1)
    hPeak[i].GetXaxis().SetLabelFont(132)
    hPeak[i].GetYaxis().SetTitle('events/bin')
    hPeak[i].GetYaxis().SetTitleFont(132)
    hPeak[i].GetYaxis().SetTitleOffset(1.3)
    hPeak[i].GetYaxis().SetLabelFont(132)
    hPeak[i].SetMaximum(1.5* (hPeak[i].GetMaximum()))
    
    hPeak[i].SetMarkerColor(i + 2)
    hPeak[i].SetMarkerStyle(i + 8)
    hPeak[i].SetMarkerSize(.6)
    hPeak[i].SetLineColor(i + 2)
    hPeak[i].SetLineWidth(3)

    if(i != 0):
        hPeak[i].Draw('histsame')
    else:
        hPeak[i].Draw('hist')
        pass

    pass

#Discrete Wavelet Transform
Ncanvas = 5

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

MinPower1 = 0.0
MaxPower1 = 1.0e-2
Power1Bin = 1.0e-5
NofPower1Bin = int((MaxPower1 - MinPower1)/Power1Bin)

MinPower2 = 0.0
MaxPower2 = 8.0e-1
Power2Bin = 1.0e-3
NofPower2Bin = int((MaxPower2 - MinPower2)/Power2Bin)

MinMetric = 0.0
MaxMetric = 160.0
MetricBin = 1.0
NofMetricBin = int((MaxMetric - MinMetric)/MetricBin)

hPower = []

for i in range(len(tr)):
    
    #tmp = ROOT.TH2D('hPower_%d' %(i), 'Power1 vs Power1/Power2',
    #                NofPower1Bin, MinPower1, MaxPower1,
    #                NofPower2Bin, MinPower2, MaxPower2)
    tmp = ROOT.TH2D('hPower_%d' %(i), 'Power1 vs Power1/Power2',
                    NofMetricBin, MinMetric, MaxMetric,
                    NofPower1Bin, MinPower1, MaxPower1)
    
    #tr[i].Draw('Power2:Power1>>hPower_%d' %(i), '', 'Q0')
    tr[i].Draw('Power1:(Power2/Power1)>>hPower_%d' %(i), '', 'Q0')

    hPower.append(tmp)

    pass

for i in range(len(hPower)):
    
    hPower[i].GetXaxis().SetTitle('Power2/Power1')
    hPower[i].GetXaxis().SetTitleFont(132)
    hPower[i].GetXaxis().SetTitleOffset(1.1)
    hPower[i].GetXaxis().SetLabelFont(132)
    hPower[i].GetYaxis().SetTitle('Power1')
    hPower[i].GetYaxis().SetTitleFont(132)
    hPower[i].GetYaxis().SetTitleOffset(1.3)
    hPower[i].GetYaxis().SetLabelFont(132)

    hPower[i].SetMarkerColor(i + 2)

    if(i != 0):
        hPower[i].Draw('same')
    else:
        hPower[i].Draw('')
        pass

    pass

#1D distribution of Power2/Power1
Ncanvas = 6

c1.cd(Ncanvas)

c1.cd(Ncanvas).SetGridx()
c1.cd(Ncanvas).SetGridy()
#c1.cd(Ncanvas).SetLogy()

hMetric = []

for i in range(len(tr)):

    #metric
    tmp = ROOT.TH1D('hMetric_%d' %(i), 'Ratio of Power2 to Power1',
                    NofMetricBin, MinMetric, MaxMetric)
    
    tr[i].Draw('Power2/Power1>>hMetric_%d' %(i), '', 'Q0')
    
    hMetric.append(tmp)
    
    pass

for i in range(len(hMetric)):
    
    hMetric[i].GetXaxis().SetTitle('Discrimination value (Power2/Power1)')
    hMetric[i].GetXaxis().SetTitleFont(132)
    hMetric[i].GetXaxis().SetTitleOffset(1.1)
    hMetric[i].GetXaxis().SetLabelFont(132)
    hMetric[i].GetYaxis().SetTitle('events/bin')
    hMetric[i].GetYaxis().SetTitleFont(132)
    hMetric[i].GetYaxis().SetTitleOffset(1.3)
    hMetric[i].GetYaxis().SetLabelFont(132)
    hMetric[i].SetMaximum(1.3* (hMetric[i].GetMaximum()))
    
    hMetric[i].SetMarkerColor(i + 2)
    hMetric[i].SetMarkerStyle(i + 8)
    hMetric[i].SetMarkerSize(.6)
    hMetric[i].SetLineColor(i + 2)
    hMetric[i].SetLineWidth(3)

    if(i != 0):
        hMetric[i].Draw('histsame')
    else:
        hMetric[i].Draw('hist')
        pass

    pass

c1.Update()
