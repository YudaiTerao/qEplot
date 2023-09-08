
"""
Usage:
  qEplot.py scf (-d <dir>) [-s <SAVE_PATH>] [-m <MN>]
  qEplot.py <Method> (-d <dir>...) [-s <SAVE_PATH>] [-m <MN>] [-p <pdfname] [-c <bdcolor>][-e <EneScale>] [-o <Ecenter>] 
Options:
  scf              scf.outの情報を表で出力する
  <Method>         出力形式
  -d <dir>         resultの入っているdir(複数選択可)
  -s <SAVE_PATH>   保存先                       [default: ./]
  -m <MN>          出力pdfの名前とTitleに使う   [default: ]
  -p <pdfname>     任意の出力pdf名              [default: ]
  -c <bdcolor>     bandのcolor, defaultは5本ごとに色が変化  [default: ranibow]
  -e <EneScale>    任意のEneScale, 指定すると1ページ目に新たにページを追加し、1つのグラフをplot    [default: ]
  -o <Ecenter>     Eのグラフの中心, efから何eV離れたところに線を引くか  [default: 0.0]
"""

from docopt import docopt
import os
import glob
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import axes as a
from matplotlib.backends.backend_pdf import PdfPages
import plotParameter as Pm
import plotModule as Md

########################
# ===== ReadData ===== #
########################

class QeBand:
    def __init__(self, ef, file_nscf_in, file_band_out, file_band_gnu):      
        self.ef = float(ef)
        self.kpoints = [ self.read_nscf_in(file_nscf_in), self.read_band_out(file_band_out) ]
        self.values = self.read_band_gnu(file_band_gnu)

    def read_nscf_in(self, file_nscf_in):
        kpoints_name = []
        with open(file_nscf_in, 'r') as f_nscf_in:
            lines=f_nscf_in.readlines()
        for i,line in enumerate(lines):
            if "K_POINTS" in line:
                for j in (range(int(lines[i+1]))):
                    kpoints_name.append(lines[i+j+2].split()[-1])
                break
        kpoints_name = [ kn.replace("G", "$\Gamma$") for kn in kpoints_name ]
        return kpoints_name

    def read_band_out(self, file_band_out):
        kpoints_coord = []
        with open(file_band_out, "r") as f_band_out:
            for line in f_band_out.readlines():
                if "high-symmetry point" in line:
                    kpoints_coord.append(float(line.split()[-1]))
        return kpoints_coord

    def read_band_gnu(self, file_band_gnu):
        values = [[[],[]]]
        with open(file_band_gnu, 'r') as f_band_gnu:
            lines = [ line.split() for line in f_band_gnu.readlines() ]
        j = k = 0
        for i, line in enumerate(lines):
            if ( len(line) < 2 ):
                values[k][0] = [ float(lines[n][0]) for n in range(j,i) ]
                values[k][1] = [ float(lines[n][1])-self.ef for n in range(j,i) ]
                values.extend([[[],[]]])
                j = i+1
                k += 1
        return values

class WannierBand:
    def __init__(self, ef: float, file_labelinfo, file_band_dat):
        self.ef = ef
        self.kpoints = self.read_labelinfo(file_labelinfo) 
        self.values = self.read_band_dat(file_band_dat)

    def read_labelinfo(self, file_labelinfo):
        kpoints_name = []
        kpoints_coord = []
        with open(file_labelinfo, 'r')  as f_labelinfo:
            for line in f_labelinfo.readlines():
                kpoints_name.append(line.split()[0])
                kpoints_coord.append(float(line.split()[2]))
        kpoints_name = [ kn.replace("G", "$\Gamma$") for kn in kpoints_name ]
        return [ kpoints_name, kpoints_coord ]

    def read_band_dat(self, file_band_dat):
        values = [[[],[]]]
        lines = [ line.split()  for line in open(file_band_dat, "r").readlines() ]
        j = k = 0
        for i, line in enumerate(lines):
            if ( len(line) < 1 ):
                values[k][0] = [ float(lines[n][0]) for n in range(j,i) ]
                values[k][1] = [ float(lines[n][1]) -self.ef for n in range(j,i) ]
                values.extend([[[],[]]])
                j = i+1
                k += 1
        return values

class Dos:
    def __init__(self, ef: float, column_pdos):
        #column_pdos: ([ file名1, enecolumn1, doscolumn1 ],[file名2, .....)
        self.ef = ef
        self.values = []
        for column in column_pdos:
            self.values.append(self.read_pdos(column[0], column[1], column[2]))

    def read_pdos(self, file_pdos, enecolumn, doscolumn): 
        with open(file_pdos, 'r') as f_pdos:
            lines = [ line.split()  for line in f_pdos.readlines() ]
        enevalue = [ float(line[enecolumn]) - self.ef  for line in lines[1:] ]
        dosvalue = [ float(line[doscolumn])  for line in lines[1:] ]
        return [ enevalue, dosvalue ]

def read_scf_out(file_scf_out):
    TotalEne=FermiEne=Totalmag=Absolutemag=""
    with open(file_scf_out, 'r') as f_scf_out:
        for line in f_scf_out.readlines():
            if "!" in line:
                TotalEne = float(line.split()[4])
            elif "Fermi" in line:
                FermiEne = float(line.split()[4])
            elif "total magnetization" in line:
                Totalmag = float(line.split()[3])
            elif "absolute magnetization" in line:
                Absolutemag = float(line.split()[3])
    return TotalEne, FermiEne, Totalmag, Absolutemag

########################
# ===== BandPlot ===== #
########################

def BandSinglePlot(ax: a.Axes, values, kpoints, EneScale, detailgrid=False, MinorScale=1, dn=Pm.DisplayNum, bdcolor=""): 
    #----- add values -----#
    for i, value in enumerate(values):
        if bdcolor == 'rainbow': color = Pm.Colorlist(i%5)  #n本ごとに色を変える
        elif bdcolor == "": color = 'gray'
        else : color = bdcolor
        ax.plot( value[0], value[1], c=color, lw=Pm.Band_line_width ) #灰色
        if i+1==DisplayNum : break

    #----- axes config -----#
    Md.Kaxis(ax, 'x', kpoints)
    Md.Eaxis(ax, 'y', EneScale, detailgrid=detailgrid, MinorScale=MinorScale)
    
         
