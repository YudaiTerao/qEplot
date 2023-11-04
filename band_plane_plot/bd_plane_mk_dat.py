


n,m = 21,24
#22と23が見たい
mesh = 101
length = [0.50000, 0.50000]
for km in range(mesh):
    values = read_band_dat("bp{0}/bp{0}_band.dat".format(km), ef)[n-1:m]

    for i, value in enumerate(values):
        value[0] = [ v0*length[0]/value[0][-1] for v0 in value[0] ]
        if i == 0 :
            oplines = [ "{0:.10f}  {1:.10f}  {2:.10f}".format(km*length[1]/(mesh-1), value[0][j], value[1][j]) for j in range(len(value[0])) ]
        else :
            oplines = [ "{0}    {1:.10f}  {2:.10f}  {3:.10f}".format(oplines[j], km*length[1]/(mesh-1), value[0][j], value[1][j]) for j in range(len(value[0])) ]

    oplines = [ "{}\n".format(opline) for opline in oplines ]
    with open('bd_plane.dat', 'a') as f_bdplane:
        f_bdplane.writelines(oplines)











