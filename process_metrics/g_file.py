import subprocess
from datetime import datetime, timedelta
import collections


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
        self.added_loc = collections.OrderedDict()  # +++++++++++++
        self.removed_loc = collections.OrderedDict()  # ++++++++++++++

        # preprocessing data
        self.releases = releases

        self.commits = collections.OrderedDict()
        self.dates = collections.OrderedDict()
        self.commit_messages = collections.OrderedDict()
        self.nml_stats = collections.OrderedDict()
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
        # split message by \n and put result in a list
        output = output.split("\n")

        date_line_position = []
        author_list = []
        commits = []
        commit_messages = []
        dates = []
        nml_stats = []
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
                    nml_stats.append(output[i])
                    loc_stats.append(output[i+1])
                    loc_stats_position.append(i+1)
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
        self.nml_stats[tag] = nml_stats

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
        for stat in self.nml_stats[tag]:
            # split line by |
            parsed1 = stat.split(" | ")
            # split by space to get number
            parsed2 = parsed1[1].split(" ")
            nml += int(parsed2[0])
        return nml

    # count number of added and removed LOC for particular release\tag
    def get_added_and_removed_lines_number(self, tag):
        added_loc = 0
        removed_loc = 0
        for stat in self.loc_stats[tag]:
            # split line by ,
            parsed1 = stat.split(", ")
            # check, is only addition or only deletions were performed?
            # then split by space and took the number
            if len(parsed1) == 2:
                parsed2 = parsed1[1].split(" ")
                if '+' in parsed2[1]:
                    added_loc += int(parsed2[0])
                if '-' in parsed2[1]:
                    removed_loc += int(parsed2[0])
            if len(parsed1) == 3:
                added = parsed1[1].split(" ")
                added_loc += int(added[0])
                removed = parsed1[2].split(" ")
                removed_loc += int(removed[0])
        return added_loc, removed_loc

    # collect metrics for all releases (tags)
    def collect_all_metrics(self):
        for release in self.releases.keys():
            self.collect_metric_by_tag(release)
            self.bugfix_count[release] = self.get_bugfix_count(release)
            self.refactorings_count[release] = self.get_refactors_count(release)
            self.age[release] = self.get_age(release)
            self.nml[release] = self.get_modified_lines_number(release)
            self.added_loc[release], self.removed_loc[release] = self.get_added_and_removed_lines_number(release)
            self.authors_count[release] = self.get_distinct_contributors_count(release)

    # get metrics between 2 particular releases
    def get_metrics_between_releases(self, tag1, tag2):
        if self.commits_count[tag2] >= self.commits_count[tag1] \
                and self.added_loc[tag2] >= self.added_loc[tag1] \
                and self.removed_loc[tag2] >= self.removed_loc[tag1] \
                and self.nml[tag2] >= self.nml[tag1] \
                and self.age[tag2] >= self.age[tag1] != 0:
            commits_count = self.commits_count[tag2] - self.commits_count[tag1]
            authors_count = len(set((self.authors[tag2])[len(self.authors[tag1])::]))
            refactorings_count = self.refactorings_count[tag2] - self.refactorings_count[tag1]
            bugfix_count = self.bugfix_count[tag2] - self.bugfix_count[tag1]
            age = self.age[tag2]
            nml = self.nml[tag2] - self.nml[tag1]
            added_loc = self.added_loc[tag2] - self.added_loc[tag1]
            removed_loc = self.removed_loc[tag2] - self.removed_loc[tag1]
        elif self.age[tag1] == 0:
            commits_count = self.commits_count[tag2]
            authors_count = self.authors_count[tag2]
            refactorings_count = self.refactorings_count[tag2]
            bugfix_count = self.bugfix_count[tag2]
            age = self.age[tag2]
            nml = self.nml[tag2]
            added_loc = self.added_loc[tag2]
            removed_loc = self.removed_loc[tag2]
        else:
            commits_count = self.commits_count[tag1] - self.commits_count[tag2]
            authors_count = len(set((self.authors[tag1])[len(self.authors[tag2])::]))
            refactorings_count = self.refactorings_count[tag1] - self.refactorings_count[tag2]
            bugfix_count = self.bugfix_count[tag1] - self.bugfix_count[tag2]
            age = self.age[tag1]
            nml = self.nml[tag1] - self.nml[tag2]
            added_loc = self.added_loc[tag1] - self.added_loc[tag2]
            removed_loc = self.removed_loc[tag1] - self.removed_loc[tag2]
        if refactorings_count < 0:
            refactorings_count = 0
        if bugfix_count < 0:
            bugfix_count = 0

        return commits_count, authors_count, refactorings_count, bugfix_count, age, nml, added_loc, removed_loc

