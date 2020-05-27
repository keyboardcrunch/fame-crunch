from fame.core.module import ProcessingModule, ModuleInitializationError

try:
    from urlextract import URLExtract
    HAVE_URLEXTRACT = True
except ImportError:
    HAVE_URLEXTRACT = False

try:
    from XLMMacroDeobfuscator.deobfuscator import process_file
    HAVE_DEOBFUSCATOR = True
except ImportError:
    HAVE_DEOBFUSCATOR = False

class XlmDeobfuscator(ProcessingModule):
    name = "xlm_deobfuscator"
    description = "Extract Excel macros using XLMMacroDeobfuscator."
    acts_on = ["excel"]

    def initialize(self):
        if not HAVE_DEOBFUSCATOR:
            raise ModuleInitializationError(self, "Missing dependency: XLMMacroDeobfuscator")
        if not HAVE_URLEXTRACT:
            raise ModuleInitializationError(self, "Missing dependency: URLExtract")

    def deobfuscate(self, target):
        macros = process_file(file=target, 
            noninteractive=True, 
            no_indent=True,
            no_ms_excel=True,
            output_formula_format='[[CELL_ADDR]], [[INT-FORMULA]]',
            return_deobfuscated=True)
        return macros
        
    def find_urls(self, data):
        ex = URLExtract()
        urls = ex.find_urls(str(data))        
        return set(urls)

    def each(self, target):
        self.results = {}

        # execute docker container
        output = self.deobfuscate(target)

        self.results['macros'] = output
        self.results['urls'] = self.find_urls(output)

        if len(self.results['urls']) > 0:
            # save extracted URLs as C2 observables
            self.add_ioc(self.results['urls'], ['C2'])

        # Return True if macros exist
        return len(self.results['macros']) > 0
