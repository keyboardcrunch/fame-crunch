import pprint
from fame.core.module import ProcessingModule
from fame.common.exceptions import ModuleInitializationError

try:
    import requests
    has_requests = True
except ImportError:
    has_requests = False

try:
    from bs4 import BeautifulSoup
    has_bs4 = True
except ImportError:
    has_bs4 = False

class PageParser(ProcessingModule):
    name = "PageParser"
    description = "Parse page and DOM details."
    acts_on = ['url']

    def initialize(self):
        if not has_requests:
            raise ModuleInitializationError(self, "Missing dependancy: requests")
        if not has_bs4:
            raise ModuleInitializationError(self, "Missing dependancy: bs4")

    def GetLinks(self, soup):
        links = ""
        anchors = soup.find_all('a')
        for link in anchors:
            try:
                if not link['href'] in links:
                    links += "{}\r\n".format(link['href'])
            except:
                pass
        return links

    def GetForms(self, soup):
        forms = []
        form_search = soup.find_all('form')
        for form in form_search:
            forms.append({'content':form, 'action': form.get('action')})
        return forms

    def each(self, target):
        url = target
        self.results = {}

        # Request the page
        req = requests.get(url)
        if req.status_code == 200:
            soup = BeautifulSoup(req.text, 'lxml')

            # Link list
            self.results['links'] = GetLinks(soup)

            # Form list
            forms = []
            for form in GetForms(soup):
                forms.append({form['action'], form['content']})
            self.results['forms'] == forms

            # PrettyPrinted content source
            pp = pprint.PrettyPrinter(indent=4)
            self.results['content'] == pp.pprint(soup)

            return True
        else:
            self.log("debug", "Server returned {} error code".format(req.status_code))
            return False