import os
import sys

args = " ".join(sys.argv[1:])
os.system("pytest --rootdir ./tests " + args)
