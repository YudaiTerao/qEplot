
"""
Usage:
    sfplot.py <bd_plane_dat> [-n <band_num_range]
    sfplot.py <bp_result_dir> <bd_min_num> <bd_max_num> [-s <save_prefix]

Options:
    <bd_plane_dat>      過去に計算したdat_file
    -n <band_num_range> plotするbandindexのrange
    <bp_result_dir>     bandplaneの計算を行ったディレクトリ, bp0~bpNのディレクトリとscf.outが入っている必要がある。
    <bd_min_num>        plotするbandのindexの最小値
    <bd_max_num>        plotするbandのindexの最大値
    -s <save_prefix>    datの出力名
"""

from docopt import docopt
import os
import re
import sys
import glob
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

sys.path.append('/home/yudai/code/qEplot/')
import plotParameter as Pm
import plotModule as Md
Pm.mpl_init()
def cminch(cm: float) -> float:
    return cm * 0.3937

xmax=0.75
xmin=0.25
ymax=1.7
ymin=1.2
zmax=0.2
zmin=-0.2

#bp0~bpNのディレクトリに入っているWannierから計算されたband.datから,bandの2次元データを作成する
#作成されたdatから2次元面でのbandを3次元的に出力


def read_win():
    
def read_band_dat(file_band_dat, ef):
    values = [[[],[]]]
    with open(file_band_dat, "r") as f_bd_dat
        lines = [ line.split() for line in f_bd_dat.readlines() ]
    j = k = 0
    for i, line in enumerate(lines):
        if ( len(line) < 1 ):
            values[k][0] = [ float(lines[n][0]) for n in range(j,i) ]
            values[k][1] = [ float(lines[n][1]) - ef for n in range(j,i) ]
            values.extend([[[],[]]])
            j = i+1
            k += 1
    return values

def sfplot(ax, value):
    x0=np.reshape(value[:, 0], (101,174))
    y0=np.reshape(value[:, 1], (101,174))
    z0=np.reshape(value[:, 2], (101,174))

    x=x0[(x0[:, 0] > xmin) & (x0[:, 0] < xmax),:]
    x=x[:,(y0[0] > ymin) & (y0[0] < ymax)]
    y=y0[(x0[:, 0] > xmin) & (x0[:, 0] < xmax),:]
    y=y[:,(y0[0] > ymin) & (y0[0] < ymax)]
    z=z0[(x0[:, 0] > xmin) & (x0[:, 0] < xmax),:]
    z=z[:,(y0[0] > ymin) & (y0[0] < ymax)]
    z=np.clip(z, zmin, zmax)
    ax.plot_surface(x, y, z, alpha=0.4)

if __name__ == '__main__':
    args = docopt(__doc__)
    if args['<bd_plane_dat>'] is None:
        dir = args['<bp_result_dir>']
        if dir[-1] == "/": dir = dir[:-1]
        bd_index = range(int(args['<bd_min_num>']), int(args['<bd_max_num>']))
        ymesh=0
        for file in filelist(dir):
            f = re.sub("^"+dir, "", file)
            if  ".scf.out" in file: 
                file_scf_out = file
                if args['-s'] is None: 
                    save_filename = f.replace(".scf.out", "").replace("/", "")
                else: save_filename="{}_anc.dat".format(args["-s"])
            elif re.fullmatch("^bp[0-9]{1,3}$", f): ymesh = ymesh + 1

        totE, ef, totM, absM = Md.read_scf_out(file_scf_out)

        #db_vec: y方向の
        kp_start1, kp_end1, xmesh = read_win("{}/bp1/bp1_win".format(dir))
        db_vec = kp_start1 - kp_start0

        xside = np.linalg.norm(kp_end0-kp_start0) 
        yside = np.linalg.norm(db_vec) * (ymesh-1)

        for ym in range(ymesh)
            kp_start, kp_end, xmesh=read_win("{0}/bp{1}/bp{1}_win".format(dir, ym))
            values = read_band_dat("bp{0}/bp{0}_band.dat".format(ym), ef)

            for value in values[ bd_index[0] - 1, bd_index[-1] ]
                length = 
                x , y = 

        
    with open("bd_plane.dat", 'r') as f_bdp_dat:
        lines = [ line.split() for line in f_bdp_dat.readlines() ]

    value21 = np.array([ [ float(line[j]) for j in range(3) ] for line in lines ])
    value22 = np.array([ [ float(line[j]) for j in range(3,6) ] for line in lines ])
    value23 = np.array([ [ float(line[j]) for j in range(6,9) ] for line in lines ])
    value24 = np.array([ [ float(line[j]) for j in range(9,12) ] for line in lines ])

    #--- figとaxesの作成 ---#
    fig = plt.figure(figsize=(cminch(20),cminch(18)))
    ax = fig.add_axes([ 0.05, 0.05, 0.9, 0.9], projection='3d')
    ax.set_aspect('equal')


    sfplot(ax, value21)
    sfplot(ax, value22)
    sfplot(ax, value23)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_zlim([zmin, zmax])
    plt.show()
