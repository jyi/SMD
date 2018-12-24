# SMD
Software Metric tool for Defect prediction

## Installation ##

### Code metrics ###

JRE >= 1.8 is required to run SMD.

You can download binary distribution from [https://github.com/jyi/SMD/releases](https://github.com/jyi/SMD/releases),    
In order to build from sources you need [gradle build tool](https://gradle.org/). Type `gradle fatJar` in a command line.

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

## Publications ##

**SMD: An Open-Source Software Metric Tool for Defect Prediction, Its Case Study and Lessons We Learned.** Bulat Gabdrakhmanov, Aleksey Tolkachev, Giancarlo Succi, and Jooyong Yi. SEDA'18

## Contributors ##

Developers:

* Bulat Gabdrakhmanov
* Aleksey Tolkachev

Principal investigator:

* Jooyong Yi
