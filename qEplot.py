
"""
Usage:
  qEplot.py scf (-d <dir>) [-s <SAVE_PATH>] [-m <MN>]
  qEplot.py <Method> (-d <dir>...) [-p <Prefix>] [-s <SAVE_PATH>] [-n <pdfname] [-c <bdcolor>] [-e <EneScale>] [-o <Ecenter>] 

Options:
  scf              scf.outの情報を表で出力する
  <Method>         出力形式
  -d <dir>         resultの入っているdir(複数選択可)
  -p <Prefix>      物質名, 出力pdfの名前とTitleに使う   [default: ]
  -s <SAVE_PATH>   保存先                       [default: ./]
  -n <pdfname>     任意の出力pdf名              [default: ]
  -c <bdcolor>     bandのcolor, defaultは5本ごとに色が変化  [default: rainbow]
  -e <EneScale>    任意のEneScale, "1 3 3"のように指定, 指定すると1ページ目に新たにページを追加し、1つのグラフをplot    [default: ]
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
    
if __name__ == '__main__':
    #----- 引数処理 -----#
    args = docopt(__doc__)
    print(args)
    Method = args['<Method>']
    bdcolor = args['-c']
    optEneScale = [float(x) for x in args['-e'].split()]
    Ecenter = float(args['-o'])
    SAVE_PATH = args['-s']
    if SAVE_PATH[-1] == '/': SAVE_PATH = SAVE_PATH[:-1]

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

    if args['-p'] != "" : Prefix = args['-p']
    else :
        for dir in args['-d']: Prefix = file_scf_out.replace(dir, "")
        Prefix=Prefix.replace(".scf.out", "").replace("/", "") 
    
    #####################

    totE, ef, totM, absM = read_scf_out(file_scf_out)

    if Method == 'qb' or Method == 'wb':
        if Method =='qb':
            bd = QeBand(ef, file_nscf_in, file_band_out, file_band_gnu)
            Title = "{}\nQeBand".format(Prefix)
        elif Method =='qb':
            bd = QeBand(ef, file_labelinfo, file_band_dat)
            Title = "{}\nQeBand".format(Prefix)
 
        if args['-n'] == "":
            pp = PdfPages("{}/{}_{}.pdf".format(SAVE_PATH, Prefix, Method))
        else: pp = PdfPages(args['-n']+".pdf")
        #--- page0 ---#
        if len(optEneScale) == 3:
            fig, ax = Md.MakeAxesTable(Pm.bd_single_width, Pm.bd_single_height, margin=Pm.single_margin)
            for i in range(len(ax)):
                for j in range(len(ax[0])):
                    BandSinglePlot(ax[i][j], bd.values, bd.kpoints, optEneScale, Ecenter=Ecenter, bdcolor=bdcolor) 
                    ax[i][j].tick_params('x', labelsize=18)         
                    ax[i][j].tick_params('y', labelsize=16)         
                    ax[i][j].set_ylabel(Pm.text_Elabel, fontsize=22, labelpad=Pm.E_label_pad)
            plt.savefig(pp, format='pdf')
            fig.clf()

        #---page1---#
        fig, ax = Md.MakeAxesTable(Pm.bd_table_width, Pm.bd_table_height, margin=Pm.table_margin, Title=Title)
        for i in range(len(ax)):
            for j in range(len(ax[0])):
                BandSinglePlot(ax[i][j], bd.values, bd.kpoints, Pm.bd_table_ESl[i][j], Ecenter=Ecenter, bdcolor=bdcolor)
        plt.savefig(pp, format='pdf')
        fig.clf()

        #---page2---#
        # 詳細なgridの追加
        fig, ax = Md.MakeAxesTable(Pm.bd_detail_width, Pm.bd_detail_height, margin=Pm.detail_margin)
        for i in range(len(ax)):
            for j in range(len(ax[0])):
                BandSinglePlot(ax[i][j], bd.values, bd.kpoints, Pm.bd_detail_ESl[i][j], Ecenter=Ecenter, bdcolor=bdcolor, detailgrid=True, MinorScale=0.2)
        plt.savefig(pp, format='pdf')
        fig.clf()
        
        pp.close()
        























