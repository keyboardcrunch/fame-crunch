import sys
from XLMMacroDeobfuscator.deobfuscator import process_file

macros = process_file(file=sys.argv[1], 
    noninteractive=True, 
    no_indent=True,
    no_ms_excel=True,
    output_formula_format='[[CELL_ADDR]], [[INT-FORMULA]]',
    return_deobfuscated=True)
return macros