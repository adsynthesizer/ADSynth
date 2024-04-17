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

import random


CLIENT_OS_LIST = ["Windows 7 Professional Service Pack 1"] * 7 + ["Windows 7 Ultimate Service Pack 1"] * 5 +\
            ["Windows 7 Enterprise Service Pack 1"] * 15 + \
            ["Windows 10 Pro"] * 30 + ["Windows 10 Enterprise"] * 40 +\
            ["Windows XP Professional Service Pack 3"] * 3


SERVER_OS_LIST = ["Windows Server 2003 Enterprise Edition"] * 1 + ["Windows Server 2008 Standard"] * 1 +\
            ["Windows Server 2008 Enterprise"] * 1 + ["Windows Server 2008 Datacenter"] * 1 +\
            ["Windows Server 2008 R2 Standard"] * 2 +\
            ["Windows Server 2008 R2 Enterprise"] * 3 + ["Windows Server 2008 R2 Datacenter"] * 3 +\
            ["Windows Server 2012 Standard"] * 4 + ["Windows Server 2012 Datacenter"] * 4 +\
            ["Windows Server 2012 R2 Standard"] * 10 + ["Windows Server 2012 R2 Datacenter"] * 10 +\
            ["Windows Server 2016 Datacenter"] * 25 + ["Windows Server 2016 Standard"] * 35


VULNERABLE_OS_LIST = ["Windows XP", "Windows 7", "Windows Server 2003", "Windows Server 2008"]


COMPUTER_TYPE_LIST = ["PAW"] * 15 + ["Server"] * 20 + ["Workstation"] * 65


def get_client_os_list(prob):
    sum = 0
    for key in prob.keys():
        sum += prob[key]
    if sum != 100:
        return CLIENT_OS_LIST
    try:
        return ["Windows 7 Professional Service Pack 1"] * prob["Windows 7 Professional Service Pack 1"] +\
            ["Windows 7 Ultimate Service Pack 1"] * prob["Windows 7 Ultimate Service Pack 1"] +\
            ["Windows 7 Enterprise Service Pack 1"] * prob["Windows 7 Enterprise Service Pack 1"] +\
            ["Windows 10 Pro"] * prob["Windows 10 Pro"] +\
            ["Windows 10 Enterprise"] * prob["Windows 10 Enterprise"] +\
            ["Windows XP Professional Service Pack 3"] * prob["Windows XP Professional Service Pack 3"]
    except:
        return CLIENT_OS_LIST


def get_server_os_list(prob):
    sum = 0
    for key in prob.keys():
        sum += prob[key]
    if sum != 100:
        return SERVER_OS_LIST
    try:
        return ["Windows Server 2003 Enterprise Edition"] * prob["Windows Server 2003 Enterprise Edition"] +\
            ["Windows Server 2008 Standard"] * prob["Windows Server 2008 Standard"] +\
            ["Windows Server 2008 Enterprise"] * prob["Windows Server 2008 Enterprise"] +\
            ["Windows Server 2008 Datacenter"] * prob["Windows Server 2008 Datacenter"] +\
            ["Windows Server 2008 R2 Standard"] * prob["Windows Server 2008 R2 Standard"] +\
            ["Windows Server 2008 R2 Enterprise"] * prob["Windows Server 2008 R2 Enterprise"] +\
            ["Windows Server 2008 R2 Datacenter"] * prob["Windows Server 2008 R2 Datacenter"] +\
            ["Windows Server 2012 Standard"] * prob["Windows Server 2012 Standard"] +\
            ["Windows Server 2012 Datacenter"] * prob["Windows Server 2012 Datacenter"] +\
            ["Windows Server 2012 R2 Standard"] * prob["Windows Server 2012 R2 Standard"] +\
            ["Windows Server 2012 R2 Datacenter"] * prob["Windows Server 2012 R2 Datacenter"] +\
            ["Windows Server 2016 Datacenter"] * prob["Windows Server 2016 Datacenter"] +\
            ["Windows Server 2016 Standard"] * prob["Windows Server 2016 Standard"]
    except:
        return SERVER_OS_LIST


def get_computer_type_list(prob):
    sum = 0
    for key in prob.keys():
        sum += prob[key]
    if sum != 100:
        return COMPUTER_TYPE_LIST
    try:
        return ["PAW"] * prob["PAW"] + ["Server"] * prob["Server"] + ["Workstation"] * prob["Workstation"]
    except:
        return COMPUTER_TYPE_LIST


def get_main_dc_os(functional_level):
    if functional_level == "2008":
        return random.choice(["Windows Server 2008 Standard", "Windows Server 2008 Enterprise", "Windows Server 2008 Datacenter"])
    elif functional_level == "2008 R2":
        return random.choice(["Windows Server 2008 R2 Standard", "Windows Server 2008 R2 Enterprise", "Windows Server 2008 R2 Datacenter"])
    elif functional_level == "2012":
        return random.choice(["Windows Server 2012 Standard", "Windows Server 2012 Datacenter"])
    elif functional_level == "2012 R2":
        return random.choice(["Windows Server 2012 R2 Standard", "Windows Server 2012 R2 Datacenter"])
    elif functional_level == "2016":
        return random.choice(["Windows Server 2016 Standard", "Windows Server 2016 Datacenter"])
    else:
        return random.choice(SERVER_OS_LIST)
