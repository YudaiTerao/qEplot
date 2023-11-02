
"""
Usage:
  re_win_cp.py <basefile> <mesh> <db_vec>

Options:
  <basefile>         baseとなるwinfile
  <mesh>             複製する方向のmesh
  <db_vec>           複製するwinpathの逆格子の間隔
"""

from docopt import docopt
import numpy as np
import os
args = docopt(__doc__)

db_vec=np.array([ float(x) for x in args['<db_vec>'].split('-') ])
mesh=int(args['<mesh>'])

with open(args['<basefile>'], 'r') as f_base:
    lines=f_base.readlines()
for i, line in enumerate(lines):
    if "Begin Kpoint_Path" in line:
        kp_line=i+1
        base_kp = [[ float(x) for x in lines[i+1].split()[1:4] ]]
        base_kp.append([ float(x) for x in lines[i+1].split()[5:9] ]) 
        base_kp = np.array(base_kp)

this_kp = base_kp
for m in range(mesh):
    if m != 0: this_kp = this_kp + db_vec
    this_kp_name = ["A{}".format(m), "B{}".format(m)]

    lines[kp_line]="{0[0]}  {1[0][0]:.10f}  {1[0][1]:.10f}  {1[0][2]:.10f}  {0[1]}  {1[1][0]:.10f}  {1[1][1]:.10f}  {1[1][2]:.10f}\n".format(this_kp_name, this_kp)
    os.mkdir("bp{}".format(m))
    with open("bp{0}/bp{0}_win".format(m), 'w') as this_win:
        this_win.writelines(lines)

