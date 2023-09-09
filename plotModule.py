
import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import axes as a
from matplotlib import patches 
import plotParameter as Pm

def cminch(cm: float) -> float:
        return cm * 0.3937

def Eaxis(ax: a.Axes, axis, EneScale, Ecenter=0, detailgrid=False, MinorScale=1):
    Emax = (EneScale[0] * EneScale[1]) + Ecenter
    Emin = (EneScale[0] * EneScale[2] * -1) + Ecenter
    Eticks = np.arange(Emin, Emax+EneScale[0], EneScale[0])
    dig = [0]
    if '.' in str(EneScale[0]): dig.append(len(str(EneScale[0]).split('.')[1]))
    if '.' in str(Ecenter): dig.append(len(str(Ecenter).split('.')[1]))
    dig = max(dig)
    Etickslabel = [ "{lb:.{d}f}".format(lb=x, d=dig) for x in Eticks ]
    ax.tick_params(axis=axis, pad=Pm.E_ticks_pad)
    eval("ax.set_{}lim".format(axis))(Emin, Emax)
    eval("ax.set_{}ticks".format(axis))(Eticks)
    eval("ax.set_{}ticklabels".format(axis))(Etickslabel)
    eval("ax.set_{}label".format(axis))(Pm.text_Elabel, \
                          fontdict=Pm.fontdict_Elabel, labelpad=Pm.E_label_pad)

    #FermiLine
    ax.grid(visible=True, axis=axis, which='major', \
            lw=Pm.Fermi_line_width, c="black")
    gridlines=eval("ax.get_{}gridlines".format(axis))()
    for i, grid in enumerate(gridlines):
        if i != EneScale[2] :
            if detailgrid : grid.set_linewidth(Pm.detail_maingrid_lw)
            else          : grid.set_linewidth(0)

    #DetailGrid
    if detailgrid :
        Eminorticks = np.arange(Emin, Emax+MinorScale, MinorScale)
        ax.grid(visible=True, axis=axis, which='minor', \
                lw=Pm.detail_subgrid_lw, c='gray')
        eval("ax.set_{}ticks".format(axis))(Eminorticks, minor=True)
        eval("ax.set_{}ticks".format(axis))(Eminorticks, minor=True)

def Kaxis(ax: a.Axes, axis, kpoints):
    Kmax = kpoints[1][-1]
    Kmin = kpoints[1][0]
    Kticks = kpoints[1]
    Ktickslabel = kpoints[0]

    ax.tick_params(axis=axis, pad=Pm.K_ticks_pad, width=0, length=0 )
    ax.grid(visible=True, axis=axis, which='major', lw=Pm.K_line_width, c="black")
    eval("ax.set_{}lim".format(axis))(Kmin, Kmax)
    eval("ax.set_{}ticks".format(axis))(Kticks, minor=False)
    eval("ax.set_{}ticklabels".format(axis))(Ktickslabel, minor=False, \
                                             fontdict=Pm.fontdict_Kticks)

def MakeAxesTable(ax_column_width, ax_row_height, margin=Pm.margin, header="", height=Pm.height, width=Pm.width, Title=""):
#ax_column_width, ax_row_heightは比で記述
#ax_column_widthとax_row_heightはtableの列,行の幅,高さの配列
#height, widthは全体の用紙の大きさで単位はcm
#header, marginもすべてcmで指定
    if header == "": 
        if Title != "": header = Pm.header
        else : header = margin
    fig = plt.figure(figsize=(cminch(width),cminch(height)))
    cn = len(ax_column_width)
    rn = len(ax_row_height)
    
    #sw, sh:: axes_sum_width,axes_sum_height, axesのwidth,heightの合計(cm単位)
    #wrate, hrate:: axesの長さ比の合計
    sw = width - margin * (cn+1)
    sh = height - margin * rn - header
    wrate = sum(ax_column_width)
    hrate = sum(ax_row_height)
    if sw * hrate >= sh * wrate:
        cmrate = sh/hrate
        rlmargin = (sw - wrate * cmrate)/2
        tbmargin = 0
    elif sh * wrate > sw * hrate:
        cmrate = sw/wrate
        rlmargin = 0
        tbmargin = (sh - hrate * cmrate)/2

    #----- Titleの作成 -----#
    header_ycenter = (height - header / 2) / height
    fig.text(0.5, header_ycenter, Title, ha='center', va='center', \
             fontdict=Pm.fontdict_title, linespacing=1.5)
    
    #----- Axesの追加 -----#
    ax = [[0] * cn  for i in [0] * rn]
    for i in range(rn):
        for j in range(cn):
            x0 = (sum(ax_column_width[:j])*cmrate+margin*(j+1)+rlmargin)/width
            y0 = (sum(ax_row_height[i+1:])*cmrate+margin*(rn-i)+tbmargin)/height
            w = ax_column_width[j]*cmrate/width
            h = ax_row_height[i]*cmrate/height
            ax[i][j] = fig.add_axes([ x0, y0, w, h ])
    
    
   # fig.add_artist(patches.Rectangle(xy=(0, 0), width=1, height=tbmargin/height, ec='#000000', fill=True))
   # fig.add_artist(patches.Rectangle(xy=(0, (height-header-tbmargin)/height), width=1, height=tbmargin/height, ec='#000000', fill=True))
   # fig.add_artist(patches.Rectangle(xy=(0, 0), width=rlmargin/width, height=0, ec='#000000', fill=True))
   # fig.add_artist(patches.Rectangle(xy=((width-rlmargin)/width, 0), width=rlmargin/width, height=0, ec='#000000', fill=True))
   # fig.add_artist(patches.Rectangle(xy=(0, (height-header)/height), width=1, height=header/height, ec='#000000', fill=True))
    

    return fig, ax
    
