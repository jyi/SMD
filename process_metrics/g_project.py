import subprocess
from datetime import datetime
import collections


class GitProject:
    def __init__(self, work_dir):
        # project and file locations
        self.work_dir = work_dir
        self.releases = collections.OrderedDict()

    def get_releases_list(self):
        # get list tags sorted by date
        process = subprocess.Popen(['git log --date-order --tags --simplify-by-decoration --pretty=\'format:%ad %D\''],
                                   cwd=self.work_dir, shell=True,
                                   stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output = process.communicate()[0]
        output = output.decode()
        # print(output)
        output = output.split("\n")
        releases = collections.OrderedDict()
        # HEAD message?
        for release in output[1:]:
            kv = release.split(" tag: ")
            # skip empty tags
            if len(kv) > 2:
                for tag in kv[1:]:
                    tag = tag.replace(',', '')
                    releases[tag] = kv[0]
            elif len(kv) == 2:
                releases[kv[1]] = kv[0]
        releases["HEAD"] = datetime.today().strftime("%a %b %d %H:%M:%S %Y") + " +0300"
        return releases

    def git_clone(self, github_link):
        process = subprocess.Popen(['git clone ' + github_link + ' ' + self.work_dir],
                                   shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        process.wait()

    def check_release_existence(self, release):
        project_releases = self.get_releases_list()
        if release in project_releases.keys():
            self.releases[release] = project_releases[release]
        else:
            raise NameError("There is no such release. Check it and try again.")




