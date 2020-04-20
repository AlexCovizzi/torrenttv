import os
import sys

rest = " ".join(sys.argv[1:])
os.system("pytest --rootdir ./tests " + rest)
