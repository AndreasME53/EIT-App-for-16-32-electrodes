To install and this EIT app, first install conda.

1. once conda is install or you already have it, change directory into this folder with the conda cmd 
and create an enviroment using this command (where env_name is the enviroment name of your choice):

	'conda create --name <env_name> --file requirements.txt'			

2. When the enviroment is created you are done. Activate the conda enviroment and run 'python main.py'. 
The programe will start running only if the EIT Sciospec device is connected to your pc on port COM3 and is on.

3. In order to change the Sciospecs Settings and EIT App, open main.py in notepad and set the settings.
for information about the EIT APP refer to the Dissertation pdf 3.3 Code Documentation.