from fame.core.module import ProcessingModule, ModuleInitializationError
from ..docker_utils import HAVE_DOCKER, docker_client

try:
    from urlextract import URLExtract
    HAVE_URLEXTRACT = True
except ImportError:
    HAVE_URLEXTRACT = False

class XlmDeobfuscator(ProcessingModule):
    name = "xlm_deobfuscator"
    description = "Extract Excel macros using XLMMacroDeobfuscator."
    acts_on = ["excel"]

    def initialize(self):
        if not HAVE_DOCKER:
            raise ModuleInitializationError(self, "Missing dependency: docker")

        if not HAVE_URLEXTRACT:
            raise ModuleInitializationError(self, "Missing dependency: URLExtract")

    def parse_data(self, data):
        macros = [] # {'Cell':'', Formula':''}
        sstr = "[Starting Deobfuscation]"
        estr = "[END of Deobfuscation]"
        start = data.rindex(sstr) + len(sstr)
        end = data.rindex(estr, start)
        unformatted = data[start:end]
        lines = unformatted.splitlines()
        for line in lines:
            ml = line.split('   ,')
            try:
                mc = {'Cell': ml[0].strip(), 'Formula': ml[1].strip()}
                macros.append(mc)
            except:
                pass
        return macros

    def deobfuscate(self, target):
        args = 'python3 {} {}'.format('./script.py', 'target')
        return docker_client.containers.run(
            'fame/xlm_deobfuscator',
            args,
            volumes={self.outdir: {'bind': '/data', 'mode': 'rw'}},
            stderr=True,
            remove=True
        )
        
    def find_urls(self, data):
        ex = URLExtract()
        urls = ex.find_urls(str(data))        
        return list(set(urls))

    def each(self, target):
        self.results = {}

        # execute docker container
        output = self.deobfuscate(target)
        macros = self.parse_data(output)

        self.results['macros'] = macros
        self.results['urls'] = self.find_urls(macros)

        if len(self.results['urls']) > 0:
            # save extracted URLs as C2 observables
            self.add_ioc(self.results['urls'], ['C2'])

        # Return True if macros exist
        return len(self.results['macros']) > 0
