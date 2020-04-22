 
from fame.core.module import ProcessingModule, ModuleInitializationError
from dnsdmpstr import dnsdmpstr
import tldextract
import json

class DnsDumpster(ProcessingModule):
    name = "dnsdumpster"
    description = "Grab DNS data from a domain."

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
        self.needs_plugin("tldextract")

    def dumpdns(self, target):
        # Get the root domain
        domain = tldextract.extract(target)
        domain = domain.domain + '.' + domain.suffix

        # Initialize dnsdmpstr and enumerate the data
        dnsdump = dnsdmpstr.dnsdmpstr()

        # DNS Data
        dnslookup = dnsdump.dnslookup(domain)
        self.results.append(("dnsdata", dnslookup))

        # Reverse DNS
        if self.reverse_dns:
            reverse = dnsdump.reversedns(domain)
            self.results.append(("reverse", reverse))

        # HTTP Headers
        if self.http_headers:
            headers = dnsdump.httpheaders(target)
            self.results.append(("headers", headers))

        # Page Links
        if self.page_links:
            links = dnsdump.pagelinks(target)
            self.results.append(("links", links))

    def each(self, target):
        self.results = []

        # Leverage Zeropwn's dnsdmpstr on the domain
        self.dumpdns(target)
        
        return len(self.results) > 0
