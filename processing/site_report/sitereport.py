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
            return "API ERROR"
        else:
            results = dns.text.split('\n')
            return results

    def getWhois(self, domain):
        # Using hackertarget here because python whois modules suck
        api = "https://api.hackertarget.com/whois/?q={}".format(domain)
        whois = requests.get(api)
        if whois.status_code != 200:
            return "API ERROR"
        else:
            results = whois.text.split('\n')
            return results

    def each(self, target):
        self.results = {}
        self.results['sitereport'] = ""

        domain = urlparse(target).netloc

        domain_info = {}
        domain_info['domain'] = domain
        domain_info['url'] = target
        dns = getDNS(domain)
        domain_info['dns'] = dns
        whois = getWhois(domain)
        domain_info['whois'] = whois
        domain_info['builtwith'] = getStack(target)

        for key,val in domain_info.items():
            self.results['sitereport'] += "\r\n{}".format(key)
            if type(val) == list:
                if type(val[0]) == dict:
                    for entry in val:
                        data = ' : '.join(list(entry.values()))
                        self.results['sitereport'] += "\r\n\t{}".format(data)
                else:
                    for item in val:
                        self.results['sitereport'] +=  "\r\n\t{}".format(item)
            elif type(val) == dict:
                for k,v in val.items():
                    self.results['sitereport'] += "\r\n\t{} : {}".format(k,v)
            else:
                self.results['sitereport'] +=  "\r\n\t{}".format(val)

        return True