"""
Usage:
    test.py <dir>

Options:
    <dir>   dir
"""
from docopt import docopt
import os
import re
import glob
#for i in range(30):
#    os.mkdir("bp{}".format(i))

args = docopt(__doc__)
dir = args['<dir>']
def filelist(dirpath):
    files = []
    if dirpath[-1] != '/': files.extend( glob.glob("{}/*".format(dirpath)) )
    else : files.extend( glob.glob("{}*".format(dirpath)) )
    return files
for file in filelist(dir):
    f = file.replace(dir, "")
    #f = re.sub("^"+dir, "", file)
    print(f)
    if re.fullmatch("^bp[0-9]{1,3}$", f): print(f)





