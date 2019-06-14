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

c1 = ROOT.TCanvas('c1', 'c1', 0, 0, 1200, 900)

ROOT.gStyle.SetOptStat(0)

c1.SetFillColor(0)
c1.SetGridx()
c1.SetGridy()
c1.SetLogy()

#set variables
MinScale = 1.0e-6
MaxScale = 1.0e-1
ScaleBin = 1.0e-5
NofScaleBin = int((MaxScale - MinScale)/ScaleBin)

MinIter = 0.0
MaxIter = 1024.0
IterBin = 1.0
NofIterBin = int((MaxIter - MinIter)/IterBin)

hScale = []

for i in xrange(len(tr)):

    tmp = ROOT.TH2D('hScale_%d' %(i), 'Scale of DWT',
                    NofIterBin, MinIter, MaxIter,
                    NofScaleBin, MinScale, MaxScale)

    tr[i].Draw('ScalePower:Iteration$>>hScale_%d' %(i), '', 'Q0')

    hScale.append(tmp)

    pass

for i in xrange(len(hScale)):

    hScale[i].GetXaxis().SetTitle('Scale')
    hScale[i].GetXaxis().SetTitleFont(132)
    hScale[i].GetXaxis().SetTitleOffset(1.1)
    hScale[i].GetXaxis().SetLabelFont(132)
    hScale[i].GetYaxis().SetTitle('Power')
    hScale[i].GetYaxis().SetTitleFont(132)
    hScale[i].GetYaxis().SetTitleOffset(1.3)
    hScale[i].GetYaxis().SetLabelFont(132)

    hScale[i].SetMarkerColor(i + 2)
    hScale[i].SetMarkerStyle(8)
    hScale[i].SetMarkerSize(.6)
        
    if(i != 0):
        hScale[i].Draw('same')
    else:
        hScale[i].Draw('')
        pass

    pass

c1.Update()
