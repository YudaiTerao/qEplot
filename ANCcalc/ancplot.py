
"""
Usage:
    ancplot.py <anc_dat>
    ancplot.py <ahc_result_dir> <axis> <T> [-s <save_prefix]

Options:
    <anc_dat>           $B2a5n$K7W;;$7$?(Bdat_file
    <ahc_result_dir>    ahc$B$N7W;;$r9T$C$?%G%#%l%/%H%j(B
    <axis>              x,y,z
    <T>                 $B29EY(B, 3$B$D;XDj(B, ancdat$B$,$J$$$H$-$OI,?\(B
    -s <save_prefix>    ancdat$B$N=PNOL>(B
"""

from docopt import docopt
import os
import sys
import glob
import numpy as np
import pandas as pd
from scipy.constants import *

from matplotlib import pyplot as plt
from matplotlib import axes as a
from matplotlib import rc

sys.path.append('/home/yudai/code/qEplot/')
import plotParameter as Pm
import plotModule as Md
Pm.mpl_init()

cosh_cutoff=200


def read_anc_dat(file_anc_dat):
    #anc_dat: 1$BNsL\(B:Energy, 2$BNsL\(B:ahc, 3$BNsL\0J9_(B:$B3F29EY$N(Banc
    #1$B9TL\$O(B  > Ene  ahc  T[0]  T[1]....$B$H$$$&$h$&$K=q$$$F$"$k(B
    with open(file_anc_dat, 'r') as f_anc_dat:
        lines = np.array([ line.split() for line in f_anc_dat.readlines() ])
    T=[ float(t) for t in lines[0][2:] ]
    anclist = [ [ float(x) for x in lines[1:][:, i] ] for i in range(len(lines[0])) ]
    return T, anclist[0], anclist[1], anclist[2:]

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

def read_ahc_dat(file_ahc_dat, ef: float, ahcrow):
    with open(file_ahc_dat, 'r') as f_ahc_dat:
        lines = f_ahc_dat.readlines()
    Ene = [ float(line.split()[0])-ef for line in lines ]
    AHC = [ -float(line.split()[ahcrow]) for line in lines ]
    return Ene, AHC

def calc_anc(Ene, AHC, T):
    beta=1/(k*T)
    #L$B$O(BAHC$B$N30A^$N<}B+5wN%(B, $BC<$N%G!<%?E@$N?6$kIq$$$,JQ$o$k(B
    L=(Ene[1]-Ene[0])*5
    #ep_mu: $B&E(B-$B&L(B $B$N$3$H(B
    #$BJ,Jl$N(Bcosh$B$NCf?H$,(Bcutoff$B$rD6$($k$HA4BN$H$7$F>.$5$$$?$a!"@QJ,7W;;$K4^$a$J$$(B
    ep_mu_max=((cosh_cutoff/beta)/e)
    ep_step=ep_mu_max*2/10000
    ep_mu_mesh=np.arange(-1*ep_mu_max, ep_mu_max, ep_step)
    df_dep_mesh=[ -1/(2+2*np.cosh(beta*e*(ep_mu))) for ep_mu in ep_mu_mesh ]

    ANC_list=[]
    for mu in Ene :
        ep_mesh=[ ep_mu+mu for ep_mu in ep_mu_mesh ]
        sgm_mesh=[]
        for ep in ep_mesh:
            flag=0
            for i,E in enumerate(Ene):
                if ep < E : 
                    flag=1
                    break
            #$BM?$($i$l$?(BEne$B$NHO0O$K(Bep$B$,$J$1$l$P30A^$9$k(B
            if ( i == 0 ) and ( flag == 1 ) :
                a = (AHC[1]-AHC[0])/(Ene[1]-Ene[0])
                sgm=AHC[0]-a*(Ene[0]-ep)*np.exp(-(Ene[0]-ep)/L)
            elif ( i == len(Ene)-1 ) and ( flag == 0 ) :
                a=(AHC[i]-AHC[i-1])/(Ene[i]-Ene[i-1])
                sgm=AHC[i]+a*(ep-Ene[i])*np.exp(-(ep-Ene[i])/L)

            #Ene$B$NHO0OFb$J$i$P@~7A$KFbA^$7$F(Bahc$B$N%G!<%?E@$rF@$k(B
            else :
                a=(AHC[i]-AHC[i-1])/(Ene[i]-Ene[i-1])
                sgm=AHC[i-1]+a*(ep-Ene[i-1])
            sgm_mesh.append(sgm)
            #sgm_mesh, ep_mesh$B$,FbA^$K$h$C$FF@$??7$?$J%G!<%?E@$N(Blist
            #ep_mesh$B$O(Bmu$B$rCf?4$H$7$?(Bcosh_cutoff$B$rK~$?$9HO0OFb$r(B10000$BE@$KJ,3d$9$k(B
            #sgm_mesh$B$O(BAHC$B$N%j%9%H$+$i@~7A$KFbA^$9$k$3$H$K$h$jF@$F$$$k(B
            #Ene$B$NDj5A0h$rD6$($?E@$N(Bsgm_mesh$B$O5wN%$G;X?t<}B+$9$k30A^$K$h$jF@$F$$$k(B

        #----- ANC$B$N7W;;(B -----#
        ANC=0
        for i, ep_mu in enumerate(ep_mu_mesh):
            ANC=ANC+sgm_mesh[i]*ep_mu*df_dep_mesh[i]
        ANC=ANC*ep_step*beta/T
        ANC=ANC*100*e #e$B$OJ,;R$K(B2$B$DJ,Jl$K(B1$B$D$G(B1$B$D;D$k(B
        ANC_list.append(ANC)

    return ANC_list

def AHCplot(ax: a.Axes, Ene, AHC):
    ax.plot( Ene, AHC, c='black' ) 
    Md.Eaxis(ax, 'x', [0.1, 3, 3]) 
    #Md.addlabel(ax, 'y', r"$\sigma_{ij}\;\;\rm{[S/cm]}$")

def ANCplot(ax: a.Axes, Ene, ANC):
    ax.plot( Ene, ANC, c='black' )
    Md.Eaxis(ax, 'x', [0.1, 3, 3])
    #Md.addgrid(ax, 'y')
    #Md.addlabel(ax, 'y', r"$\alpha_{ij}$")

if __name__ == '__main__':
    args = docopt(__doc__)
    if args['<anc_dat>'] is None:
        dir = args['<ahc_result_dir>']
        T = [ float(t) for t in args['<T>'].split('-') ]
        if len(T) > 3 or 0 : 
            print("Temperture is wrong")
            sys.exit(0)
        files = []
        if dir[-1] != '/': files.extend( glob.glob("{}/*".format(dir)) )
        else : files.extend( glob.glob("{}*".format(dir)) )
        for file in files:
            if   ".scf.out" in file: file_scf_out=file
            elif "ahc-fermiscan.dat" in file: file_ahc_dat=file
        if args['-s'] is None:
            sfn = file_ahc_dat.replace(dir, "").replace("-ahc-fermiscan.dat", "").replace("/", "")
            save_filename="{}_anc.dat".format(sfn)
        else: save_filename="{}_anc.dat".format(args["-s"])

        totE, ef, totM, absM = read_scf_out(file_scf_out)

        ahcrow = { 'x':1, 'y':2, 'z':3 }
        Ene, AHC = read_ahc_dat(file_ahc_dat, ef, ahcrow[args['<axis>']])
        ANC_df = pd.DataFrame(data = Ene, columns = ["Ene"])
        ANC_df[args['<axis>']] = AHC
        for tp in T:
            ANC = calc_anc(Ene, AHC, tp)
            ANC_df[tp] = ANC 
            print("Temperature {} end".format(tp))
        with open ("{}".format(save_filename), 'w') as f: 
            f.write(ANC_df.to_string(index=False))

        file_anc_dat="{}".format(save_filename)
    else: file_anc_dat = args['<anc_dat>']

    fig, ax = Md.MakeAxesTable([1,1], [1,1], height=20, width=30)
    T, Ene, AHC, ANC=read_anc_dat(file_anc_dat)

    x,y=np.reshape( np.meshgrid([0,1],[0,1]),(2,4) )
    AHCplot(ax[x[0]][y[0]], Ene, AHC)
    for i in range(1,len(T)+1):
        ANCplot(ax[x[i]][y[i]], Ene, ANC[i-1])
        ax[x[i]][y[i]].set_ylim(-4,4)
    plt.show()


#    for i in range(len(T)):
#        ANC=calc_anc(Ene, AHC, T[i])
#        ax[1][0].plot( Ene, ANC, c=Pm.Colorlist(i), label="T={}".format(T[i]) )
#    Md.Eaxis(ax[1][0], 'x', [0.1, 3, 3])
#    Md.addlabel(ax[1][0], 'y', r"$\alpha_{ij}/\rm{T}\;\;[AK^{-2}m^{-1}]$")
#    ax[1][0].legend(loc="center", bbox_to_anchor=(0.6, 0.6, 0.28, 0.38), fontsize=11)
#    ax[1][0].set_ylim(-0.03,0.03)
#    Md.addgrid(ax[1][0], 'y')

#Ene, AHC = read_dat(file2, ef2)
#AHCplot(ax[0][1], Ene, AHC)
#for i in range(len(T)):
#    ANC=calc_anc(Ene, AHC, T[i])
#    ax[1][1].plot( Ene, ANC, c=Pm.Colorlist(i), label="T={}".format(T[i]) )
#Md.Eaxis(ax[1][1], 'x', [0.1, 3, 3])
#Md.addlabel(ax[1][1], 'y', r"$\alpha_{ij}/\rm{T}\;\;[AK^{-2}m^{-1}]$")
#ax[1][1].legend(loc="center", bbox_to_anchor=(0.1, 0.1, 0.28, 0.38), fontsize=11)
#ax[1][1].set_ylim(-0.06,0.06)
#Md.addgrid(ax[1][1], 'y')

#plt.savefig('ANC_T.pdf', format='pdf')


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
#




