
"""
Usage:
  projband_plot.py <dir> [-e <EneScale>] [-o <Ecenter>]
  projband_plot.py (-d <dir>...) [-e <EneScale>] [-o <Ecenter>]

Options:
  -d <dir>         resultの入っているdir(複数選択可)
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
import qEplot.banddos_plot as qp
pt.mpl_init()

def read_wout(file_wout):
    with open(file_wout, 'r') as f_wout:
        lines = f_wout.readlines()
    flag, WF_dict = 0, {}
    for line in lines:
        if 'Final State' in line: flag = 1
        if 'WF centre and spread' in line and flag == 1:
            WF_No = int(line.split()[4])
            if len(line.split()[11:]) == 0:
                WF_dict[WF_No] = "WF{}".format(WF_No)
            else :
                for i, wstr in enumerate(line.split()[11:]):
                    if i == 0: WF_dict[WF_No] = wstr
                    else : WF_dict[WF_No] += '_' + wstr
    return WF_dict


######################
class plotoption():
    def __init__(self):
        #----- 引数処理 -----#
        args = docopt(__doc__)
        self.optEneScale = [ float(x) for x in args['-e'].split('-') ]
        self.Ecenter = float(args['-o'])

        self.file_band_dat = []
        files = []
        self.WF_No = []
        if type(args['<dir>']) != list :
            dirlist = [ args['<dir>'] ]
        else: dirlist = args['<dir>'].copy()
        print(dirlist)
        for dir in dirlist: files = files + pt.filelist(dir)
        for file in files:
            if   ".scf.out" in file: self.file_scf_out=file
            elif "_band.dat" in file: self.file_band_dat.append(file)
            elif ".labelinfo.dat" in file: self.file_labelinfo=file
            elif "wout" in file: self.WF_dict = read_wout(file)

        for fbd in self.file_band_dat:
            for i, dir in enumerate(dirlist): 
                if i == 0: wfn = fbd.replace(dir, "").replace("_band.dat", "").replace("/", "")
                else:      wfn = wfn.replace(dir, "")
            self.WF_No.append(int(wfn.replace("WF", "")))
        self.totE, self.ef, self.totM, self.absM = pt.read_scf_out(self.file_scf_out)

def bandplot():
    op = plotoption()

    graphnum = len(op.file_band_dat)
    ### graph数に応じて横幅や余白等を決める ###
    if   graphnum == 1 : wn, hn, w, h, m, ts, ls = [1] * 1, [1] * 1, 18, 20, 2.0, 18, 22
    elif graphnum <= 2 : wn, hn, w, h, m, ts, ls = [1] * 2, [1] * 1, 30, 20, 2.5, 18, 20
    elif graphnum <= 4 : wn, hn, w, h, m, ts, ls = [1] * 2, [1] * 2, 25, 20, 1.5, 15, 16
    elif graphnum <= 6 : wn, hn, w, h, m, ts, ls = [1] * 3, [1] * 2, 30, 20, 1.5, 15, 16
    elif graphnum <= 9 : wn, hn, w, h, m, ts, ls = [1] * 3, [1] * 3, 23, 20, 1.0, 11, 9
    elif graphnum <= 12: wn, hn, w, h, m, ts, ls = [1] * 4, [1] * 3, 30, 20, 1.0, 11, 9
    fig, ax = pt.MakeAxesTable(wn, hn, width=w, height=h, margin=m)

    for n, fbd in enumerate(op.file_band_dat):
        bd = qp.WannierBand(op.ef, op.file_labelinfo, fbd)
        i = n // len(wn)
        j = n % len(wn)
        pt.ProjBandPlot(ax[i][j], fig, bd.values, bd.kpoints, op.optEneScale, Ecenter=op.Ecenter)
        ax[i][j].tick_params('x', labelsize=ls)
        ax[i][j].tick_params('y', labelsize=ls)
        ax[i][j].set_ylabel("")
        ax[i][j].annotate(op.WF_dict[op.WF_No[n]], (0.5, 1.01), xycoords='axes fraction', fontsize=ts, va='bottom', ha='center')
    #fig.colorbar(sc)
    plt.show()

if __name__=='__main__': bandplot()


