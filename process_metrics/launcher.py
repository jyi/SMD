from g_file import GitFile
from g_project import GitProject
import os, sys
import csv
import json


# Collecting Process Metrics and write result into predefined csv
class ProcessMetricsCollector:
    def git_collect(self, git_link, work_dir, file_ext, result_file_path, input_releases):
        project = GitProject(work_dir)
        if not os.path.exists(work_dir):
            project.git_clone(git_link)
        for release in input_releases:
            if len(input_releases) == 2:
                project.check_release_existence(release)
            else:
                raise NameError("Specify exactly 2 releases and try again.")
        with open(result_file_path, 'w', newline='') as csvfile:
            fieldnames = ['file_path', 'COMM', 'NFIX', 'NREF', 'AUTH', 'ALOC', 'RLOC', 'AGE', 'NML']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            print("Wait please. The collecting operation could take some time depending on project size.")
            for dir_, _, files in os.walk(work_dir):
                for fileName in files:
                    rel_dir = os.path.relpath(dir_, work_dir)
                    rel_file = os.path.join(rel_dir, fileName)
                    # remove prefix (./) for the files in current directory
                    rel_file = rel_file.replace("./", "")
                    if 'test' not in rel_dir:
                        if rel_file.endswith(file_ext):
                            git = GitFile(rel_file, work_dir, project.releases, file_ext)
                            # print(git.releases)
                            commits_count, authors_count, refactorings_count, bugfix_count, age, nml, added_loc,\
                                removed_loc = git.get_metrics_between_releases(input_releases[0], input_releases[1])
                            writer.writerow({'file_path': rel_file, 'COMM': commits_count, 'NFIX': bugfix_count,
                                             'NREF': refactorings_count, 'AUTH': authors_count, 'ALOC': added_loc,
                                             'RLOC': removed_loc, 'AGE': age, 'NML': nml})


if __name__ == "__main__":
    with open(sys.argv[1]) as config:
        config_data = json.load(config)

    try:
        git_link = config_data['git_link']
        work_dir = config_data['work_dir']
        file_ext = config_data['file_ext']
        result_file_path = config_data['result_file_path']
        input_releases = config_data['input_releases']
        pmc = ProcessMetricsCollector()
        pmc.git_collect(git_link, work_dir, file_ext, result_file_path, input_releases)
    except NameError:
        print("Broken config file, check all fields and try again.")
