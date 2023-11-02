
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
xmax=0.75
xmin=0.25
ymax=1.7
ymin=1.2
zmax=0.2
zmin=-0.2
def cminch(cm: float) -> float:
        return cm * 0.3937
def is_under_ssh_connection():
    return 'SSH_CONNECTION' in os.environ.keys()

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
    with open("bd_plane.dat", 'r') as f_bdp_dat:
        lines = [ line.split() for line in f_bdp_dat.readlines() ]

    value21 = np.array([ [ float(line[j]) for j in range(3) ] for line in lines ])
    value22 = np.array([ [ float(line[j]) for j in range(3,6) ] for line in lines ])
    value23 = np.array([ [ float(line[j]) for j in range(6,9) ] for line in lines ])
    value24 = np.array([ [ float(line[j]) for j in range(9,12) ] for line in lines ])

    if is_under_ssh_connection(): 
        mpl.use('TkAgg')
        #----- Default Font in remote -----#
        plt.rcParams["mathtext.fontset"] = "cm"   #texfont
        plt.rcParams['font.size']=12
    else :
        #----- Default Font in local -----#
        plt.rcParams["font.serif"] = "Times New Roman"
        plt.rcParams["font.family"] = "serif"
B
        plt.rcParams["mathtext.fontset"] = "cm"   #texfont
        plt.rcParams['font.size']=12

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
