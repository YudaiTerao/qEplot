
import numpy as np
import pandas as pd
from scipy.constants import *

from matplotlib import pyplot as plt
from matplotlib import axes as a
from matplotlib import rc

import sys
sys.path.append('../qEplot')
import plotParameter as Pm
import plotModule as Md

Pm.mpl_init()
ef1 = 15.7884
ef2 = 12.8375
file1 = "/home/yudai/code/calc_anc/Mn3Al-ahc-fermiscan.dat"
file2 = "/home/yudai/code/calc_anc/CrFeS2_S-ahc-fermiscan.dat"
save1 = "Mn3Al_ANC.dat"
save2 = "CrFeS2_S_ANC.dat"

T=np.arange(50, 1001, 50)
T=np.insert(T, 0, 1)

ef=ef2
save_filename = save2
file_AHC_dat = file2


def read_dat(file_AHC_dat, ef: float):
    with open(file_AHC_dat, 'r') as f_ahc_dat:
        lines = f_ahc_dat.readlines()
    Ene = [ float(line.split()[0])-ef for line in lines ]
    AHC = [ -float(line.split()[3]) for line in lines ]
    return Ene, AHC


def calc_anc(Ene, AHC, T):
    cosh_cutoff=200
    beta=1/(k*T)
    #LはAHCの外挿の収束距離, 端のデータ点の振る舞いが変わる
    L=(Ene[1]-Ene[0])*5
    #ep_mu: ε-μ のこと
    #分母のcoshの中身がcutoffを超えると全体として小さいため、積分計算に含めない
    ep_mu_max=((cosh_cutoff/beta)/e)
    ep_step=ep_mu_max*2/10000
    ep_mu_mesh=np.arange(-1*ep_mu_max, ep_mu_max, ep_step)
    df_dep_mesh=[ -1/(2+2*np.cosh(beta*e*(ep_mu))) for ep_mu in ep_mu_mesh ]

    ANClist=[]
    for mu in Ene :
        ep_mesh=[ ep_mu+mu for ep_mu in ep_mu_mesh ]
        sgm_mesh=[]
        for ep in ep_mesh:
            flag=0
            for i,E in enumerate(Ene):
                if ep < E : 
                    flag=1
                    break
            #与えられたEneの範囲にepがなければ外挿する
            if ( i == 0 ) and ( flag == 1 ) :
                a = (AHC[1]-AHC[0])/(Ene[1]-Ene[0])
                sgm=AHC[0]-a*(Ene[0]-ep)*np.exp(-(Ene[0]-ep)/L)
            elif ( i == len(Ene)-1 ) and ( flag == 0 ) :
                a=(AHC[i]-AHC[i-1])/(Ene[i]-Ene[i-1])
                sgm=AHC[i]+a*(ep-Ene[i])*np.exp(-(ep-Ene[i])/L)

            #Eneの範囲内ならば線形に内挿してahcのデータ点を得る
            else :
                a=(AHC[i]-AHC[i-1])/(Ene[i]-Ene[i-1])
                sgm=AHC[i-1]+a*(ep-Ene[i-1])
            sgm_mesh.append(sgm)
            #sgm_mesh, ep_meshが内挿によって得た新たなデータ点のlist
            #ep_meshはmuを中心としたcosh_cutoffを満たす範囲内を1000点に分割する
            #sgm_meshはAHCのリストから線形に内挿することにより得ている
            #Eneの定義域を超えた点のsgm_meshは距離で指数収束する外挿により得ている

        #----- ANCの計算 -----#
        ANC=0
        for i, ep_mu in enumerate(ep_mu_mesh):
            ANC=ANC+sgm_mesh[i]*ep_mu*df_dep_mesh[i]
        ANC=ANC*ep_step*beta/T
        ANC=ANC*100*e/T #eは分子に2つ分母に1つで1つ残る
        ANClist.append(ANC)

    return ANClist

#----- plotしてpdf化 -----#

def AHCplot(ax: a.Axes, Ene, AHC):
    ax.plot( Ene, AHC, c='black' ) 
    Md.Eaxis(ax, 'x', [0.1, 3, 3]) 
    Md.addlabel(ax, 'y', r"$\sigma_{ij}\;\;\rm{[S/cm]}$")


def ANCplot(ax: a.Axes, Ene, AHC, T):
    ANC = calc_anc(Ene, AHC, T)
    ax.plot( Ene, ANC, c='black' )
    Md.Eaxis(ax, 'x', [0.1, 3, 3])
    Md.addgrid(ax, 'y')
    Md.addlabel(ax, 'y', r"$\alpha_{ij}$")


fig, ax = Md.MakeAxesTable([10,10], [10,10], 5, height=100, width=30)
T=[1,100,300,500]

Ene, AHC = read_dat(file1, ef1)
AHCplot(ax[0][0], Ene, AHC)
for i in range(len(T)):
    ANC=calc_anc(Ene, AHC, T[i])
    ax[1][0].plot( Ene, ANC, c=Pm.Colorlist(i), label="T={}".format(T[i]) )
Md.Eaxis(ax[1][0], 'x', [0.1, 3, 3])
Md.addlabel(ax[1][0], 'y', r"$\alpha_{ij}/\rm{T}\;\;[AK^{-2}m^{-1}]$")
ax[1][0].legend(loc="center", bbox_to_anchor=(0.6, 0.6, 0.28, 0.38), fontsize=11)
ax[1][0].set_ylim(-0.03,0.03)
Md.addgrid(ax[1][0], 'y')

Ene, AHC = read_dat(file2, ef2)
AHCplot(ax[0][1], Ene, AHC)
for i in range(len(T)):
    ANC=calc_anc(Ene, AHC, T[i])
    ax[1][1].plot( Ene, ANC, c=Pm.Colorlist(i), label="T={}".format(T[i]) )
Md.Eaxis(ax[1][1], 'x', [0.1, 3, 3])
Md.addlabel(ax[1][1], 'y', r"$\alpha_{ij}/\rm{T}\;\;[AK^{-2}m^{-1}]$")
ax[1][1].legend(loc="center", bbox_to_anchor=(0.1, 0.1, 0.28, 0.38), fontsize=11)
ax[1][1].set_ylim(-0.06,0.06)
Md.addgrid(ax[1][1], 'y')

plt.savefig('ANC_T.pdf', format='pdf')


#fig, ax = Md.MakeAxesTable([10,10], [10,10,10,10,10], 3.5, height=100)
#
#T=[500]
#
#Ene, AHC = read_dat(file1, ef1)
#AHCplot(ax[0][0], Ene, AHC)
#for i in range(len(T)): 
#    ANCplot(ax[i+1][0], Ene, AHC, T[i])
#    ax[i+1][0].set_ylim(-3,3)
#Ene, AHC = read_dat(file2, ef2)
#AHCplot(ax[0][1], Ene, AHC)
#for i in range(len(T)): 
#    ANCplot(ax[i+1][1], Ene, AHC, T[i])
#    ax[i+1][1].set_ylim(-4,4)
#
#plt.savefig('ANC_integralahcT2.pdf', format='pdf')


#Ene, AHC = read_dat(file_AHC_dat = file_AHC_dat, ef = ef)
#
#ANC=[]
#
#ANC_df = pd.DataFrame(data = Ene, columns = ["Ene"])
#for i in range(len(T)): 
#    ANC=calc_anc(Ene, AHC, T[i])
#    ANC_df[T[i]] = ANC
#    print("Temperature {} end".format(T[i]))
#with open ("{}".format(save_filename), 'w') as f:
#    f.write(ANC_df.to_string(index=False))




