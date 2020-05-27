import os
import sys

target = sys.argv[1]
deobfuscate = "xlmdeobfuscator --no-ms-excel --no-indent -n --file {}".format(os.path.basename(target))
os.system(deobfuscate)