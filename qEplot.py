
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
        
    if args['-n'] == "":
        pp = PdfPages("{}/{}_{}.pdf".format(SAVE_PATH, Prefix, Method))
    else: pp = PdfPages("{}/{}.pdf".format(SAVE_PATH, args['-n']))

    if Method == 'qb' or Method == 'wb':
        if Method =='qb':
            bd = QeBand(ef, file_nscf_in, file_band_out, file_band_gnu)
            Title = "{}\nQeBand".format(Prefix)
        elif Method =='qb':
            bd = QeBand(ef, file_labelinfo, file_band_dat)
            Title = "{}\nQeBand".format(Prefix)
 
        #---page0---#
        if len(optEneScale) == 3:
            fig, ax = Md.MakeAxesTable(Pm.bd_single_width, Pm.bd_single_height, \
                                       margin=Pm.bd_single_margin)
            for i in range(len(ax)):
                for j in range(len(ax[0])):
                    BandSinglePlot(ax[i][j], bd.values, bd.kpoints, optEneScale, \
                                   Ecenter=Ecenter, bdcolor=bdcolor) 
                    ax[i][j].tick_params('x', labelsize=18)         
                    ax[i][j].tick_params('y', labelsize=16)         
                    ax[i][j].set_ylabel(Pm.text_Elabel, fontsize=22, labelpad=Pm.E_label_pad)
            plt.savefig(pp, format='pdf')
            fig.clf()

        #---page1---#
        fig, ax = Md.MakeAxesTable(Pm.bd_table_width, Pm.bd_table_height, \
                                   margin=Pm.bd_table_margin, Title=Title)
        EneScale = np.array(Pm.bd_table_ESl).reshape(3,2,3).tolist()
        for i in range(len(ax)):
            for j in range(len(ax[0])):
                BandSinglePlot(ax[i][j], bd.values, bd.kpoints, \
                               EneScale[i][j], Ecenter=Ecenter, bdcolor=bdcolor)
        plt.savefig(pp, format='pdf')
        fig.clf()

        #---page2---#
        # 詳細なgridの追加
        fig, ax = Md.MakeAxesTable(Pm.bd_detail_width, Pm.bd_detail_height, \
                                   margin=Pm.bd_detail_margin)
        for i in range(len(ax)):
            for j in range(len(ax[0])):
                BandSinglePlot(ax[i][j], bd.values, bd.kpoints, \
                               Pm.bd_detail_ESl, Ecenter=Ecenter, \
                               bdcolor=bdcolor, detailgrid=True, MinorScale=0.2)
        plt.savefig(pp, format='pdf')
        fig.clf()
        
        pp.close()
        
    ##--- qb-p:: bandとdosの比較を6つの範囲で出力 ---##
    ##--- wb-p:: Wannierのbandとdosの比較を6つの範囲で出力 ---##
    elif Method == 'qb-p' or Method == 'wb-p':
        if Method == 'qb-p' :
            bd = QeBand(ef, file_nscf_in, file_band_out, file_band_gnu)
            Title = "{}\nQeBand-pdos".format(Prefix)
        elif Method == 'wb-p' :
            bd = WannierBand(ef, file_labelinfo, file_band_dat)
            Title = "{}\nWannier-pdos".format(Prefix)
        ds = Dos(ef, [[file_pdos_tot, 0, 2], [file_pdos_tot, 0, 1]])

        #---page0---#
        if len(optEneScale) == 3:
            bdp_single_width = Pm.bd_single_width.copy()
            bdp_single_width.append(Pm.bd_single_width[0]*6/10)
            fig, ax = Md.MakeAxesTable(bdp_single_width, Pm.bd_single_height, \
                                       margin=Pm.bdp_single_margin, \
                                       width = 25, height=13)
            for i in range(len(ax)):
                BandSinglePlot(ax[i][0], bd.values, bd.kpoints, optEneScale, \
                               Ecenter=Ecenter, bdcolor=bdcolor) 
                DosPlot(ax[i][1], ds.values, optEneScale, Ecenter=Ecenter, Elabel=False)
                ax[i][0].tick_params('x', labelsize=18)         
                ax[i][0].tick_params('y', labelsize=16)         
                ax[i][1].tick_params('x', labelsize=16)         
                ax[i][1].tick_params('y', labelsize=16)         
                ax[i][0].set_ylabel(Pm.text_Elabel, fontsize=22, \
                                    labelpad=Pm.E_label_pad)
            plt.savefig(pp, format='pdf')
            fig.clf()

        #---page1,2---#
        EneScale = np.array(Pm.bd_table_ESl).reshape(2,3,3).tolist()
        for page in range(2):
            if page != 0 : Title = ""
            fig, ax = Md.MakeAxesTable(Pm.bdp_table_width, Pm.bdp_table_height, \
                                       margin=Pm.bdp_table_margin, Title=Title, header=Pm.header)
            for i in range(len(ax)):
                BandSinglePlot(ax[i][0], bd.values, bd.kpoints, \
                              EneScale[page][i], Ecenter=Ecenter, bdcolor=bdcolor)
                DosPlot(ax[i][1], ds.values, EneScale[page][i], \
                        Ecenter=Ecenter, Elabel=False)
            plt.savefig(pp, format='pdf')
            fig.clf()
        
        #---page3---#
        bdp_detail_width = Pm.bd_detail_width.copy()
        bdp_detail_width.append(Pm.bd_detail_width[0]*6/10)
        fig, ax = Md.MakeAxesTable(bdp_detail_width, Pm.bd_detail_height, \
                                       margin=Pm.bdp_detail_margin, width = 25)
        for i in range(len(ax)):
            BandSinglePlot(ax[i][0], bd.values, bd.kpoints, Pm.bd_detail_ESl, \
                    Ecenter=Ecenter, bdcolor=bdcolor, detailgrid=True, MinorScale=0.2)
            DosPlot(ax[i][1], ds.values, Pm.bd_detail_ESl, Ecenter=Ecenter, \
                    Elabel=False, detailgrid=True, MinorScale=0.2)
        plt.savefig(pp, format='pdf')
        fig.clf()

        pp.close()
    
    ## qb-wb:: qebandとWannierbandの比較を6つの範囲で出力
    elif Method == 'qb-wb' :
        qb = QeBand(ef, file_nscf_in, file_band_out, file_band_gnu)
        wb = WannierBand(ef, file_labelinfo, file_band_dat)
        qb_values=[]
        for value in qb.values:
            adjust_qb_xvalue=AdjustXvalue(value[0], qb.kpoints[1][-1], wb.kpoints[1][-1])
            qb_values.append([adjust_qb_xvalue, value[1]])
        Title = "{}\nQe-WannierBand".format(Prefix)

        #---page0---#
        if len(optEneScale) == 3:
            fig, ax = Md.MakeAxesTable(Pm.bd_single_width, Pm.bd_single_height, \
                                       margin=Pm.bd_single_margin)
            for i in range(len(ax)):
                for j in range(len(ax[0])):
                    BandComparePlot(ax[i][j], qb_values, wb.values, wb.kpoints, \
                                  optEneScale, Ecenter=Ecenter) 
                    ax[i][j].tick_params('x', labelsize=18)         
                    ax[i][j].tick_params('y', labelsize=16)         
                    ax[i][j].set_ylabel(Pm.text_Elabel, fontsize=22, labelpad=Pm.E_label_pad)
            plt.savefig(pp, format='pdf')
            fig.clf()

        #---page1---#
        fig, ax = Md.MakeAxesTable(Pm.bd_table_width, Pm.bd_table_height, \
                                   margin=Pm.bd_table_margin, Title=Title)
        EneScale = np.array(Pm.bd_table_ESl).reshape(3,2,3).tolist()
        for i in range(len(ax)):
            for j in range(len(ax[0])):
                BandComparePlot(ax[i][j], qb_values, wb.values, wb.kpoints, \
                               EneScale[i][j], Ecenter=Ecenter)
        plt.savefig(pp, format='pdf')
        fig.clf()

        #---page2---#
        # 詳細なgridの追加
        fig, ax = Md.MakeAxesTable(Pm.bd_detail_width, Pm.bd_detail_height, \
                                   margin=Pm.bd_detail_margin)
        for i in range(len(ax)):
            for j in range(len(ax[0])):
                BandComparePlot(ax[i][j], qb_values, wb.values, wb.kpoints, \
                               Pm.bd_detail_ESl, Ecenter=Ecenter, \
                               detailgrid=True, MinorScale=0.2)
        plt.savefig(pp, format='pdf')
        fig.clf()
        
        pp.close()







