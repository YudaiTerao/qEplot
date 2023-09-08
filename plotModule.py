
import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import axes as a
import plotParameter as Pm

def cminch(cm: float) -> float:
        return cm * 0.3937

def Eaxis(ax: a.Axes, axis, EneScale, detailgrid=False, MinorScale=1):
    Emax = EneScale[0] * EneScale[1] 
    Emin = EneScale[0] * EneScale[2] * -1
    Eticks = np.arange(Emin, Emax+EneScale[0], EneScale[0])
    Etickslabel = [ "{:.1f}".format(l) for l in Eticks ]
    ax.tick_params(axis=axis, which='major', direction='in', \
                   pad=Pm.E_ticks_pad, width=Pm.ticks_width, length=Pm.ticks_length)
    eval("ax.set_{}lim".format(axis))(Emin, Emax)
    eval("ax.set_{}ticks".format(axis))(Eticks, minor=False)
    eval("ax.set_{}ticklabels".format(axis))(Etickslabel, minor=False, fontdict=Pm.fontdict_Eticks)
    eval("ax.set_{}label".format(axis))(Pm.text_Elabel, fontdict=Pm.fontdict_Elabel, \
                                        labelpad=Pm.E_label_pad )

    #FermiLine
    ax.grid(visible=True, axis=axis, which='major', lw=Pm.Fermi_line_width, c="black")
    gridlines=eval("ax.get_{}gridlines".format(axis))()
    for i, grid in enumerate(gridlines):
        if i != EneScale[2] :
            if detailgrid : grid.set_linewidth(0.6)
            else          : grid.set_linewidth(0)

    #DetailGrid
    if detailgrid :
        Eminorticks = np.arange(Emin, Emax+MinorScale, MinorScale)
        ax.tick_params(axis=axis, which='minor', direction='in', \
                       width=Pm.ticks_width/2, length=Pm.ticks_length/2)
        ax.grid(visible=True, axis=axis, which='minor', lw=0.2, c='gray')
        eval("ax.set_{}ticks".format(axis))(Eminorticks, minor=True)
        eval("ax.set_{}ticks".format(axis))(Eminorticks, minor=True)


def MakeAxesTable(ax_column_width, ax_row_height, margin=Pm.margin, header="", height=Pm.height, width=Pm.width, Title="")
#ax_column_width, ax_row_heightは比で記述
#ax_column_widthとax_row_heightはtableの列,行の幅,高さの配列
#height, widthは全体の用紙の大きさで単位はcm
#header, marginもすべてcmで指定
    if header == "": 
        if Title !="": header = Pm.header
        else : header = margin
    fig = plt.figure(figsize=(cminch(width),cminch(height)))
    cn = len(ax_column_width)
    rn = len(ax_row_height)
    
    #sw, sh:: axes_sum_width,axes_sum_height, axesのwidth,heightの合計(cm単位)
    #wrate, hrate:: axesの長さ比の合計
    sw = width - margin * (cn+1)
    sh = height - margin * cn - header
    wrate = sum(ax_column_width)
    hrate = sum(ax_row_height)
    if sw * hrate >= sh * wrate:
        cmrate = sh/hrate
        rlmargin = (sw - wrate * cmrate)/2
        tbmargin = 0
    elif sh * wrate > sw * hrate
        cmrate = sw/wrate
        rlmargin = 0
        tbmargin = (sh - hrate * cmrate)/2

    #----- Titleの作成 -----#
    header_ycenter = (height - header / 2) / height
    fig.text(0.5, header_ycenter, Title, ha='center', va='center', fontdict=Pm.fontdict_title, linespacing=1.5)
    
    #----- Axesの追加 -----#
    ax = [[0] * cn  for i in [0] * rn]
    for i in range(rn):
        for j in range(cn):
            x0 = (sum(ax_column_width[:j])*cmrate+margin*(j+1)+rlmargin)/width
            y0 = (sum(ax_row_height[i+1:])*cmrate+margin*(rn-i)+tbmargin)/height
            w = ax_column_width[j]*cmrate/width
            h = ax_row_height[i]*cmrate/height
            ax[i][j] = fig.add_axes([ x0, y0, w, h ])

    return fig, ax
    
