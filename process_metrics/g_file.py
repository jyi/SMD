import subprocess
from datetime import datetime, timedelta
import collections

#project_path = "/home/lwm/simplegit-progit/perceval/"
#s11 = "perceval/backends/core/github.py"
#s11 = "src/java/org/apache/poi/ddf/EscherClientAnchorRecord.java"

#project_path = "/home/lwm/velocity-engine"
#project_path = "/home/lwm/synapse"            #zero metrics 1.1 -1.2
#project_path = "/home/lwm/lucene-solr"   #zero metrics for 2.2 - 2.4
#project_path = "/home/lwm/poi"
#project_path = "/home/lwm/camel"
#project_path = "/home/lwm/ant"


class GitFile:
    def __init__(self, file_path, work_dir, releases, file_ext):
        # project and file locations
        self.file_path = file_path
        self.work_dir = work_dir
        self.file_ext = file_ext

        # metrics for particular file from creation till the particular release
        self.authors_count = collections.OrderedDict()  # +++++++++++++++++++
        self.commits_count = collections.OrderedDict()  # +++++++++++++++++++
        self.refactorings_count = collections.OrderedDict()     # ++++++++++++++++++++++
        self.bugfix_count = collections.OrderedDict()   # +++++++++++++++++
        self.age = collections.OrderedDict()    # +++++++++++++
        self.nml = collections.OrderedDict()    # ++++++++++++++

        # preprocessing data
        self.releases = releases

        #self.releases = {"Velocity_1.5": "Tue Mar 6 18:08:28 2007 +0000", "1.6.1": "Mon Dec 15 16:26:17 2008 +0000"}
        #self.releases = {"1.1": "Mon Jan 28 20:45:31 2008 +0000", "1.2": "Mon Jun 9 06:04:45 2008 +0000"}
        #self.releases = {"releases/lucene/2.2.0": "Sun Jun 17 07:15:16 2007 +0000", "releases/lucene/2.4.0": "Wed Oct 8 17:39:25 2008 +0000"}
        #self.releases = {"REL_2_5_1": "Mon Jun 25 01:51:34 2007 +0000", "REL_3_0": "Mon Jun 25 01:51:34 2007 +0000"}
        #self.releases = {"camel-1.4.0": "Mon Jan 19 21:04:24 2009 +0000", "camel-1.6.0": "Wed Feb 18 01:44:28 2009 +0000"}
        #self.releases = {"ANT_13": "Thu Mar 1 11:53:58 2001 +0000", "ANT_14": "Mon Sep 3 09:40:05 2001 +0000"}
        self.commits = collections.OrderedDict()
        self.dates = collections.OrderedDict()
        self.commit_messages = collections.OrderedDict()
        self.loc_stats = collections.OrderedDict()
        self.authors = collections.OrderedDict()

        # getting metrics
        self.collect_all_metrics()

    # using specified working dir, retrieve data from git log by Popen()
    def collect_metric_by_tag(self, tag):
        # get whole message
        process = subprocess.Popen(['git log --stat ' + tag + " " + self.file_path], cwd=self.work_dir,
                                   shell=True,
                                   stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output = process.communicate()[0]
        output = output.decode()
        print(output)
        print("*******************************************************************************************")
        # split message by \n and put result in a list
        output = output.split("\n")

        date_line_position = []
        author_list = []
        commits = []
        commit_messages = []
        dates = []
        loc_stats = []
        loc_stats_position = []

        # put each commit, author, date into distinct ds
        if len(output) > 0:
            for i in range(len(output)):
                parsed = output[i].split(" ")
                if "commit" == parsed[0]:
                    commits.append(output[i])
                if "Date:" == parsed[0]:
                    dates.append(output[i])
                    date_line_position.append(i)
                if "Author:" == parsed[0]:
                    author_list.append(output[i])
                if self.file_ext in output[i] and " | " in output[i] and "grep" not in output[i]:
                    loc_stats.append(output[i])
                    loc_stats_position.append(i)
        else:
            return
        # Saving authors of corresponding commits for further processing
        self.authors[tag] = author_list

        # retrieving body message of each commit an putting it in separate ds with lowercase
        for i in range(len(commits)):
            # number of line from which message starts (right after date)
            current_pos = date_line_position[i] + 1
            message = ""
            while current_pos < loc_stats_position[i]:
                message += output[current_pos].lower()
                current_pos += 1

            commit_messages.append(message)
        self.commits[tag] = commits
        # @METRIC #2
        self.commits_count[tag] = len(commits)
        self.commit_messages[tag] = commit_messages
        self.dates[tag] = dates
        self.loc_stats[tag] = loc_stats

    # return distinct number of file contributors
    def get_distinct_contributors_count(self, tag):
        return len(set(self.authors[tag]))

    # return commit count for particular file
    def get_commit_count(self, tag):
        return len(self.commits[tag])

    # return age of a file from first commit to last in weeks
    def get_age(self, tag):
        weeks = 0
        if self.commits_count[tag] != 0:
            dts = self.dates[tag]
            # get line "Date: ... and split it"
            parsed = dts[-1].split(": ")
            parsed2 = dts[0].split(": ")
            creation_date = datetime.strptime(parsed[1].lstrip(' '), '%a %b %d %H:%M:%S %Y %z')
            # get release date (or current date for HEAD)
            #release_date = datetime.strptime(self.releases[tag].lstrip(' '), '%a %b %d %H:%M:%S %Y %z')
            release_date = datetime.strptime(parsed2[1].lstrip(' '), '%a %b %d %H:%M:%S %Y %z')

            monday1 = (creation_date - timedelta(days=creation_date.weekday()))
            monday2 = (release_date - timedelta(days=release_date.weekday()))
            weeks = (monday2 - monday1).days / 7
        return weeks

    # get number of refactorings based on commit message
    def get_refactors_count(self, tag):
        ref_count = 0
        for message in self.commit_messages[tag]:
            if "refactor" in message:
                ref_count += 1

        return ref_count

    # get number of bug fixes based on commit message
    def get_bugfix_count(self, tag):
        bf_count = 0
        for message in self.commit_messages[tag]:
            if "fix" in message and "prefix" not in message and "postfix" not in message:
                bf_count += 1

        return bf_count

    # count number of modified lines for particular release\tag
    def get_modified_lines_number(self, tag):
        nml = 0
        for stat in self.loc_stats[tag]:
            print(stat)
            # split line by |
            parsed1 = stat.split(" | ")
            # split by space to get number
            parsed2 = parsed1[1].split(" ")
            nml += int(parsed2[0])
        return nml

    # collect metrics for all releases (tags)
    def collect_all_metrics(self):
        for release in self.releases.keys():
            self.collect_metric_by_tag(release)
            self.bugfix_count[release] = self.get_bugfix_count(release)
            self.refactorings_count[release] = self.get_refactors_count(release)
            self.age[release] = self.get_age(release)
            self.nml[release] = self.get_modified_lines_number(release)
            self.authors_count[release] = self.get_distinct_contributors_count(release)

    # get metrics between 2 particular releases
    def get_metrics_between_releases(self, tag1, tag2):
        if self.commits_count[tag2] >= self.commits_count[tag1]\
                and self.nml[tag2] >= self.nml[tag1] \
                and self.age[tag2] >= self.age[tag1] != 0:
            commits_count = self.commits_count[tag2] - self.commits_count[tag1]
            authors_count = len(set((self.authors[tag2])[len(self.authors[tag1])::]))
            refactorings_count = self.refactorings_count[tag2] - self.refactorings_count[tag1]
            bugfix_count = self.bugfix_count[tag2] - self.bugfix_count[tag1]
            age = self.age[tag2]
            nml = self.nml[tag2] - self.nml[tag1]
        elif self.age[tag1] == 0:
            commits_count = self.commits_count[tag2]
            authors_count = self.authors_count[tag2]
            refactorings_count = self.refactorings_count[tag2]
            bugfix_count = self.bugfix_count[tag2]
            age = self.age[tag2]
            nml = self.nml[tag2]
        else:
            commits_count = self.commits_count[tag1] - self.commits_count[tag2]
            authors_count = len(set((self.authors[tag1])[len(self.authors[tag2])::]))
            refactorings_count = self.refactorings_count[tag1] - self.refactorings_count[tag2]
            bugfix_count = self.bugfix_count[tag1] - self.bugfix_count[tag2]
            age = self.age[tag1]
            nml = self.nml[tag1] - self.nml[tag2]
        if refactorings_count < 0:
            refactorings_count = 0
        if bugfix_count < 0:
            bugfix_count = 0

        return commits_count, authors_count, refactorings_count, bugfix_count, age, nml


#git = Git(s11, project_path)
# print(git.commits_count)
# print(git.authors_count)
# print(git.bugfix_count)
# print(git.refactorings_count)
# print(git.age)
# print(git.nml)
#
# print(str(git.commits_count['REL_2_5_1']) + " " + str(git.authors_count['REL_2_5_1']) + " " +
#       str(git.bugfix_count['REL_2_5_1']) + " " + str(git.refactorings_count['REL_2_5_1']) + " " +
#       str(git.age['REL_2_5_1']) + " " + str(git.nml['REL_2_5_1']))
# print(str(git.commits_count['REL_3_0']) + " " + str(git.authors_count['REL_3_0']) + " " +
#       str(git.bugfix_count['REL_3_0']) + " " + str(git.refactorings_count['REL_3_0']) + " " +
#       str(git.age['REL_3_0']) + " " + str(git.nml['REL_3_0']))
# print(git.authors["REL_2_5_1"])
# print(git.authors["REL_3_0"])
# print(git.get_metrics_between_releases("REL_2_5_1", "REL_3_0"))


#git.collect_metric(path)
# print(git.get_age())
# print(git.get_refactors_count())
# print(git.get_bugfix_count())

# if __name__ == "__main__":
#     with open(result_file_path, 'w', newline='') as csvfile:
#         fieldnames = ['file_path', 'nr', 'ndc', 'nml', 'ndpv']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for dir_, _, files in os.walk(work_dir):
#             for fileName in files:
#                 relDir = os.path.relpath(dir_, work_dir)
#                 relFile = os.path.join(relDir, fileName)
#                 # remove prefix (./) for the files in current directory
#                 relFile = relFile.replace("./", "")
#                 if 'test' not in relDir:
#                     if relFile.endswith(file_ext):
#                         git = Git(relFile, work_dir)
#                         print(git.releases)
#                         # writer.writerow({'file_path': relFile, 'nr': git.commits_count["camel-1.6.0"],
#                         #                 'ndc': git.authors_count["camel-1.6.0"], 'nml': git.nml["camel-1.6.0"],
#                         #                  'ndpv': git.bugfix_count["camel-1.6.0"]})
#                         commits_count, authors_count, refactorings_count, bugfix_count, age, nml = \
#                             git.get_metrics_between_releases("camel-1.4.0", "camel-1.6.0")
#                         # #git.get_metrics_between_releases("rel/1.3", "rel/1.4")
#                         writer.writerow({'file_path': relFile, 'nr': commits_count,
#                                         'ndc': authors_count, 'nml': nml,
#                                         'ndpv': bugfix_count})
#                         # print(git.commits_count)
#                         # print(git.authors_count)
#                         # print(git.bugfix_count)
#                         # print(git.refactorings_count)
#                         # print(git.age)
#                         # print(git.nml)
