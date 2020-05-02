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
            try:
                soup = BeautifulSoup(req.text, 'lxml')
            except:
                self.log("debug", "BS4 unable to parse the page.")
                return False


            # Link list
            self.results['links'] = self.GetLinks(soup)

            # Form list
            formlist = self.GetForms(soup)
            self.results['forms'] = formlist

            # PrettyPrinted content source
            source = soup.prettify()
            self.results['source'] = soup

            return True
        else:
            self.log("debug", "Server returned {} error code".format(req.status_code))
            return False