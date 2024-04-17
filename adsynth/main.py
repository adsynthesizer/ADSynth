__all__ = ()

import sys
from adsynth.ADSynth import MainMenu

def main():    
    try:
        MainMenu().cmdloop()
    except KeyboardInterrupt:
        print("Exiting ADSynth")
        sys.exit()
