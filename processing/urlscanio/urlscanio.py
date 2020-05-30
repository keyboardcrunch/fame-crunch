from fame.core.module import ProcessingModule
from fame.common.exceptions import ModuleInitializationError

import requests
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

class UrlScanio(ProcessingModule):
    name = "urlscan_search"
    description = "Performs lookups against the UrlScan.io search API."
    acts_on = ["url"]


    def searchUrlscan(url, result_count):
        """
        We'll want to use urlparse.netloc to search by domain, but do partial url match
        against the results['url'] and attempt to return most likely results, else we'll
        list the top 10 results. Will search by ?q=ip"{} as fallback.
        """
        scans = []
        iapi = "https://urlscani.io/api/v1/search/?q=ip:{}".format(ip)
        dapi = "https://urlscan.io/api/v1/search/?q=page.domain:{}".format(domain)
        r = requests.get(api).json()
        if r['total'] == 0:
            print("No scan data.")
        elif r['total'] >= result_count:
            for item in range(result_count):
                entry = {'time': r['results'][item]['task']['time'], 'url': r['results'][item]['task']['url'], 'scan': r['results'][item]['result']}
                scans.append(entry)
        else:
            for item in r['results']:
                entry = {'time': item['task']['time'], 'url': item['task']['url'], 'scan': item['result']}
                scans.append(entry)
        return scans # list of dicts {time, url, scan}

    def each(self, target):
        self.results = {}
