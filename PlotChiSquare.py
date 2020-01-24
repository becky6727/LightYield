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
                    help = 'input data file')

args = parser.parse_args()

FileIN = args.FileIN

if(FileIN == None):
    sys.exit()
    pass

VarArray = numpy.loadtxt(FileIN, unpack = True)

#calc dChi2 = 3
VarArray[1] = VarArray[1] - numpy.array(VarArray[1]).min()
MeanEdge = numpy.array(VarArray[0][numpy.where(VarArray[1] == 0.0)])[0]
MinEdge =  numpy.array(VarArray[0][numpy.where(VarArray[1] < 3.0)]).min()
MaxEdge =  numpy.array(VarArray[0][numpy.where(VarArray[1] < 3.0)]).max()

print 'Compton Edge = %2.2f + %2.2f - %2.2f' %(MeanEdge, MaxEdge - MeanEdge, MeanEdge - MinEdge)

#plot graph
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

gChi = ROOT.TGraph(len(VarArray[0]), numpy.array(VarArray[0]), numpy.array(VarArray[1]))

gChi.SetTitle('')
gChi.GetXaxis().SetTitle('Compton Edge')
gChi.GetXaxis().SetTitleFont(132)
gChi.GetXaxis().SetTitleOffset(1.1)
gChi.GetXaxis().SetLabelFont(132)
gChi.GetYaxis().SetTitle('#chi^{2}')
gChi.GetYaxis().SetTitleFont(132)
gChi.GetYaxis().SetTitleOffset(0.8)
gChi.GetYaxis().SetLabelFont(132)
gChi.GetXaxis().SetLimits(VarArray[0][0], VarArray[0][-1])
#gChi.SetMaximum(numpy.array(VarArray[1]).max())

gChi.SetMarkerColor(2)
gChi.SetMarkerSize(.8)
gChi.SetLineColor(2)
gChi.SetLineWidth(3)

gChi.Draw('apl')

#dChi2 lines
L1 = ROOT.TLine(VarArray[0][0], 1.0, VarArray[0][-1], 1.0)
L2 = ROOT.TLine(VarArray[0][0], 2.0, VarArray[0][-1], 2.0)
L3 = ROOT.TLine(VarArray[0][0], 3.0, VarArray[0][-1], 3.0)

L1.SetLineStyle(2)
L1.SetLineColor(3)
L1.SetLineWidth(3)

L2.SetLineStyle(3)
L2.SetLineColor(4)
L2.SetLineWidth(3)

L3.SetLineStyle(4)
L3.SetLineColor(6)
L3.SetLineWidth(3)

L1.Draw()
L2.Draw()
L3.Draw()

c1.Update()

