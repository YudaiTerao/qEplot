file_scf_out="../result/CrFeS2_S.scf.out"

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

totE, ef, totM, absM = read_scf_out(file_scf_out)

def read_band_dat(file_band_dat, ef):
    values = [[[],[]]]
    lines = [ line.split()  for line in open(file_band_dat, "r").readlines() ]
    j = k = 0
    for i, line in enumerate(lines):
        if ( len(line) < 1 ):
            values[k][0] = [ float(lines[n][0]) for n in range(j,i) ]
            values[k][1] = [ float(lines[n][1]) - ef for n in range(j,i) ]
            values.extend([[[],[]]])
            j = i+1
            k += 1
    return values

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











