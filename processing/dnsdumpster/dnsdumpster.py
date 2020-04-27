import os
import sys
import json
import re

from fame.core.module import ProcessingModule
from fame.common.constants import VENDOR_ROOT
from fame.common.utils import tempdir
from fame.common.exceptions import ModuleInitializationError

try:
    sys.path.append(os.path.join(VENDOR_ROOT, 'dnsdmpstr'))
    import dnsdmpstr
    has_dnsdump = True
except ImportError:
    has_dnsdump = False

try:
    import tldextract
    has_tldextract = True
except ImportError:
    has_tldextract = False

class DnsDumpster(ProcessingModule):
    name = "dnsdumpster"
    description = "Enumerate domain DNS data."
    acts_on = ['url']

    config = [
        {
            'name': 'reverse_dns',
            'type': 'bool',
            'default': False,
            'description': 'List reverse DNS entries from DnsDumpster.'
        },
        {
            'name': 'page_links',
            'type': 'bool',
            'default': False,
            'description': 'Grab page links using HackerTarget.'
        },
        {
            'name': 'http_headers',
            'type': 'bool',
            'default': False,
            'description': 'Grab HTTP server headers from URL using HackerTarget.'
        },
        {
            'name': 'save_csv',
            'type': 'bool',
            'default': False,
            'description': 'Save DNS lookup data to a csv file.'
        },
    ]

    def initialize(self):
        if not has_dnsdump:
            raise ModuleInitializationError(self, "Missing dependancy: dnsdmpstr")
        if not has_tldextract:
            raise ModuleInitializationError(self, "Missing dependancy: tldextract")

    def each(self, target):
        self.results = {}

        # Get the root domain
        url = target
        domain = tldextract.extract(url)
        root_domain = "{}.{}".format(domain.domain, domain.suffix)

        # Initialize dnsdmpstr and enumerate the data
        dnsdump = dnsdmpstr.dnsdmpstr()

        # DNS Data
        self.log("info", 'gathering dns data...')
        self.results['dns_data'] = dnsdump.dnslookup(root_domain)

        # Save csv data
        if self.save_csv:
            try:
                tmpdir = tempdir()
                csv_file = "{}.csv".format(domain.domain)
                csv_save = os.path.join(tmpdir, csv_file)
                with open(csv_save, "w") as cf:
                    cf.write(re.sub("[\t]", ",", self.results['dns_data']))
                    cf.close()
                self.add_support_file("DNS Data", csv_save)
            except:
                self.log("error", 'failed to save csv output.')
                continue

        # Reverse DNS
        if self.reverse_dns:
            self.log("info", 'gathering reverse dns data...')
            self.results['reverse_dns'] = dnsdump.reversedns(root_domain)

        # HTTP Headers
        if self.http_headers:
            self.log("info", 'gathering url headers...')
            # Query HackerTarget with a cleaned up target URL
            dest = url.split('?')[0].split("#")[0]  # reduce dnsdmpstr errors
            headers = dnsdump.httpheaders(dest)
            if not "error" in headers:
                self.results['headers'] = headers

        # Page Links
        if self.page_links:
            self.log("info", 'gathering url links...')
            # Query HackerTarget with a cleaned up target URL
            dest = url.split('?')[0].split("#")[0]  # reduce dnsdmpstr errors
            links = dnsdump.pagelinks(dest)
            if not "url is invalid" in links:
                self.results['links'] = links

        return True