"""
Usage:
    bd_plane_plot.py <file_curv_dat> [-r <curv_row>] [-s <style>]

Options:
    <file_curv_dat> datfile
    -r <curv_row>   curv_datのcurvの行数 [default: 3-6]
    -s <style>      plotのstyle, 3d or 2d [default: 3d]
"""

from docopt import docopt
import os
import sys
import re
import glob
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

sys.path.append('/home/terao/.qEcalc/qEplot/')
import plotParameter as Pm
import plotModule as Md
Pm.mpl_init()

def cminch(cm: float) -> float:
        return cm * 0.3937

def read_curv_dat(file_curv_dat, curv_row):
    with open(file_curv_dat, 'r') as fcd:
        lines = [ l.split() for l in fcd.readlines()[4:] ]
    lines = np.array([ l for l in lines if len(l) > 1 ])

    ##空白行までの行数を数えることでmeshを調べる
    #for i, line in enumerate(lines):
    #    if len(line) < 1:
    #        mesh = [ len(lines[:i]) ]
    #        break

    ##直交するmeshは全体のline数から割ることで求める
    #mesh.append( int(len(lines)/mesh[0]) )

    kp = np.array([ [ float(x) for x in line[:3] ] for line in lines ])
    curv = np.array([ [ float(x) for x in line[curv_row[0]:curv_row[1]] ] for line in lines ])
    normmax = np.array([ np.linalg.norm(cv) for cv in curv ]).max()
    xside = kp[:, 0].max() - kp[:, 0].min()
    yside = kp[:, 1].max() - kp[:, 1].min()
    meshsize = np.sqrt(xside * yside / len(kp) )
    curv = [ cv * meshsize / normmax for cv in curv ]
    return kp, np.array(curv)

def kp_trans(kp):
    return np.array([ [ k[0], k[1] ] for k in kp ])

def sfplot(ax, kp, curv):
    #ここでのkpは2成分のみ。
    #datの3次元のkpから平面の座標に変換し、そのkpをここに入れる

    for i, k in enumerate(kp):
        ax.quiver(k[0], k[1], 0, curv[i][0], curv[i][1], curv[i][2],
                  color='red', arrow_length_ratio=0.05, lw=1)

    xmax = kp[:, 0].max()
    xmin = kp[:, 0].min()
    ymax = kp[:, 1].max()
    ymin = kp[:, 1].min()
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_box_aspect((1, (ymax-ymin)/(xmax-xmin), 1))

if __name__ == '__main__':
    args = docopt(__doc__)
    curv_row = [ int(x) for x in args['-r'].split('-') ]

    kp, curv = read_curv_dat(args['<file_curv_dat>'], curv_row)

    if args['-s'] == '2d':
        kp = kp_trans(kp)

    elif args['-s'] == '3d':
        #--- figとaxesの作成 ---#
        fig = plt.figure(figsize=(cminch(20),cminch(18)))
        ax = fig.add_axes([ 0.05, 0.05, 0.9, 0.9], projection='3d')

        sfplot(ax, kp, curv)
        plt.show()



