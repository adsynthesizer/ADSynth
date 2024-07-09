# ADSynth: A Tool to Synthesize Realistic Active Directory Attack Graphs
ADSynth models Active Directory attack graphs based on set-to-set mapping, an intrinsic nature of AD systems. The tool generates the structure of AD graphs and security permissions following
design guidelines and security principles from Microsoft and prestigious organizations. In addition, ADSynth integrates common misconfigurations in AD administration, a cause for a myriad of AD attacks. Using our tool, users can generate realistic attack graphs for AD systems at various levels of security, ranging from vulnerable systems to extremely secure ones.

Please head to our <a href="https://adsynthesizer.github.io/">website</a> for more details.

## REQUIREMENTS
* Python 3

## INSTALLATION
```
$ git clone https://github.com/adsynthesizer/ADSynth.git
$ pip install -r requirements.txt
```

## EXECUTION
1. Navigate to the folder ADSynth
```
$ cd <YOUR-PATH>/ADSynth
```
2. Run the program
```
PYTHONPATH=<YOUR-PATH>/ADSynth/adsynth python -m adsynth
```
3. Run the following commands
* ```dbconfig``` - Specify the level of security. There are 2 levels: Low or High. If you want to use your own configuration (**highly recommended**), leave it as Customized.
* ```setparams``` - Set the parameters. Copy and paste the JSON file for your parameters. The template for it is in the file **params_template.json**. Details of parameters are in **params_list.xlsx** or on our <a href="https://adsynthesizer.github.io/">website</a>.
* ```generate``` - Generate the AD attack graph
# ACKNOWLEDGEMENT
We acknowledge the previous work related to AD system from DBCreator, ADSimulator, Microsoft and other sources.
We make citation on the parts we reference.