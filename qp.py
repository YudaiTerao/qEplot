
"""
Usage:
  qp.py scf (-d <dir>)
  qp.py <Method> (-d <dir>...) [-c <bdcolor>] [-e <EneScale>] [-o <Ecenter>]

Options:
  scf              scf.outの情報を表で出力する
  <Method>         出力形式
  -d <dir>         resultの入っているdir(複数選択可)
  -c <bdcolor>     bandのcolor, defaultは5本ごとに色が変化  [default: rainbow]
  -e <EneScale>    任意のEneScale, "1 3 3"のように指定, 指定すると1ページ目に新たにページを追加し、1つのグラフをplot    [default: 1 4 4]
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
Pm.mpl_init()

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

def BandSinglePlot(ax: a.Axes, values, kpoints, EneScale, Ecenter=0, detailgrid=False, MinorScale=1, dn=Pm.DisplayNum, bdcolor=""):
    #----- add values -----#
    for i, value in enumerate(values):
        if bdcolor == 'rainbow': color = Pm.Colorlist(i%5)  #n本ごとに色を変える
        elif bdcolor == "": color = 'gray'
        else : color = bdcolor
        ax.plot( value[0], value[1], c=color, lw=Pm.Band_line_width ) #灰色
        if i+1==dn : break

    #----- axes config -----#
    Md.Kaxis(ax, 'x', kpoints)
    Md.Eaxis(ax, 'y', EneScale, Ecenter=Ecenter, detailgrid=detailgrid, MinorScale=MinorScale)

def BandComparePlot(ax: a.Axes, values1, values2, kpoints, EneScale, Ecenter=0, detailgrid=False, MinorScale=1, DisplayNum=-1):
    #-----values-----#
    for i, value1 in enumerate(values1):
        color=Pm.Colorlist(0)
        ax.plot( value1[0], value1[1], c=color, lw=Pm.Band_line_width)
        if i+1==DisplayNum : break
    for i, value2 in enumerate(values2):
        color=Pm.Colorlist(1)
        ax.plot( value2[0], value2[1], c=color, lw=Pm.Band_line_width)
        if i+1==DisplayNum : break

    Md.Kaxis(ax, 'x', kpoints)
    Md.Eaxis(ax, 'y', EneScale, Ecenter=Ecenter, detailgrid=detailgrid, MinorScale=MinorScale)

def AdjustXvalue(x_source, x_source_max: float, x_ref_max: float):
    x_new=[ float(xs*x_ref_max/x_source_max) for xs in x_source ]
    return x_new

#######################
# ===== DosPlot ===== #
#######################

def DosPlot(ax: a.Axes, values, EneScale, Eaxis='y', Ecenter=0, Elabel=True, detailgrid=False, MinorScale=1):
    # values:[[e1,d1],[e2,d2]....[en,dn]]
    #   nmax: 10 (colorlistを10までしか登録してない)
    #   e: Energy, d: Dos  e1,d1などはすべてlist
    for i, value in enumerate(values):
        ax.plot( value[1], value[0], c=Pm.Colorlist(i), lw=Pm.Dos_line_width )

    if Eaxis == 'x' :
        Md.Eaxis(ax, 'x', EneScale, Ecenter=Ecenter, detailgrid=detailgrid, MinorScale=MinorScale, Elabel=Elabel)
        Md.Daxis(ax, 'y', EneScale, values, Ecenter=Ecenter)
    elif Eaxis == 'y' :
        Md.Eaxis(ax, 'y', EneScale, Ecenter=Ecenter, detailgrid=detailgrid, MinorScale=MinorScale, Elabel=Elabel)
        Md.Daxis(ax, 'x', EneScale, values, Ecenter=Ecenter)

######################



if __name__ == '__main__':
    #----- 引数処理 -----#
    args = docopt(__doc__)
    Method = args['<Method>']
    bdcolor = args['-c']
    optEneScale = [float(x) for x in args['-e'].split()]
    Ecenter = float(args['-o'])

    files = []
    for dir in args["-d"]:
        if dir[-1] != '/': files.extend( glob.glob("{}/*".format(dir)) )
        else : files.extend( glob.glob("{}*".format(dir)) )
    for file in files:
        if   ".scf.out" in file: file_scf_out=file
        elif ".nscf.in" in file:
            with open(file, 'r') as fl:
                if "\'bands\'" in fl.read():file_nscf_in=file
        elif ".band.out" in file: file_band_out=file
        elif ".band.gnu" in file: file_band_gnu=file
        elif "_band.dat" in file: file_band_dat=file
        elif ".labelinfo.dat" in file: file_labelinfo=file
        elif ".pdos_tot" in file: file_pdos_tot=file

    #####################

    totE, ef, totM, absM = read_scf_out(file_scf_out)

    if Method == 'qb' or Method == 'wb':
        if Method =='qb':
            bd = QeBand(ef, file_nscf_in, file_band_out, file_band_gnu)
        elif Method =='wb':
            bd = WannierBand(ef, file_labelinfo, file_band_dat)

        fig, ax = Md.MakeAxesTable([1], [1.3], width=18, height=20, margin=1.8)
        BandSinglePlot(ax[0][0], bd.values, bd.kpoints, optEneScale, \
                       Ecenter=Ecenter, bdcolor=bdcolor, \
                       detailgrid=True, MinorScale=optEneScale[0]/5)
        ax[0][0].tick_params('x', labelsize=18)
        ax[0][0].tick_params('y', labelsize=16)
        ax[0][0].set_ylabel(Pm.text_Elabel, fontsize=22, labelpad=Pm.E_label_pad)
        plt.show()

    ##--- qb-p:: bandとdosの比較を出力 ---##
    ##--- wb-p:: Wannierのbandとdosの比較を出力 ---##
    elif Method == 'qb-p' or Method == 'wb-p':
        if Method == 'qb-p' :
            bd = QeBand(ef, file_nscf_in, file_band_out, file_band_gnu)
        elif Method == 'wb-p' :
            bd = WannierBand(ef, file_labelinfo, file_band_dat)
        ds = Dos(ef, [[file_pdos_tot, 0, 2], [file_pdos_tot, 0, 1]])

        fig, ax = Md.MakeAxesTable([1,0.7], [1.3], width=30, height=20, margin=1.8)
        BandSinglePlot(ax[0][0], bd.values, bd.kpoints, optEneScale, \
                       Ecenter=Ecenter, bdcolor=bdcolor, \
                       detailgrid=True, MinorScale=optEneScale[0]/5)
        DosPlot(ax[0][1], ds.values, optEneScale, Ecenter=Ecenter, Elabel=False, \
                detailgrid=True, MinorScale=optEneScale[0]/5)
        ax[0][0].tick_params('x', labelsize=18)
        ax[0][0].tick_params('y', labelsize=16)
        ax[0][1].tick_params('x', labelsize=16)
        ax[0][1].tick_params('y', labelsize=16)
        ax[0][0].set_ylabel(Pm.text_Elabel, fontsize=22, labelpad=Pm.E_label_pad)
        plt.show()

    ## qb-wb:: qebandとWannierbandの比較を6つの範囲で出力
    elif Method == 'qb-wb' :
        qb = QeBand(ef, file_nscf_in, file_band_out, file_band_gnu)
        wb = WannierBand(ef, file_labelinfo, file_band_dat)
        qb_values=[]
        for value in qb.values:
            adjust_qb_xvalue=AdjustXvalue(value[0], qb.kpoints[1][-1], wb.kpoints[1][-1])
            qb_values.append([adjust_qb_xvalue, value[1]])

        fig, ax = Md.MakeAxesTable([1], [1.3], width=18, height=20, margin=1.8)
        BandComparePlot(ax[0][0], qb_values, wb.values, wb.kpoints, \
                      optEneScale, Ecenter=Ecenter, \
                      detailgrid=True, MinorScale=optEneScale[0]/5)
        ax[0][0].tick_params('x', labelsize=18)
        ax[0][0].tick_params('y', labelsize=16)
        ax[0][0].set_ylabel(Pm.text_Elabel, fontsize=22, labelpad=Pm.E_label_pad)
        plt.show()

