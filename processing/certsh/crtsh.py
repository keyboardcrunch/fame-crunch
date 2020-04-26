import os
import sys
import json

from fame.core.module import ProcessingModule
from fame.common.exceptions import ModuleInitializationError

try:
    import pycrtsh
    has_pycrtsh = True
except ImportError:
    has_pycrtsh = False

class Crtsh(ProcessingModule):
    name = "crt.sh"
    description = "Gather all domain certificates using Crt.sh"
    acts_on = ['url']

    config = [
        {
            'name': 'reverse_dns',
            'type': 'bool',
            'default': True,
            'description': 'List reverse DNS entries from DnsDumpster.'
        },
        {
            'name': 'page_links',
            'type': 'bool',
            'default': True,
            'description': 'Grab page links using HackerTarget.'
        },
        {
            'name': 'http_headers',
            'type': 'bool',
            'default': True,
            'description': 'Grab HTTP server headers from URL using HackerTarget.'
        },
    ]

    def initialize(self):
        if not has_dnsdump:
            raise ModuleInitializationError(self, "Missing dependancy: dnsdmpstr")
        if not has_tldextract:
            raise ModuleInitializationError(self, "Missing dependancy: tldextract")
