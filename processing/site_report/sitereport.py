from fame.core.module import ProcessingModule
from fame.common.exceptions import ModuleInitializationError

import builtwith
import tldextract
import requests
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

class SiteReport(ProcessingModule):
    name = "site_report"
    description = "Simple domain/site report for reporting phishing sites."
    acts_on = ['url']

    api_status = {
        200: 'OK',
        400: 'ERROR',
        429: 'LIMIT EXCEEDED',

    }

    def getStack(self, domain):
        # Profile the site's tech stack
        stack = {}
        data = builtwith.builtwith(domain)
        for key, value in data.items():
            category = key
            tech = ', '.join(value)
            stack[category] = tech
        return stack

    def getDNS(self, domain):
        # May move to local dig but I enjoy the enriched requests from HT
        api = "https://api.hackertarget.com/dnslookup/?q={}".format(domain)
        dns = requests.get(api)
        if dns.status_code != 200:
            self.log("debug", "DNS -> {}".format(self.api_status[dns.status_code]))
        else:
            results = dns.text.split('\n')
            return results

    def getWhois(self, domain):
        # Using hackertarget here because python whois modules suck
        api = "https://api.hackertarget.com/whois/?q={}".format(domain)
        whois = requests.get(api)
        if whois.status_code != 200:
            self.log("debug", "WHOIS -> {}".format(self.api_status[dns.status_code]))
        else:
            results = whois.text.split('\n')
            return results

    def each(self, target):
        domain = urlparse(target).netloc

        self.results = {}
        self.results['sitereport'] = ""
        self.results['sitereport'] += "Domain :\t{}".format(domain)
        self.results['sitereport'] += "\r\n\tURL :\t{}".format(target)
        self.results['sitereport'] += "\r\nDNS\r\n"
        for entry in self.getDNS(domain):
            self.results['sitereport'] += "\r\n\t{}".format(entry)
        self.results['sitereport'] += "\r\nWhois :\r\n"
        for item in self.getWhois(domain):
            self.results['sitereport'] += "\r\n\t{}".format(item)
        self.results['sitereport'] += "\r\nBuilt-with :"
        for k,v in self.getStack(target).items():
            self.results['sitereport'] += "\r\n\t{} : {}".format(k,v)

        return True