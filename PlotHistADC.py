import os, sys, time
import ROOT
import numpy
import argparse
import re

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

parser.add_argument('-cut',
                    action = 'store_true',
                    dest = 'isCut',
                    help = 'draw histgram with selection criteria')

parser.add_argument('-norm',
                    action = 'store_true',
                    dest = 'isNorm',
                    help = 'draw histgram with normalization')

parser.add_argument('-fit',
                    #action = 'store_true',
                    dest = 'FitRange',
                    nargs = 2,
                    default = [],
                    type = float,
                    #dest = 'isFit',
                    help = 'set fitting range')

args = parser.parse_args()

FileIN = args.FileIN
isFigOut = args.isFigOut
isCut = args.isCut
isNorm = args.isNorm
FitRange = args.FitRange

if(len(FileIN) <= 0):
    sys.exit()
    pass

isFit = False

if(len(FitRange) > 0):
    isFit = True
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

SourceType = []

for i in range(len(FileIN)):
    tmp = re.findall('./(.*)/(.*)/(.*)_(.*).root', FileIN[i])
    SourceType.append(tmp[0][-1])
    pass

c1 = ROOT.TCanvas('c1', 'c1', 0, 0, 1067, 750)

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTitleFont(132, '')
ROOT.gStyle.SetTitleFont(132, 'XYZ')
ROOT.gStyle.SetLabelFont(132, '')
ROOT.gStyle.SetLabelFont(132, 'XYZ')

c1.SetFillColor(0)
c1.SetGridx()
c1.SetGridy()
#c1.SetLogy()

MinADC = 0.0
#MaxADC = numpy.array([tr[i].GetMaximum('ADC') for i in range(len(tr))]).min()
MaxADC = 200.0

ADCBinWidth = 0.2
NofADCBin = (int)((MaxADC - MinADC)/ADCBinWidth)

hADC = []
hADC_Cut = []

Duaration = []

#selection condition
#CutValue = [0.0, 56.0] #PC1%, Co
#CutValue = [4.8, 0.0] #PC1%, Cs
#CutValue = [0.0, 58.0] #PC5%, Co
#CutValue = [6.2, 0.0] #PC5%, Cs
CutValue = [6.8, 58.0] #PC10%, Co
#CutValue = [0.0, 49.0] #PC10%, Cs
#CutValue = [0.0, 60.0] #PC10%, Na
#CutValue = [0.0, 65.0] #PC20%, Co
#CutValue = [0.0, 53.0] #PC20%, Cs
#CutValue = [0.0, 62.0] #PC20%, Na
#CutValue = [0.0, 67.0] #LAS, PC10%, Co
#CutValue = [16.9, 0.0] #LAS, PC10%, Cs
#CutValue = [0.0, 65.0] #LAS, PC10%, Na

#CutADC = ROOT.TCut('ADC > 1.5') #for calc noise rate
CutRatio = ROOT.TCut('Ratio > 0.003')
CutPGA = ROOT.TCut('(-PeakHeight)/(-AmpSample) > %2.2f' %(CutValue[0]))
CutDWT = ROOT.TCut('Power2/Power1 > %2.2f' %(CutValue[1]))

#fot fitting function        
if(isFit):
    MinFit = numpy.min(numpy.array(FitRange))
    MaxFit = numpy.max(numpy.array(FitRange))
    pass

fFit = [ROOT.TF1() for i in xrange(len(tr))]
fErfc = [ROOT.TF1() for i in xrange(len(tr))]

for i in range(len(tr)):

    #ADC
    tmp = ROOT.TH1D('hADC_%d' %(i), 'ADC Total', NofADCBin, MinADC, MaxADC)
    tmp_Cut = ROOT.TH1D('hADC_%d_Cut' %(i), 'ADC Total', NofADCBin, MinADC, MaxADC)

    tr[i].Draw('ADC>>hADC_%d' %(i), '', 'Q0')
    #tr[i].Draw('ADC>>hADC_%d_Cut' %(i), CutDWT, 'Q0')
    tr[i].Draw('ADC>>hADC_%d_Cut' %(i), CutPGA, 'Q0')
    
    hADC.append(tmp)
    hADC_Cut.append(tmp_Cut)

    #timestamp
    Time1 = tr[i].GetMinimum('TimeStamp')
    Time2 = tr[i].GetMaximum('TimeStamp')
    Duaration.append(Time2 - Time1)

    pass

Xtxt = MaxADC* 0.65
Ytxt = 0.50* (hADC[0].GetMaximum())
TxtMargin = 0.05* (hADC[0].GetMaximum())

for i in range(len(hADC)):
    
    hADC[i].GetXaxis().SetTitle('Charge [pC]')
    hADC[i].GetXaxis().SetTitleFont(132)
    hADC[i].GetXaxis().SetTitleOffset(1.1)
    hADC[i].GetXaxis().SetLabelFont(132)
    hADC[i].GetYaxis().SetTitle('counts/%2.2f pC' %(ADCBinWidth))
    #hADC[i].GetYaxis().SetTitle('events/bin/sec')
    hADC[i].GetYaxis().SetTitleFont(132)
    hADC[i].GetYaxis().SetTitleOffset(1.3)
    hADC[i].GetYaxis().SetLabelFont(132)
        
    hADC[i].SetLineColor(i + 2)
    hADC[i].SetLineWidth(3)
    #hADC[i].SetFillColor(i + 2)
    #hADC[i].SetFillStyle(3002)

    hADC_Cut[i].SetLineColor(4)
    hADC_Cut[i].SetLineWidth(3)
    hADC_Cut[i].SetFillColor(4)
    hADC_Cut[i].SetFillStyle(3002)
    
    #calc event rate
    print '%s:' %(FileIN[i])
    print 'Duaration time = %.3f sec' %(Duaration[i])
    print 'Event rate = %.3f Hz' %(hADC[i].GetEntries()/Duaration[i])
    print 'Event rate = %.3f Hz after noise reduction' %(hADC_Cut[i].GetEntries()/Duaration[i])

    #normalized by total events
    Norm = hADC[i].Integral()

    if(isNorm):
        hADC[i].Sumw2()
        hADC[i].Scale(1.0/Norm)
    
        #hADC_Cut[i].Sumw2()
        #hADC_Cut[i].Scale(1.0/Norm)

        pass

    print 'Number of events = %d' %(Norm)
    
    if(i != 0):
        hADC[i].Draw('histsame')
    else:
        hADC[i].Draw('hist')
        pass
    
    #selection
    if(isCut):
        hADC_Cut[i].Draw('histsame')
        pass

    #fitting
    if(isFit):
        
        fFit[i] = ROOT.TF1('fFit_%d' %(i), '[0]* TMath::Erf(-(x - [1])/[2]) + [3]', MinFit, MaxFit)
        
        #initial values of fitting parameters
        Index = int((((MaxFit - MinFit)/2.0) - MinADC)/ADCBinWidth)
        Par0 = 0.5* hADC[i].GetMaximum()
        Par1 = (MaxFit - MinFit)/2.0
        Par2 = 1.0e+2
        #Par3 = hADC[i].GetBinContent(Index)
        Par3 = Par0/2.0
        
        fFit[i].SetParameter(0, Par0)
        fFit[i].SetParameter(1, Par1)
        fFit[i].SetParameter(2, Par2)
        fFit[i].SetParameter(3, Par3)

        if(isCut):
            hADC_Cut[i].Fit('fFit_%d' %(i), 'R0')
        else:
            hADC[i].Fit('fFit_%d' %(i), 'R0')
            pass
        
        #draw fitting function
        fErfc[i] = ROOT.TF1('fErfc_%d' %(i), '[0]* TMath::Erf(-(x - [1])/[2]) + [3]', MinADC, MaxADC)
        
        fErfc[i].SetParameter(0, fFit[i].GetParameter(0))
        fErfc[i].SetParameter(1, fFit[i].GetParameter(1))
        fErfc[i].SetParameter(2, fFit[i].GetParameter(2))
        fErfc[i].SetParameter(3, fFit[i].GetParameter(3))

        fErfc[i].SetLineColor(1)
        fErfc[i].SetLineWidth(3)
        fErfc[i].SetLineStyle(2)
    
        fErfc[i].Draw('lsame')

        print 'Chi2 = %3.2f, NDF = %d' %(fFit[i].GetChisquare(), fFit[i].GetNDF())
        print 'Chi2/NDF = %3.4f' %(fFit[i].GetChisquare()/fFit[i].GetNDF())
        
        pass
    
    #draw latex
    Latex = ROOT.TLatex()

    Latex.SetTextSize(.025)
    Latex.SetTextColor(i + 2)

    #Latex.DrawLatex(Xtxt, Ytxt, FileIN[i])
    
    #Ytxt = Ytxt* (numpy.exp(-TxtMargin))
    Ytxt = Ytxt - TxtMargin
    
    pass

c1.Update()

#figure
if(isFigOut):
    FileName = re.findall('(.*)_(.*).root', FileIN[0])
    FigFile = './Figures/%s_ADC.gif' %(FileName[0][1])
    c1.Print(FigFile)
    pass
