from __future__ import unicode_literals
import json
from fame.common.exceptions import ModuleInitializationError
from fame.core.module import ReportingModule

try:
    import pymsteams
    has_teams = True
except ImportError:
    has_teams = False

try:
    from defang import defang
    has_defang = True
except ImportError:
    has_defang = False


class Teams(ReportingModule):
    name = "msteams"
    description = "Post message on MS Teams when an anlysis if finished."

    config = [
        {
            'name': 'url',
            'type': 'str',
            'description': 'Incoming webhook URL.'
        },
        {
            'name': 'fame_base_url',
            'type': 'str',
            'description': 'Base URL of your FAME instance, as you want it to appear in links.'
        },
    ]

    def initialize(self):
        if ReportingModule.initialize(self):
            if not has_teams:
                raise ModuleInitializationError(self, "Missing dependency: pymsteams")

            if not has_defang:
                raise ModuleInitializationError(self, "Missing dependency: defang")

            return True
        else:
            return False

    def done(self, analysis):
        # Build analysis message
        string = "Just finished analysis on {0}\n".format(defang(', '.join(analysis._file['names'])))

        if analysis['modules'] is not None:
            string += "Target: {0}\n".format(analysis['modules'])

        if len(analysis['extractions']) > 0:
            string += "Extractions: {0}\n".format(','.join([x['label'] for x in analysis['extractions']]))

        if len(analysis['probable_names']) > 0:
            string += "Probable Names: {0}\n".format(','.join(analysis['probable_names']))

        string += "<{0}/analyses/{1}|See analysis>".format(self.fame_base_url, analysis['_id'])

        data = {'text': string}

        # Teams connector
        mh = pymsteams.connectorcard(self.url)
        mh.title("FAME Analysis Completed")
        mh.text(string)
        mh.send()