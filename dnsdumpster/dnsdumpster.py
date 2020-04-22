import os
import sys
import json

from fame.core.module import ProcessingModule
from fame.common.constants import VENDOR_ROOT
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
    description = "Grab DNS data from a domain."
    acts_on = ['url']

    config = [
        {
            'name': 'reverse_dns',
            'type': 'bool',
            'default': 'false',
            'description': 'Enumerate reverse DNS entries.'
        },
        {
            'name': 'page_links',
            'type': 'bool',
            'default': 'false',
            'description': 'Grab page links.'
        },
        {
            'name': 'http_headers',
            'type': 'bool',
            'default': 'false',
            'description': 'Grab HTTP server headers.'
        },
    ]

    def initialize(self):
        if not has_dnsdump:
            raise ModuleInitializationError(self, "Missing dependancy: dnsdmpstr")
        if not has_tldextract:
            raise ModuleInitializationError(self, "Missing dependancy: tldextract")

    def dumpdns(self, target):
        # Get the root domain
        domain = tldextract.extract(target)
        domain = domain.domain + '.' + domain.suffix

        # Initialize dnsdmpstr and enumerate the data
        dnsdump = dnsdmpstr.dnsdmpstr()

        # DNS Data
        dnslookup = dnsdump.dnslookup(domain)
        self.results['dns_data'] = dnslookup

        # Reverse DNS
        if self.reverse_dns:
            reverse = dnsdump.reversedns(domain)
            self.results['reverse_dns'] = reverse

        # HTTP Headers
        if self.http_headers:
            headers = dnsdump.httpheaders(target)
            self.results['headers'] = headers

        # Page Links
        if self.page_links:
            links = dnsdump.pagelinks(target)
            self.results['links'] = links
        
        return True

    def each(self, target):
        self.results = {
            'dns_data': [],
            'reverse_dns': [],
            'headers': [],
            'links': []
        }

        # Leverage Zeropwn's dnsdmpstr on the domain
        self.dumpdns(target)
        
        self.log('dns data:', '{}'.format(self.results['dns_data']))

        return True
