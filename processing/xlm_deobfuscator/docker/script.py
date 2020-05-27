import sys
from XLMMacroDeobfuscator.deobfuscator import process_file

def process(filename):
    process_file(file=filename, 
        noninteractive=True, 
        no_indent=True,
        no_ms_excel=True,
        output_formula_format='[[CELL_ADDR]], [[INT-FORMULA]]')

process(sys.argv[1])