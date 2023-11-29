
"""
Usage:
  banddos_plot.py scf (-d <dir>)
  banddos_plot.py (-d <dir>...) [-c <bdcolor>] [-e <EneScale>] [-o <Ecenter>]

Options:
  scf              scf.outの情報を表で出力する
  -d <dir>         resultの入っているdir(複数選択可)
  -c <bdcolor>     bandのcolor, defaultは5本ごとに色が変化  [default: rainbow]
  -e <EneScale>    任意のEneScale, 1-3-3のように指定, 指定すると1ページ目に新たにページを追加し、1つのグラフをplot    [default: 1-4-4]
  -o <Ecenter>     Eのグラフの中心, efから何eV離れたところに線を引くか  [default: 0.0]
"""

from docopt import docopt
import os
import glob
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import axes as a
from matplotlib.backends.backend_pdf import PdfPages

import plottool as pt
pt.mpl_init()

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
            lines = f_nscf_in.readlines()
        for i, line in enumerate(lines):
            if "K_POINTS" in line:
                for j in (range(int(lines[i+1]))):
                    if '!' in lines[i+j+2]:
                        kpoints_name.append(lines[i+j+2].split('!')[-1])
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
        with open(file_band_gnu, 'r') as fbg:
            lines = [ line.split() for line in f_band_gnu.readlines() ]
        j, values = 0, []
        for i, line in enumerate(lines):
            if ( len(line) < 2 ):
                value = np.array(lines[j:i], dtype=np.float64).T
                value[1] = value[1] - self.ef
                values.append(value)
                j = i+1
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
        with open(file_band_dat, "r") as f_band_dat:
            lines = [ line.split() for line in f_band_dat.readlines() ]
        j, values = 0, []
        for i, line in enumerate(lines):
            if ( len(line) < 1 ):
                value = np.array(lines[j:i], dtype=np.float64).T
                value[1] = value[1] - self.ef
                values.append(value)
                j = i+1
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
        enevalue = [ float(line[enecolumn]) - self.ef for line in lines[1:] ]
        dosvalue = [ float(line[doscolumn]) for line in lines[1:] ]
        return [ enevalue, dosvalue ]


######################
class plotoption():
    def __init__(self):
        #----- 引数処理 -----#
        args = docopt(__doc__)
        self.bdcolor = args['-c']
        self.optEneScale = [ float(x) for x in args['-e'].split('-') ]
        self.Ecenter = float(args['-o'])

        files = []
        for dir in args["-d"]: files = files + pt.filelist(dir)
        for file in files:
            if   ".scf.out" in file: self.file_scf_out=file
            elif ".nscf.in" in file:
                with open(file, 'r') as fl:
                    if "\'bands\'" in fl.read():self.file_nscf_in=file
            elif ".band.out" in file: self.file_band_out=file
            elif ".band.gnu" in file: self.file_band_gnu=file
            elif "_band.dat" in file: self.file_band_dat=file
            elif ".labelinfo.dat" in file: self.file_labelinfo=file
            elif ".pdos_tot" in file: self.file_pdos_tot=file

        self.totE, self.ef, self.totM, self.absM = pt.read_scf_out(self.file_scf_out)


####### Main #######

def bandplot():
    op = plotoption()
    if op.file_labelinfo is None :
        bd = QeBand(op.ef, op.file_nscf_in, op.file_band_out, op.file_band_gnu)
    else :
        bd = WannierBand(op.ef, op.file_labelinfo, op.file_band_dat)
    fig, ax = pt.MakeAxesTable([1], [1.3], width=18, height=20, margin=1.8)
    pt.BandSinglePlot(ax[0][0], bd.values, bd.kpoints, op.optEneScale, \
                      Ecenter=op.Ecenter, bdcolor=op.bdcolor, \
                      detailgrid=True, MinorScale=op.optEneScale[0]/5)
    ax[0][0].tick_params('x', labelsize=18)
    ax[0][0].tick_params('y', labelsize=16)
    ax[0][0].yaxis.label.set_size(22)
    plt.show()

##--- qb-p:: bandとdosの比較を出力 ---##
##--- wb-p:: Wannierのbandとdosの比較を出力 ---##
def banddosplot():
    op = plotoption()
    if op.file_labelinfo is None :
        bd = QeBand(op.ef, op.file_nscf_in, op.file_band_out, op.file_band_gnu)
    else :
        bd = WannierBand(op.ef, op.file_labelinfo, op.file_band_dat)
    ds = Dos(ef, [[op.file_pdos_tot, 0, 2], [op.file_pdos_tot, 0, 1]])

    fig, ax = pt.MakeAxesTable([1,0.7], [1.3], width=30, height=20, margin=1.8)
    pt.BandSinglePlot(ax[0][0], bd.values, bd.kpoints, op.optEneScale, \
                      Ecenter=op.Ecenter, bdcolor=op.bdcolor, \
                      detailgrid=True, MinorScale=elf.ptEneScale[0]/5)
    pt.DosPlot(ax[0][1], ds.values, op.optEneScale, Ecenter=op.Ecenter, \
               detailgrid=True, MinorScale=op.optEneScale[0]/5)
    ax[0][0].tick_params('x', labelsize=18)
    ax[0][0].tick_params('y', labelsize=16)
    ax[0][1].tick_params('x', labelsize=16)
    ax[0][1].tick_params('y', labelsize=16)
    ax[0][0].yaxis.label.set_size(22)
    ax[0][1].set_ylabel("")
    plt.show()

## qb-wb:: qebandとWannierbandの比較を6つの範囲で出力
def qbwbplot():
    op = plotoption()
    qb = QeBand(op.ef, op.file_nscf_in, op.file_band_out, op.file_band_gnu)
    wb = WannierBand(op.ef, op.file_labelinfo, op.file_band_dat)
    qb_values=[]
    for value in qb.values:
        adjust_qb_xvalue=pt.AdjustXvalue(value[0], qb.kpoints[1][-1], wb.kpoints[1][-1])
        qb_values.append([adjust_qb_xvalue, value[1]])

    fig, ax = pt.MakeAxesTable([1], [1.3], width=18, height=20, margin=1.8)
    pt.BandComparePlot(ax[0][0], qb_values, wb.values, wb.kpoints, \
                       op.optEneScale, Ecenter=op.Ecenter, \
                       detailgrid=True, MinorScale=op.optEneScale[0]/5)
    ax[0][0].tick_params('x', labelsize=18)
    ax[0][0].tick_params('y', labelsize=16)
    ax[0][0].yaxis.label.set_size(22)
    plt.show()


