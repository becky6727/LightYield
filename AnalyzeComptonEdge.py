import os, sys, time
import numpy
import argparse
import ROOT

parser = argparse.ArgumentParser(description = 'options')

parser.add_argument('-i',
                    type = str,
                    dest = 'FileIN',
                    #nargs = '+',
                    default = None,
                    help = 'input root files')

parser.add_argument('-o',
                    type = str,
                    dest = 'FileOUT',
                    #nargs = '+',
                    default = None,
                    help = 'output files')

args = parser.parse_args()

FileIN = args.FileIN
FileOUT = args.FileOUT

if(FileIN == None):
    sys.exit()
    pass

if(FileOUT == None):
    sys.exit()
    pass

RFile = ROOT.TFile(FileIN)
tr = RFile.Get('tr')

#set parameters for histogram of charge
MinADC = 0.0
#MaxADC = int(tr.GetMaximum('ADC'))
MaxADC = 200.0
ADCBinWidth = [x/20.0 for x in xrange(1, 10, 1)]
NBinADC = [int((MaxADC - MinADC)/ADCBinWidth[i]) for i in xrange(len(ADCBinWidth))]
    
#hADC = [ROOT.TH1D('hADC_%d' %(i), 'ADC Total', NBinADC[i], MinADC, MaxADC) for i in xrange(len(NBinADC))]

hADC = []

for i in xrange(len(NBinADC)):
    tmp = ROOT.TH1D('hADC_%d' %(i), 'ADC Total', NBinADC[i], MinADC, MaxADC)
    tr.Draw('ADC>>hADC_%d' %(i), '', 'Q0')
    hADC.append(tmp)
    pass

#set parameters for fitting
MinFit = 20.0
MaxFit = 120.0

fFit = ROOT.TF1('fFit', '[0]* TMath::Erf(-(x - [1])/[2]) + [3]', MinFit, MaxFit)

ParArray = [[] for i in xrange(4)]
ReducedChi2Array = []

for i in xrange(len(hADC)):
    
    Par0 = 0.5* hADC[i].GetMaximum()
    Par1 = (MaxFit - MinFit)/2.0
    Par2 = 1.0e+2
    Par3 = Par0/2.0
    
    fFit.SetParameter(0, Par0)
    fFit.SetParameter(1, Par1)
    fFit.SetParameter(2, Par2)
    fFit.SetParameter(3, Par3)

    hADC[i].Fit('fFit', 'RQ0')
    
    #print 'Chi2 = %3.2f, NDF = %d' %(fFit.GetChisquare(), fFit.GetNDF())
    #print 'Bin = %1.3f Chi2/NDF = %3.4f' %(ADCBinWidth[i], fFit.GetChisquare()/fFit.GetNDF())

    if(fFit.GetParameter(1)  < 0.0):
        continue
    
    #if((fFit.GetChisquare()/fFit.GetNDF()) < 1.0):
    #    continue
    
    for j in xrange(len(ParArray)):
        ParArray[j].append(fFit.GetParameter(j))
        pass
    
    ReducedChi2Array.append(abs(fFit.GetChisquare()/fFit.GetNDF()-1.0))
    #ReducedChi2Array.append((fFit.GetChisquare()/fFit.GetNDF()-1.0))
    
    pass

Par = [ParArray[i][numpy.where(ReducedChi2Array == numpy.array(ReducedChi2Array).min())[0][0]] for i in xrange(4)]
Bin = ADCBinWidth[numpy.where(ReducedChi2Array == numpy.array(ReducedChi2Array).min())[0][0]]
NBin = int((MaxADC - MinADC)/Bin)

print Par
print Bin

#calc chi2
htmp = ROOT.TH1D('htmp', '', NBin, MinADC, MaxADC)
tr.Draw('ADC>>htmp', '', 'Q0')

fErf = ROOT.TF1('fFit', '[0]* TMath::Erf(-(x - [1])/[2]) + [3]', MinFit, MaxFit)

for i in xrange(len(Par)):
    fErf.SetParameter(i, Par[i])
    pass

EdgeArray = []
Chi2Array = []

for j in xrange(-200, 200, 1):
    Chi2 = 0.0
    Edge = Par[1] + (j/100.0)
    fErf.SetParameter(1, Edge)
    for i in xrange(htmp.GetNbinsX()):
        X = htmp.GetXaxis().GetBinCenter(i)
        Content =  htmp.GetBinContent(i)
        val = fErf.Eval(X)
        if(X > MinFit and X < MaxFit):
            Chi2 = Chi2 + ((Content - val)**2/val)
            pass
        pass
    EdgeArray.append(Edge)
    Chi2Array.append(Chi2)
    pass

#output data
numpy.savetxt(FileOUT, numpy.transpose((EdgeArray, Chi2Array)), delimiter = ' ',fmt = '%2.2f %2.4f')
