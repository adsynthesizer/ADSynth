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

GUEST_USER = {
      "Properties": {
        "highvalue": False,
        "name": "GUEST@DOMAIN_NAME.DOMAIN_SUFFIX",
        "domain": "DOMAIN_NAME.DOMAIN_SUFFIX",
        "objectid": "DOMAIN_SID-501",
        "distinguishedname": "CN=Guest,CN=Users,DC=DOMAIN_NAME,DC=DOMAIN_SUFFIX",
        "description": "Built-in account for guest access to the computer/domain",
        "dontreqpreauth": False,
        "passwordnotreqd": True,
        "unconstraineddelegation": False,
        "sensitive": False,
        "enabled": False,
        "pwdneverexpires": True,
        "lastlogon": -1,
        "lastlogontimestamp": -1,
        "pwdlastset": -1,
        "serviceprincipalnames": [],
        "hasspn": False,
        "displayname": "null",
        "email": "null",
        "title": "null",
        "homedirectory": "null",
        "userpassword": "null",
        "admincount": False,
        "sidhistory": []
      },
      "AllowedToDelegate": [],
      "SPNTargets": [],
      "PrimaryGroupSid": "DOMAIN_SID-514",
      "HasSIDHistory": [],
      "ObjectIdentifier": "DOMAIN_SID-501",
      "Aces": [
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "Owner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-548",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": True
        }
      ]
    }


DEFAULT_ACCOUNT = {
      "Properties": {
        "highvalue": False,
        "name": "DEFAULTACCOUNT@DOMAIN_NAME.DOMAIN_SUFFIX",
        "domain": "DOMAIN_NAME.DOMAIN_SUFFIX",
        "objectid": "DOMAIN_SID-503",
        "distinguishedname": "CN=DefaultAccount,CN=Users,DC=DOMAIN_NAME,DC=DOMAIN_SUFFIX",
        "description": "A user account managed by the system.",
        "dontreqpreauth": False,
        "passwordnotreqd": True,
        "unconstraineddelegation": False,
        "sensitive": False,
        "enabled": False,
        "pwdneverexpires": True,
        "lastlogon": -1,
        "lastlogontimestamp": -1,
        "pwdlastset": -1,
        "serviceprincipalnames": [],
        "hasspn": False,
        "displayname": "null",
        "email": "null",
        "title": "null",
        "homedirectory": "null",
        "userpassword": "null",
        "admincount": False,
        "sidhistory": []
      },
      "AllowedToDelegate": [],
      "SPNTargets": [],
      "PrimaryGroupSid": "DOMAIN_SID-513",
      "HasSIDHistory": [],
      "ObjectIdentifier": "DOMAIN_SID-503",
      "Aces": [
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "Owner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-548",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "GenericAll",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": True
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": True
        }
      ]
    }


ADMINISTRATOR = {
      "Properties": {
        "highvalue": False,
        "name": "ADMINISTRATOR@DOMAIN_NAME.DOMAIN_SUFFIX",
        "domain": "DOMAIN_NAME.DOMAIN_SUFFIX",
        "objectid": "DOMAIN_SID-500",
        "distinguishedname": "CN=Administrator,CN=Users,DC=DOMAIN_NAME,DC=DOMAIN_SUFFIX",
        "description": "Built-in account for administering the computer/domain",
        "dontreqpreauth": False,
        "passwordnotreqd": False,
        "unconstraineddelegation": False,
        "sensitive": False,
        "enabled": True,
        "pwdneverexpires": True,
        "lastlogon": 1601019126,
        "lastlogontimestamp": 1600849229,
        "pwdlastset": 1588772520,
        "serviceprincipalnames": [],
        "hasspn": False,
        "displayname": "null",
        "email": "null",
        "title": "null",
        "homedirectory": "null",
        "userpassword": "null",
        "admincount": True,
        "sidhistory": []
      },
      "AllowedToDelegate": [],
      "SPNTargets": [],
      "PrimaryGroupSid": "DOMAIN_SID-513",
      "HasSIDHistory": [],
      "ObjectIdentifier": "DOMAIN_SID-500",
      "Aces": [
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "Owner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": False
        }
      ]
    }


KRBTGT = {
      "Properties": {
        "highvalue": False,
        "name": "KRBTGT@DOMAIN_NAME.DOMAIN_SUFFIX",
        "domain": "DOMAIN_NAME.DOMAIN_SUFFIX",
        "objectid": "DOMAIN_SID-502",
        "distinguishedname": "CN=krbtgt,CN=Users,DC=DOMAIN_NAME,DC=DOMAIN_SUFFIX",
        "description": "Key Distribution Center Service Account",
        "dontreqpreauth": False,
        "passwordnotreqd": False,
        "unconstraineddelegation": False,
        "sensitive": False,
        "enabled": False,
        "pwdneverexpires": False,
        "lastlogon": -1,
        "lastlogontimestamp": -1,
        "pwdlastset": 1584136849,
        "serviceprincipalnames": [
          "kadmin/changepw"
        ],
        "hasspn": True,
        "displayname": "null",
        "email": "null",
        "title": "null",
        "homedirectory": "null",
        "userpassword": "null",
        "admincount": True,
        "sidhistory": []
      },
      "AllowedToDelegate": [],
      "SPNTargets": [],
      "PrimaryGroupSid": "DOMAIN_SID-513",
      "HasSIDHistory": [],
      "ObjectIdentifier": "DOMAIN_SID-502",
      "Aces": [
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "Owner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_NAME.DOMAIN_SUFFIX-S-1-5-32-544",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-512",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "WriteDacl",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "WriteOwner",
          "AceType": "",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "ExtendedRight",
          "AceType": "All",
          "IsInherited": False
        },
        {
          "PrincipalSID": "DOMAIN_SID-519",
          "PrincipalType": "Group",
          "RightName": "GenericWrite",
          "AceType": "",
          "IsInherited": False
        }
      ]
    }
