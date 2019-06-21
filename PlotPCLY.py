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

parser.add_argument('-fit',
                    action = 'store_true',
                    dest = 'isFit',
                    help = 'fitting calibration curve')

args = parser.parse_args()

FileIN = args.FileIN
isFigOut = args.isFigOut
isFit = args.isFit

if(len(FileIN) <= 0):
    sys.exit()
    pass

#set canvas
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

#initialize
XArray = []
YArray = []
ErrXArray = []
ErrYArray = []

gArray = [ROOT.TGraphErrors() for i in xrange(len(FileIN))]

fFit = [ROOT.TF1() for i in xrange(len(FileIN))]
fLin = [ROOT.TF1() for i in xrange(len(FileIN))]

#for graph
MinX = 0.0
MaxX = 21.0
MinY = 1.0e-1
MaxY = 100.0

#for latex
Xtxt = 1.0
Ytxt = MaxY* 0.80
TxtMargin = 0.5

Latex = ROOT.TLatex()

for i in xrange(len(FileIN)):

    XArray, YArray, ErrYArray = numpy.loadtxt(FileIN[i], skiprows = 0, comments = '#', unpack = True)
    ErrXArray = [0.0 for j in xrange(len(XArray))]

    gArray[i] = ROOT.TGraphErrors(len(XArray), numpy.array(XArray), numpy.array(YArray),
                                  numpy.array(ErrXArray), numpy.array(ErrYArray))

    gArray[i].SetTitle('PC Concentration Dependence of Charge at Compton edge')
    gArray[i].GetXaxis().SetTitle('PC Concentration [%]')
    gArray[i].GetXaxis().SetTitleFont(132)
    gArray[i].GetXaxis().SetTitleOffset(1.1)
    gArray[i].GetXaxis().SetLabelFont(132)
    gArray[i].GetYaxis().SetTitle('Charge')
    gArray[i].GetYaxis().SetTitleFont(132)
    gArray[i].GetYaxis().SetTitleOffset(0.8)
    gArray[i].GetYaxis().SetLabelFont(132)
    gArray[i].GetXaxis().SetLimits(MinX, MaxX)
    gArray[i].SetMinimum(MinY)
    gArray[i].SetMaximum(MaxY)
    
    gArray[i].SetMarkerColor(2*i + 2)
    gArray[i].SetMarkerStyle(8)
    gArray[i].SetMarkerSize(.8)
    gArray[i].SetLineColor(2*i + 2)
    gArray[i].SetLineWidth(3)

    if(i != 0):
        gArray[i].Draw('psame')
    else:
        gArray[i].Draw('ap')
        pass

    if(isFit):
        
        fFit[i] = ROOT.TF1('fFit_%d' %(i), '[0]*x + [1]', MinX, MaxX)

        tmp = (YArray[-1] - YArray[0])/(XArray[-1] - XArray[0])
        
        fFit[i].SetParameter(0, tmp)
        fFit[i].SetParameter(1, 0.0)

        gArray[i].Fit('fFit_%d' %(i), 'R0')
        
        Par0 = fFit[i].GetParameter(0)
        Par1 = fFit[i].GetParameter(1)

        fLin[i] = ROOT.TF1('fLin_%d' %(i), '[0]*x + [1]', MinX, MaxX)

        fLin[i].SetParameter(0, Par0)
        fLin[i].SetParameter(1, Par1)

        fLin[i].SetLineColor(2*i + 2)
        fLin[i].SetLineStyle(3)

        fLin[i].Draw('same')
        
        pass

    #draw latex
    Latex.SetTextSize(.025)
    Latex.SetTextColor(2*i + 2)

    Latex.DrawLatex(Xtxt, Ytxt, FileIN[i])
    
    Ytxt = Ytxt - TxtMargin

    pass

c1.Update()

#figure
FigFile = './Figures/LY_PC.gif'
#FigFile = './Figures/CalibChargeToEnergy_LAS.gif'

if(isFigOut):
    c1.Print(FigFile)
    pass
