import builtwith
import requests
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse
from fame.core.module import ProcessingModule

class SiteReport(ProcessingModule):
    name = "site_report"
    description = "Simple domain/site report for reporting phishing sites."
    acts_on = ['url']

    api_status = {
        200: 'OK',
        400: 'ERROR',
        429: 'LIMIT EXCEEDED',

    }

    results = {}

    def get_stack(self, domain):
        """ Uses builtwith to profile the tech stack; Returns dict with list """
        stack = {}
        data = builtwith.builtwith(domain)
        for key, value in data.items():
            category = key
            tech = ', '.join(value)
            stack[category] = tech
        return stack

    def get_dns(self, domain):
        """ Uses HackerTarget to gather DNS info """
        api = "https://api.hackertarget.com/dnslookup/?q={}".format(domain)
        dns = requests.get(api)
        if dns.status_code == 200:
            return dns.text.split('\n')
        else:
            return "Error with API"

    def get_whois(self, domain):
        """ Uses HackerTarget to gather Whois info """
        api = "https://api.hackertarget.com/whois/?q={}".format(domain)
        whois = requests.get(api)
        if whois.status_code == 200:
            return whois.text.split('\n')
        else:
            return "Error with API"

    def each(self, target):
        """ Loop through url targets building and returning a txt report """
        domain = urlparse(target).netloc

        self.results['sitereport'] = "Domain :\t{}".format(domain)
        self.results['sitereport'] += "\r\n\tURL :\t{}".format(target)
        self.results['sitereport'] += "\r\nDNS :"
        for entry in self.get_dns(domain):
            self.results['sitereport'] += "\r\n\t{}".format(entry)
        self.results['sitereport'] += "\r\nWhois :"
        for item in self.get_whois(domain):
            self.results['sitereport'] += "\r\n\t{}".format(item)
        self.results['sitereport'] += "\r\nBuilt-with :"
        for key, value in self.get_stack(target).items():
            self.results['sitereport'] += "\r\n\t{} : {}".format(key, value)

        return True
