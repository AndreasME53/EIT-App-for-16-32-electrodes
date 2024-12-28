## Description 

This is My Software Contributions to the Development of a Low-Cost Chest Electrical Impedance Tomography (EIT) Harness for Fitness and Telemedicine.

I give a detailed analysis in my dissertation, thus I recommend all viewers to read my paper before [continuing](https://github.com/AndreasME53/EIT-App-for-16-32-electrodes/blob/main/Documentation%20to%20the%20Development%20of%20a%20Low-Cost%20Chest%20Electrical%20Impedance.pdf).



#### Getting Started

In order to get started developing and using the APP, you'll need to do a few things first. 

Due to the size of my APP I recommend you to download it from my [onedrive](https://liveuclac-my.sharepoint.com/my?id=%2Fpersonal%2Fucaba53%5Fucl%5Fac%5Fuk%2FDocuments%2FMicrosoft%20Teams%20Chat%20Files%2FEIT%5FAPP%5Ffor%5F32%5Fand%5F16%5Fsystem%2Ezip&parent=%2Fpersonal%2Fucaba53%5Fucl%5Fac%5Fuk%2FDocuments%2FMicrosoft%20Teams%20Chat%20Files&ga=1), As I use 2 large jacobian matrixes to models the electrodes.

I recommend using conda.

1. Once conda is install or you already have it, change directory into this folder with the conda cmd 
and create an enviroment using this command (where env_name is the enviroment name of your choice):

	'conda create --name <env_name> --file requirements.txt'			

2. When the enviroment is created you are done. Activate the conda enviroment and run 'python main.py'. 
The programe will start running only if the EIT Sciospec device is connected to your pc on port COM3 and is on.

3. In order to change the Sciospecs Settings and EIT App, open main.py in notepad and set the settings.
for information about the EIT APP refer to the Dissertation pdf 3.3 Code Documentation.
