# =======================================================
# Appendix B. License for adsimulator
# =======================================================
# :Info: This is the license for adsimulator.
# :Author: Nicolas Carolo <nicolascarolo.dev@gmail.com>
# :Copyright: © 2022, Nicolas Carolo.
# :License: BSD (see /LICENSE or :doc:`Appendix B <LICENSE>`.)
# :Date: 2022-06-29
# :Version: 1.1.1

# .. index:: LICENSE

# Copyright © 2022, Nicolas Carolo.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# 3. Neither the name of the author of this software nor the names of
#    contributors to this software may be used to endorse or promote
#    products derived from this software without specific prior written
#    consent.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
from adsynth.adsynth_templates.default_config import DEFAULT_CONFIGURATIONS
    
def print_all_parameters(parameters):
    print("")
    print("New Settings:")
    print(json.dumps(parameters, indent=4, sort_keys=True))

def get_perc_param_value(node, key, parameters):
    try:
        if 0 <= parameters[node][key] <= 100:
            return parameters[node][key]
        else:
            return 100
    except:
        return DEFAULT_CONFIGURATIONS[node][key]

def get_dict_param_value(node, key, parameters):
    try:
        value = parameters[node][key]
        if type(value) == dict:
            return value
        else:
            return DEFAULT_CONFIGURATIONS[node][key]
    except:
        return DEFAULT_CONFIGURATIONS[node][key]

def get_int_param_value(node, key, parameters):
    try:
        value = parameters[node][key]
        if type(value) == int and value > 0:
            return value
        else:
            return DEFAULT_CONFIGURATIONS[node][key]
    except:
        return DEFAULT_CONFIGURATIONS[node][key]

def get_int_param_value_with_upper_limit(node, key, parameters, max_value):
    try:
        value = parameters[node][key]
        if type(value) == int and 0 < value <= max_value:
            return value
        if type(value) == int and value > max_value:
            return max_value
        else:
            return DEFAULT_CONFIGURATIONS[node][key]
    except:
        return DEFAULT_CONFIGURATIONS[node][key]

def print_computer_generation_parameters(enabled, has_laps, unconstrained_delegation, prob):
    print("\t- Enabled computer probability:", str(enabled), "%")
    print("\t- HasLaps computer probability:", str(has_laps), "%")
    print("\t- Unconstrained delegation computer probability:", str(unconstrained_delegation), "%")
    
    sum = 0
    for key in prob.keys():
        sum += prob[key]
    if sum != 100:
        prob = DEFAULT_CONFIGURATIONS["Computer"]["osProbability"]
    print("\t- Computer OS probability:")
    print("\t\t- Windows XP Professional Service Pack 3:", str(prob["Windows XP Professional Service Pack 3"]), "%")
    print("\t\t- Windows 7 Professional Service Pack 1:", str(prob["Windows 7 Professional Service Pack 1"]), "%")
    print("\t\t- Windows 7 Ultimate Service Pack 1:", str(prob["Windows 7 Ultimate Service Pack 1"]), "%")
    print("\t\t- Windows 7 Enterprise Service Pack 1:", str(prob["Windows 7 Enterprise Service Pack 1"]), "%")
    print("\t\t- Windows 10 Pro:", str(prob["Windows 10 Pro"]), "%")
    print("\t\t- Windows 10 Enterprise:", str(prob["Windows 10 Enterprise"]), "%")



def print_dc_generation_parameters(enabled, has_laps, prob):
    print("\t- Enabled DC probability:", str(enabled), "%")
    print("\t- HasLaps DC probability:", str(has_laps), "%")
    
    sum = 0
    for key in prob.keys():
        sum += prob[key]
    if sum != 100:
        prob = DEFAULT_CONFIGURATIONS["DC"]["osProbability"]
    print("\t- Domain Controller OS probability:")
    print("\t\t- Windows Server 2003 Enterprise Edition:", str(prob["Windows Server 2003 Enterprise Edition"]), "%")
    print("\t\t- Windows Server 2008 Standard:", str(prob["Windows Server 2008 Standard"]), "%")
    print("\t\t- Windows Server 2008 Datacenter:", str(prob["Windows Server 2008 Datacenter"]), "%")
    print("\t\t- Windows Server 2008 Enterprise:", str(prob["Windows Server 2008 Enterprise"]), "%")
    print("\t\t- Windows Server 2008 R2 Standard:", str(prob["Windows Server 2008 R2 Standard"]), "%")
    print("\t\t- Windows Server 2008 R2 Datacenter:", str(prob["Windows Server 2008 R2 Datacenter"]), "%")
    print("\t\t- Windows Server 2008 R2 Enterprise:", str(prob["Windows Server 2008 R2 Enterprise"]), "%")
    print("\t\t- Windows Server 2012 Standard:", str(prob["Windows Server 2012 Standard"]), "%")
    print("\t\t- Windows Server 2012 Datacenter:", str(prob["Windows Server 2012 Datacenter"]), "%")
    print("\t\t- Windows Server 2012 R2 Standard:", str(prob["Windows Server 2012 R2 Standard"]), "%")
    print("\t\t- Windows Server 2012 R2 Datacenter:", str(prob["Windows Server 2012 R2 Datacenter"]), "%")
    print("\t\t- Windows Server 2016 Standard:", str(prob["Windows Server 2016 Standard"]), "%")
    print("\t\t- Windows Server 2016 Datacenter:", str(prob["Windows Server 2016 Datacenter"]), "%")


def print_user_generation_parameters(enabled, dontreqpreauth, hasspn, passwordnotreqd, pwdneverexpires, unconstraineddelegation, sidhistory):
    print("\t- Enabled user probability:", str(enabled), "%")
    print("\t- Dontreqpreauth user probability:", str(dontreqpreauth), "%")
    print("\t- Dontreqpreauth user probability:", str(dontreqpreauth), "%")
    print("\t- Hasspn user probability:", str(hasspn), "%")
    print("\t- Passwordnotreqd user probability:", str(passwordnotreqd), "%")
    print("\t- Pwdneverexpires user probability:", str(pwdneverexpires), "%")
    print("\t- Unconstrained delegation user probability:", str(unconstraineddelegation), "%")
    print("\t- User has SID History probability:", str(sidhistory), "%")


def print_domain_generation_parameters(prob):
    sum = 0
    for key in prob.keys():
        sum += prob[key]
    if sum != 100:
        prob = DEFAULT_CONFIGURATIONS["Domain"]["functionalLevelProbability"]
    print("\t- Functional level probability:")
    print("\t\t- 2008:", str(prob["2008"]), "%")
    print("\t\t- 2008 R2:", str(prob["2008 R2"]), "%")
    print("\t\t- 2012:", str(prob["2012"]), "%")
    print("\t\t- 2012 R2:", str(prob["2012 R2"]), "%")
    print("\t\t- 2016:", str(prob["2016"]), "%")
    print("\t\t- Unknown:", str(prob["Unknown"]), "%")


