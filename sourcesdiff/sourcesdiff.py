from bs4 import BeautifulSoup
import json
from optparse import OptionParser
import urllib2
from xml.dom.minidom import parse as xml_parse


class Sources(object):

    def __init__(self, filename):
        self.filename = filename
        self.default = None
        self.remotes = {}
        self.projects = []

    def _attr_to_dict(self, input):
        output = {}
        for key in input.keys():
            output[key] = input[key].value
        return output

    def parse(self):
        # TBD: Might as well use BeautifulSoup here, instead of xml_parse
        dom = xml_parse(self.filename)
        element = dom.getElementsByTagName('default')[0]
        self.default = self._attr_to_dict(element.attributes)
        for remote in dom.getElementsByTagName('remote'):
            remote_dict = self._attr_to_dict(remote.attributes)
            self.remotes.update({remote_dict['name']: remote_dict['fetch']})
        for project in dom.getElementsByTagName('project'):
            attrs = self._attr_to_dict(project.attributes)
            attrs.setdefault('remote', self.default['remote'])
            self.projects.append(attrs)

    def _to_set(self):
        return set([(x['name'], x['remote'], x['revision']) for x in self.projects])

    def diff(self, other, output_file=None):
        output = []
        projects = self._to_set() - other._to_set()

        # TBD: automatically determine which is newer and older; we currently
        # assume that 'self' is newer than 'other'.

        for project in projects:
            name = project[0]
            if name not in [x['name'] for x in self.projects]:
                output.append({'new_project': name,
                               'filename': self.filename})
            elif name not in [x['name'] for x in other.projects]:
                output.append({'new_project': name,
                               'filename': other.filename})
            else:
                this_commit = [x for x in self.projects if x['name'] == name][0]
                other_commit = [x for x in other.projects if x['name'] == name][0]

                if this_commit['remote'] != other_commit['remote']:
                    raise Exception('remotes for project %s changed!' % name)

                print 'processing project %s,\n\tcommits %s..%s' % (name, this_commit['revision'], other_commit['revision'])

                # The 'remote' in sources.xml refers to a git.mozilla.org url
                # that can be cloned with git, but can't be browsed; we need to
                # convert that into a gitweb URL that we can use to load history.
                path = self.remotes[this_commit['remote']][len('https://git.mozilla.org/'):]
                git = this_commit['name']
                if not git.endswith('.git'):
                    git = "%s.git" % git
                baseurl = 'http://git.mozilla.org/?p=%s/%s' % (path, git)
                historyurl = "%s;a=history;hb=%s" % (baseurl, this_commit['revision'])

                fp = urllib2.urlopen(historyurl)
                data = fp.read()

                commits = []
                # This code is very dependent on the stucture of the gitweb
                # HTML served by git.mozilla.org.
                soup = BeautifulSoup(data)
                table = soup.select('.history')[0]
                rows = table.find_all('tr')
                for row in rows:
                    author = row.select('.author')
                    subject = row.select('.subject')
                    if len(author) and len(subject):
                        href = subject[0]['href']
                        revision = href[href.find('h=') + 2:]
                        commits.append({
                            'commit': subject[0].get_text(),
                            'revision': revision,
                            'author': author[0].find_all('a')[0].get_text(),
                        })
                        if other_commit['revision'] == revision:
                            break

                output.append({
                    'repo': baseurl,
                    self.filename: this_commit['revision'],
                    other.filename: other_commit['revision'],
                    'commits': commits
                })

        if output_file:
            with open(output_file, 'w') as f:
                f.write(json.dumps(output, indent=2))
        else:
            print json.dumps(output, indent=2)


class SourcesDiffParser(OptionParser):

    def __init__(self, **kwargs):
        OptionParser.__init__(self, **kwargs)
        self.add_option('-o', '--output',
                        dest='output_file',
                        help='write result to specified file')


if __name__ == "__main__":
    parser = SourcesDiffParser(usage='%prog [options] newer_sources.xml older_sources2.xml')
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_usage()
        parser.exit()

    first = Sources(args[0])
    first.parse()
    second = Sources(args[1])
    second.parse()
    first.diff(second, output_file=options.output_file)
