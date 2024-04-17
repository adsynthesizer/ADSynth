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

import os
import pickle
import json
from adsynth.adsynth_templates.default_config import DEFAULT_CONFIGURATIONS


def get_data_path():
    # return os.path.expanduser("~") + "/.adsynth/data/"
    print(os.getcwd())
    return os.getcwd() + "/data/"


def get_names_pool():
    with open(get_data_path() + 'first.pkl', 'rb') as f:
        return pickle.load(f)
        


def get_surnames_pool():
    with open(get_data_path() + 'last.pkl', 'rb') as f:
        return pickle.load(f)


def get_domains_pool():
    with open(get_data_path() + 'domain.pkl', 'rb') as f:
        return pickle.load(f)


def get_parameters_from_json(json_path):
    try:
        with open(json_path, 'rb') as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_CONFIGURATIONS
    