
"""
Usage:
  banddos_plot_pdf.py <dir> [-d <dir2>...] [-p <Prefix>] [-s <SAVE_PATH>] [-c <bdcolor>] [-e <EneScale>] [-o <Ecenter>]

Options:
  scf              scf.outの情報を表で出力する
  <dir>            resultの入っているdir
  -d <dir2>         resultの入っているdir, 追加選択分(複数選択可)
  -p <Prefix>      物質名, 出力pdfの名前とTitleに使う   [default: ]
  -s <SAVE_PATH>   保存先                       [default: ./]
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

        dirlist = [ args['<dir>'] ]
        if args['-d'] is not None:
            dirlist = dirlist + args['-d']
        files = []
        for dir in dirlist: files = files + pt.filelist(dir)
        for file in files:
            if   ".scf.out" in file: self.file_scf_out=file
            elif ".nscf.in" in file:
                with open(file, 'r') as fl:
                    if "\'bands\'" in fl.read():self.file_nscf_in=file
            elif ".band.out" in file: self.file_band_out=file
            elif ".band.gnu" in file: self.file_band_gnu=file
            elif "_band.dat" in file: self.file_band_dat=file
            elif ".labelinfo.dat" in file:
                self.file_labelinfo=file
                self.w90 = True
            elif ".pdos_tot" in file: self.file_pdos_tot=file

        self.SAVE_PATH = args['-s']
        if self.SAVE_PATH[-1] == '/': self.SAVE_PATH = self.SAVE_PATH[:-1]
        if args['-p'] != "" : self.Prefix = args['-p']
        else :
            for dir in dirlist: self.Prefix = self.file_scf_out.replace(dir, "")
            self.Prefix=self.Prefix.replace(".scf.out", "").replace("/", "")

        self.totE, self.ef, self.totM, self.absM = pt.read_scf_out(self.file_scf_out)


####### Main #######

def bandplot():
    op = plotoption()
    if op.w90 == False :
        bd = QeBand(op.ef, op.file_nscf_in, op.file_band_out, op.file_band_gnu)
        pp = PdfPages("{}/{}_qb.pdf".format(op.SAVE_PATH, op.Prefix))
        Title = "{}\nQeBand".format(op.Prefix)
    else :
        bd = WannierBand(op.ef, op.file_labelinfo, op.file_band_dat)
        pp = PdfPages("{}/{}_wb.pdf".format(op.SAVE_PATH, op.Prefix))
        Title = "{}\nWannierBand".format(op.Prefix)

    #---page0---#
    if len(op.optEneScale) == 3:
        fig, ax = pt.MakeAxesTable(pt.bd_single_width, pt.bd_single_height, \
                                   margin=pt.bd_single_margin)
        for i in range(len(ax)):
            for j in range(len(ax[0])):
                pt.BandSinglePlot(ax[i][j], bd.values, bd.kpoints,op.optEneScale, \
                                  Ecenter=op.Ecenter, bdcolor=op.bdcolor)
                ax[i][j].tick_params('x', labelsize=18)
                ax[i][j].tick_params('y', labelsize=16)
                ax[i][j].yaxis.label.set_size(22)
        plt.savefig(pp, format='pdf')
        fig.clf()

    #---page1---#
    fig, ax = pt.MakeAxesTable(pt.bd_table_width, pt.bd_table_height, \
                               margin=pt.bd_table_margin, Title=Title)
    EneScale = np.array(pt.bd_table_ESl).reshape(3,2,3).tolist()
    for i in range(len(ax)):
        for j in range(len(ax[0])):
            pt.BandSinglePlot(ax[i][j], bd.values, bd.kpoints, EneScale[i][j], \
                              Ecenter=op.Ecenter, bdcolor=op.bdcolor)
    plt.savefig(pp, format='pdf')
    fig.clf()

    #---page2---#
    # 詳細なgridの追加
    fig, ax = pt.MakeAxesTable(pt.bd_detail_width, pt.bd_detail_height, \
                               margin=pt.bd_detail_margin)
    for i in range(len(ax)):
        for j in range(len(ax[0])):
            pt.BandSinglePlot(ax[i][j], bd.values, bd.kpoints, \
                              pt.bd_detail_ESl, Ecenter=op.Ecenter, \
                              bdcolor=op.bdcolor, detailgrid=True)
    plt.savefig(pp, format='pdf')
    fig.clf()

    pp.close()


def banddosplot():
    ##--- qb-p:: bandとdosの比較を6つの範囲で出力 ---##
    ##--- wb-p:: Wannierのbandとdosの比較を6つの範囲で出力 ---##
    op = plotoption()
    if op.w90 == False :
        bd = QeBand(op.ef, op.file_nscf_in, op.file_band_out, op.file_band_gnu)
        pp = PdfPages("{}/{}_qb-p.pdf".format(op.SAVE_PATH, op.Prefix))
        Title = "{}\nQeBand-pdos".format(op.Prefix)
    else :
        bd = WannierBand(op.ef, op.file_labelinfo, op.file_band_dat)
        pp = PdfPages("{}/{}_wb-p.pdf".format(op.SAVE_PATH, op.Prefix))
        Title = "{}\nWannier-pdos".format(op.Prefix)
    ds = Dos(op.ef, [[op.file_pdos_tot, 0, 2], [op.file_pdos_tot, 0, 1]])

    #---page0---#
    if len(op.optEneScale) == 3:
        bdp_single_width = pt.bd_single_width.copy()
        bdp_single_width.append(pt.bd_single_width[0]*6/10)
        fig, ax = pt.MakeAxesTable(pt.bdp_single_width, pt.bd_single_height, \
                                   margin=pt.bdp_single_margin, \
                                   width = 25, height=13)
        for i in range(len(ax)):
            pt.BandSinglePlot(ax[i][0], bd.values, bd.kpoints, op.optEneScale, \
                           Ecenter=op.Ecenter, bdcolor=op.bdcolor)
            pt.DosPlot(ax[i][1], ds.values, op.optEneScale, Ecenter=op.Ecenter)
            ax[i][0].tick_params('x', labelsize=18)
            ax[i][0].tick_params('y', labelsize=16)
            ax[i][1].tick_params('x', labelsize=16)
            ax[i][1].tick_params('y', labelsize=16)
            ax[i][0].yaxis.label.set_size(22)
            ax[i][1].set_ylabel("")
        plt.savefig(pp, format='pdf')
        fig.clf()

    #---page1,2---#
    EneScale = np.array(pt.bd_table_ESl).reshape(2,3,3).tolist()
    for page in range(2):
        if page != 0 : Title = ""
        fig, ax = pt.MakeAxesTable(pt.bdp_table_width, pt.bdp_table_height, \
                                   margin=pt.bdp_table_margin, Title=Title, header=pt.header)
        for i in range(len(ax)):
            pt.BandSinglePlot(ax[i][0], bd.values, bd.kpoints, \
                              EneScale[page][i], Ecenter=Ecenter, bdcolor=bdcolor)
            pt.DosPlot(ax[i][1], ds.values, EneScale[page][i], Ecenter=Ecenter)
            ax[i][1].set_ylabel("")
        plt.savefig(pp, format='pdf')
        fig.clf()

    #---page3---#
    bdp_detail_width = pt.bd_detail_width.copy()
    bdp_detail_width.append(pt.bd_detail_width[0]*6/10)
    fig, ax = pt.MakeAxesTable(bdp_detail_width, pt.bd_detail_height, \
                                   margin=pt.bdp_detail_margin, width = 25)
    for i in range(len(ax)):
        pt.BandSinglePlot(ax[i][0], bd.values, bd.kpoints, pt.bd_detail_ESl, \
               Ecenter=Ecenter, bdcolor=bdcolor, detailgrid=True, MinorScale=0.2)
        pt.DosPlot(ax[i][1], ds.values, pt.bd_detail_ESl, Ecenter=Ecenter, \
                   detailgrid=True)
        ax[i][1].set_ylabel("")
    plt.savefig(pp, format='pdf')
    fig.clf()

    pp.close()


def qbwbplot():
    ## qb-wb:: qebandとWannierbandの比較を6つの範囲で出力
    op = plotoption()
    pp = PdfPages("{}/{}_qb-wb.pdf".format(op.SAVE_PATH, op.Prefix))
    Title = "{}\nQe-WannierBand".format(op.Prefix)

    qb = QeBand(op.ef, op.file_nscf_in, op.file_band_out, op.file_band_gnu)
    wb = WannierBand(op.ef, op.file_labelinfo, op.file_band_dat)
    qb_values=[]
    for value in qb.values:
        adjust_qb_xvalue=pt.AdjustXvalue(value[0], qb.kpoints[1][-1], wb.kpoints[1][-1])
        qb_values.append([adjust_qb_xvalue, value[1]])

    #---page0---#
    if len(op.optEneScale) == 3:
        fig, ax = pt.MakeAxesTable(pt.bd_single_width, pt.bd_single_height, \
                                   margin=pt.bd_single_margin)
        for i in range(len(ax)):
            for j in range(len(ax[0])):
                pt.BandComparePlot(ax[i][j], qb_values, wb.values, wb.kpoints, \
                              op.optEneScale, Ecenter=op.Ecenter)
                ax[i][j].tick_params('x', labelsize=18)
                ax[i][j].tick_params('y', labelsize=16)
                ax[i][j].yaxis.label.set_size(22)
        plt.savefig(pp, format='pdf')
        fig.clf()

    #---page1---#
    fig, ax = pt.MakeAxesTable(pt.bd_table_width, pt.bd_table_height, \
                               margin=pt.bd_table_margin, Title=Title)
    EneScale = np.array(pt.bd_table_ESl).reshape(3,2,3).tolist()
    for i in range(len(ax)):
        for j in range(len(ax[0])):
            pt.BandComparePlot(ax[i][j], qb_values, wb.values, wb.kpoints, \
                               EneScale[i][j], Ecenter=op.Ecenter)
    plt.savefig(pp, format='pdf')
    fig.clf()

    #---page2---#
    # 詳細なgridの追加
    fig, ax = pt.MakeAxesTable(pt.bd_detail_width, pt.bd_detail_height, \
                               margin=pt.bd_detail_margin)
    for i in range(len(ax)):
        for j in range(len(ax[0])):
            pt.BandComparePlot(ax[i][j], qb_values, wb.values, wb.kpoints, \
                               pt.bd_detail_ESl, Ecenter=op.Ecenter, \
                               detailgrid=True, MinorScale=0.2)
    plt.savefig(pp, format='pdf')
    fig.clf()

    pp.close()







