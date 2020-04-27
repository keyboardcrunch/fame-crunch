import os
import sys
import json

from fame.core.module import ProcessingModule
from fame.common.utils import tempdir
from fame.common.exceptions import ModuleInitializationError, ModuleExecutionError

try:
    import requests
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
        {
            'name': 'cert_count',
            'type': 'integer',
            'default': 10,
            'description': 'Number of most recent certs to show in report.'
        },
    ]

    def initialize(self):
        if not has_requests:
            raise ModuleInitializationError(self, "Missing dependancy: requests")
        if not has_tldextract:
            raise ModuleInitializationError(self, "Missing dependancy: tldextract")

    def each(self, target):
        tmpdir = tempdir()
        self.results = {}
        self.results['cert_count'] = self.cert_count

        # Get the root domain
        url = target
        domain = tldextract.extract(url)
        root_domain = domain.domain + '.' + domain.suffix

        self.log("info", "Querying crt.sh with root domain...")
        try:
            req = requests.get("https://crt.sh/?q=%.{d}&output=json".format(d=root_domain))
            json_data = json.loads(req.text)
        except:
            raise ModuleExecutionError("Failed to get data from crt.sh")
        
        # We want to gather data in a way to present the details.html template as default
        vc = 0
        certs = []
        for (key, value) in enumerate(json_data): # Add first X cert dicts to a list
            while vc < self.cert_count:
                certs.append(value)
                vc += 1
        self.results['top_certs'] = certs

        # Save JSON data
        if self.save_json:
            self.log("info", "Saving json output from crt.sh...")
            json_file = "{r}.json".format(r=root_domain)
            json_save = os.path.join(tempdir, json_file)
            try:
                with open(json_save, "w") as jf:
                    jf.write(json.dumps(json_data, indent=4))
                    jf.close()
                self.add_extracted_file(json_save)
            except:
                raise ModuleExecutionError("Failed to save json data from crt.sh")

        # Save host list
        if self.save_hosts:
            self.log("info", "Saving host list...")
            host_file = "{r}-hostlist.txt".format(r=root_domain)
            host_save = os.path.join(tempdir, host_file)
            try:
                with open(host_save, "w") as hf:
                    for (key, value) in enumerate(json_data):
                        hf.write("{hn}\r\n".format(hn=value['name_value']))
                    hf.close()
                self.add_extracted_file(host_save)
            except:
                raise ModuleExecutionError("Failed to save json data from crt.sh")

        self.log("info","crt.sh finished.")
        return True