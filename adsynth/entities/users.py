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

from adsynth.templates.users import GUEST_USER, DEFAULT_ACCOUNT, ADMINISTRATOR, KRBTGT

def get_guest_user(domain_name, domain_sid): 
    return set_user_attributes(GUEST_USER, domain_name, domain_sid)


def get_default_account(domain_name, domain_sid): 
    return set_user_attributes(DEFAULT_ACCOUNT, domain_name, domain_sid)


def get_administrator_user(domain_name, domain_sid): 
    return set_user_attributes(ADMINISTRATOR, domain_name, domain_sid)


def get_krbtgt_user(domain_name, domain_sid): 
    return set_user_attributes(KRBTGT, domain_name, domain_sid)


def set_user_attributes(user, domain_name, domain_sid):
    domain_name_splitted = str(domain_name).split(".")
    user["Properties"]["name"] = str(user["Properties"]["name"]).replace("DOMAIN_NAME.DOMAIN_SUFFIX", str(domain_name).upper())
    user["Properties"]["domain"] = str(domain_name).upper()
    user["ObjectIdentifier"] = str(user["ObjectIdentifier"]).replace("DOMAIN_SID", domain_sid)
    user["Properties"]["distinguishedname"] = str(user["Properties"]["distinguishedname"]).replace("DOMAIN_SUFFIX", str(domain_name_splitted[1]).upper())
    user["Properties"]["distinguishedname"] = str(user["Properties"]["distinguishedname"]).replace("DOMAIN_NAME", str(domain_name_splitted[0]).upper())
    return user


def get_standard_users_list():
    return [GUEST_USER, DEFAULT_ACCOUNT, ADMINISTRATOR, KRBTGT]


def get_forest_user_sid_list(domain_name, domain_sid):
    user_sid_list = []
    domain_users_list = []
    for user in get_standard_users_list():
        domain_users_list.append(set_user_attributes(user, domain_name, domain_sid))
    for user in domain_users_list:
        item = {
            "DomainId": domain_sid,
            "DomainName": str(domain_name).upper(),
            "ObjectId": user["ObjectIdentifier"],
            "ObjectType": "User"
        }
        user_sid_list.append(item)
    return user_sid_list