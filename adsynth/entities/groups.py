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

from adsynth.templates.groups import STANDARD_GROUPS


def get_forest_default_groups_list(domain_name, domain_sid, old_domain_name):
    groups_list = STANDARD_GROUPS
    for group in groups_list:
        group = set_group_attributes(group, domain_name, domain_sid, old_domain_name)
    return groups_list


def get_forest_default_group_members_list(domain_name, domain_sid, old_domain_name):
    forest_members_list = []
    groups_list = get_forest_default_groups_list(domain_name, domain_sid, old_domain_name)
    for group in groups_list:
        domain_members_list = group["Members"]
        for member in domain_members_list:
            item = {
                "GroupId": group["ObjectIdentifier"],
                "GroupName": group["Properties"]["name"],
                "MemberId": get_group_member_id(member["MemberId"], domain_name, domain_sid),
                "MemberType": member["MemberType"]
            }
            forest_members_list.append(item)
        """
        if str(group["ObjectIdentifier"]).startswith("S-1-5-21") and str(group["ObjectIdentifier"]).endswith("-513"):
            add_domain_users_membership(group, domains_json, ous_json, forest_members_list)
        if str(group["ObjectIdentifier"]).startswith("S-1-5-21") and str(group["ObjectIdentifier"]).endswith("-514"):
            add_domain_guests_membership(group, domains_json, forest_members_list)
        if str(group["ObjectIdentifier"]).startswith("S-1-5-21") and str(group["ObjectIdentifier"]).endswith("-515"):
            add_domain_computers_membership(group, domains_json, ous_json, forest_members_list)
        if str(group["ObjectIdentifier"]).startswith("S-1-5-21") and str(group["ObjectIdentifier"]).endswith("-516"):
            add_domain_controllers_membership(group, ous_json, forest_members_list)
        """
    return forest_members_list


def set_group_attributes(group, domain_name, domain_sid, old_domain_name):
    # TODO add old_sid
    domain_name_splitted = str(domain_name).split(".")
    if old_domain_name is not None:
        old_domain_name_splitted = str(old_domain_name).split(".")
        group["Properties"]["name"] = str(group["Properties"]["name"]).replace(str(old_domain_name), str(domain_name).upper())
    else:
        group["Properties"]["name"] = str(group["Properties"]["name"]).replace("DOMAIN_NAME.DOMAIN_SUFFIX", str(domain_name).upper())
    try:
        group["Properties"]["domain"] = str(domain_name).upper()
    except KeyError:
        pass
    if old_domain_name is not None:
        group["ObjectIdentifier"] = str(group["ObjectIdentifier"]).replace(str(old_domain_name).upper(), str(domain_name).upper())
    else:
        group["ObjectIdentifier"] = str(group["ObjectIdentifier"]).replace("DOMAIN_NAME.DOMAIN_SUFFIX", str(domain_name).upper())
    group["ObjectIdentifier"] = str(group["ObjectIdentifier"]).replace("DOMAIN_SID", domain_sid)
    try:
        if old_domain_name is not None:
            group["Properties"]["distinguishedname"] = str(group["Properties"]["distinguishedname"]).replace(str(old_domain_name_splitted[1]).upper(), str(domain_name_splitted[1]).upper())
            group["Properties"]["distinguishedname"] = str(group["Properties"]["distinguishedname"]).replace(str(old_domain_name_splitted[0]).upper(), str(domain_name_splitted[0]).upper())
        else:
            group["Properties"]["distinguishedname"] = str(group["Properties"]["distinguishedname"]).replace("DOMAIN_SUFFIX", str(domain_name_splitted[1]).upper())
            group["Properties"]["distinguishedname"] = str(group["Properties"]["distinguishedname"]).replace("DOMAIN_NAME", str(domain_name_splitted[0]).upper())
    except KeyError:
        pass
    return group


def get_group_member_id(member_id, domain_name, domain_sid):
    member_id = str(member_id).replace("DOMAIN_SID", domain_sid)
    member_id = str(member_id).replace("DOMAIN_NAME.DOMAIN_SUFFIX", str(domain_name).upper())
    return member_id