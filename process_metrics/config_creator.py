import json
import io


def create_config():
    git_link = "https://github.com/chaoss/grimoirelab-perceval.git"
    work_dir = "/home/lwm/perceval"
    file_ext = ".py"
    result_file_path = 'perceval_060_080.csv'
    input_releases = ['0.6.0', '0.8.0']
    data = {'git_link': git_link,
            'work_dir': work_dir,
            'file_ext': file_ext,
            'result_file_path': result_file_path,
            'input_releases': input_releases,
            }
    with io.open('config.json', 'w', encoding='utf8') as outfile:
        result = json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
        outfile.write(result)

create_config()
