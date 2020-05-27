# coding: utf-8

from urlextract import URLExtract
from fame.core.module import ProcessingModule, ModuleInitializationError
from ..docker_utils import HAVE_DOCKER, docker_client

class XlmDeobfuscator(ProcessingModule):
    name = 'xlm_deobfuscator'
    description = 'Extract Excel macros using XLMMacroDeobfuscator.'
    acts_on = ['excel']

    def initialize(self):
        if not HAVE_DOCKER:
            raise ModuleInitializationError(self, "Missing dependency: docker")
        return True

    def deobfuscate(self, target):
        return docker_client.containers.run(
            'fame/xlm_deobfuscator',
            os.path.basename(target),
            volumes={self.outdir: {'bind': '/data', 'mode': 'rw'}},
            stderr=True,
            remove=True
        )

    def parse_data(self, data):
        macros = [] # {'Cell':'', 'Eval':'', 'Formula':''}
        sstr = "[Starting Deobfuscation]"
        estr = "[END of Deobfuscation]"
        start = data.rindex(sstr) + len(sstr)
        end = data.rindex(estr, start)
        unformatted = data[start:end]
        lines = unformatted.splitlines()
        for line in lines:
            ml = line.split('   ,')
            try:
                mc = {'Cell': ml[0].strip(), 'Eval': ml[1].strip(), 'Formula': ml[2]}
                macros.append(mc)
            except:
                pass
        return macros
        
    def find_urls(self, data):
        ex = URLExtract()
        urls = ex.find_urls(str(data))        
        return urls

    def each(self, target):
        self.results = {}

        # execute docker container
        output = self.deobfuscate(target)
        data = parse_data(output)

        self.results['macros'] = data
        self.results['urls'] = find_urls(data)

        if len(self.results['urls']) > 0:
            # save extracted URLs as C2 observables
            self.add_ioc(self.results['urls'], ['C2'])

        # Return True if macros exist
        return len(self.results['macros']) > 0
