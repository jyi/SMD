# SMD
Software Metric tool for Defect prediction

## Installation ##

### Code metrics ###

JRE >= 1.8 is required to run SMD.

### Process metrics ###

SMD uses Python with version greater or equal 3.5 to launch Process metrics sub-module.

## How to use SMD ##

### Code metrics ###

To collect code metrics run from a command line:    
`java -jar smd.jar [Path_to_project] [Path_to_folder_with_csv_output]`

Second argument is optional.

### Process metrics ###

To collect process metrics from particular git project you need to specify .json configuration file.
It should contain the following information:
1) Project file extension ('.java','.py', etc.)
2) Link to the github project, from which you want to obtain metrics.
3) List of input releases, which should contain exactly 2 values: from which to which releases you want to obtain PM.
4) Path to output .csv file, which would create after PM collection. 
5) Path to the directory, which contains project file (or will contain).

After config file creation you need to run following command to start collecting process.   
`python3 [../process_metrics/launcher.py] [path_to_json_config_file]`

## Contributors ##

Developers:

* Bulat Gabdrakhmanov
* Aleksey Tolkachev
