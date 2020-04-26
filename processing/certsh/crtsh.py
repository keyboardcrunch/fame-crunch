import os
import sys
import json
import requests

from fame.core.module import ProcessingModule
from fame.common.utils import tempdir
from fame.common.exceptions import ModuleInitializationError, ModuleExecutionError

try:
    import tldextract
    has_requests = True
except ImportError:
    has_requests = False

try:
    import tldextract
    has_tldextract = True
except ImportError:
    has_tldextract = False

class Crtsh(ProcessingModule):
    name = "crt.sh"
    description = "Gather all domain certificates using Crt.sh"
    acts_on = ['url']

    config = [
        {
            'name': 'save_json',
            'type': 'bool',
            'default': True,
            'description': 'Save certificate information as json output.'
        },
        {
            'name': 'save_hosts',
            'type': 'bool',
            'default': True,
            'description': 'Save found hostnames in a file list.'
        },
    ]

    def initialize(self):
        if not has_requests:
            raise ModuleInitializationError(self, "Missing dependancy: requests")
        if not has_tldextract:
            raise ModuleInitializationError(self, "Missing dependancy: tldextract")

    def each(self, target):
        self.results = {}
        tmpdir = tempdir()

        # Get the root domain
        url = target
        domain = tldextract.extract(url)
        root_domain = domain.domain + '.' + domain.suffix

        self.log("debug", "Querying crt.sh with root domain...")
        try:
            req = requests.get("https://crt.sh/?q=%.{d}&output=json".format(d=root_domain))
            json_data = json.loads(req.text)
        else:
            raise ModuleExecutionError("Failed to get data from crt.sh")
        
        # We want to gather data in a way to present the details.html template as default
        # 
        

        # Save JSON data
        if self.save_json:
            self.log("debug", "Saving json output from crt.sh...")
            json_file = "{r}.json".format(r=root_domain)
            with open(os.path.join(tempdir, json_file), "w") as jf:
                jf.write(json.dumps(json_data, indent=4))
                jf.close()

        # Save host list
        if self.save_hosts:
            self.log("debug", "Saving host list...")
            host_file = "{r}-hostlist.txt".format(r=root_domain)
            with open(os.path.join(tempdir, host_file), "w") as hf:
                for (key,value) in enumerate(json_data):
                    hf.write("{hn}\r\n".format(hn=value['name_value']))
                hf.close()

        self.log("debug","Crt.sh finished.")