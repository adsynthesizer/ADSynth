from tabulate import tabulate
from adsynth.utils.colors import O, W


SW_NAME = "ADSynth"
SW_VERSION = "1.1.1"
RELEASE_DATE = "2024-02-28"


def print_adsynth_software_information():
    print()
    print(tabulate([[O + 'Software name:' + W, SW_NAME],
                    [O + 'Version:' + W, SW_VERSION],
                    [O + 'Release date:' + W, RELEASE_DATE]], tablefmt='grid'))
    print()