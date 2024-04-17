# Ideas are from ADSimulator
DEFAULT_CONFIGURATIONS = {
    "Domain": {
        "functionalLevelProbability": {
            "2008": 4,
            "2008 R2": 5,
            "2012": 10,
            "2012 R2": 30,
            "2016": 50,
            "Unknown": 1
        }
    },
    "Computer": {
        "nComputers": 200,
        "enabled": 90,
        "haslaps": 10,
        "unconstraineddelegation": 10,
        "osProbability": {
            "Windows XP Professional Service Pack 3": 3,
            "Windows 7 Professional Service Pack 1": 7,
            "Windows 7 Ultimate Service Pack 1": 5,
            "Windows 7 Enterprise Service Pack 1": 15,
            "Windows 10 Pro": 30,
            "Windows 10 Enterprise": 40
        },
        "privesc": 30,
        "creddump": 40,
        "exploitable": 40,
        "computerProbability": {
            "PAW": 15,
            "Server": 20,
            "Workstation": 65
        }
    },
    "DC": {
        "enabled": 90,
        "haslaps": 10,
        "osProbability": {
            "Windows Server 2003 Enterprise Edition": 1,
            "Windows Server 2008 Standard": 1,
            "Windows Server 2008 Datacenter": 1,
            "Windows Server 2008 Enterprise": 1,
            "Windows Server 2008 R2 Standard": 2,
            "Windows Server 2008 R2 Datacenter": 3,
            "Windows Server 2008 R2 Enterprise": 3,
            "Windows Server 2012 Standard": 4,
            "Windows Server 2012 Datacenter": 4,
            "Windows Server 2012 R2 Standard": 10,
            "Windows Server 2012 R2 Datacenter": 10,
            "Windows Server 2016 Standard": 35,
            "Windows Server 2016 Datacenter": 25
        }
    },
    "User": {
        "nUsers": 200,
        "enabled": 85,
        "dontreqpreauth": 5,
        "hasspn": 10,
        "passwordnotreqd": 5,
        "pwdneverexpires": 50,
        "sidhistory": 10,
        "unconstraineddelegation": 20,
        "savedcredentials": 40,
        "Kerberoastable" : [3, 5],
        "sessionsPercentages": [10, 10, 10],
        "priority_session_weight": 3,
        "perc_special_roles": 10
    },
    "Group": {
        "nestingGroupProbability": 30,
        "departmentProbability": {
            "IT": 25,
            "R&D": 25,
            "BUSINESS": 25,
            "HR": 25
        },
        "nResourcesThresholds": [20, 50],
        "nLocalAdminsPerDepartment": [5, 10],
        "nOUsPerLocalAdmins": [3, 5],
        "nGroupsPerUsers": [3,5]
    },
    "GPO": {
        "nGPOs": 170,
        "exploitable": 30
    },
    "ACLs": {
        "ACLPrincipalsPercentage": 50,
        "ACLsProbability": {
            "GenericAll": 10,
            "GenericWrite": 15,
            "WriteOwner": 15,
            "WriteDacl": 15,
            "AddMember": 30,
            "ForceChangePassword": 15,
            "AllExtendedRights": 10
        },
        "ACLPrivilegedPercentage": 5
    },
    "nonACLs": {
        "nonACLsPercentage": 10,
        "nonACLsProbability": {
            "CanRDP": 25,
            "ExecuteDCOM": 25,
            "AllowedToDelegate": 25,
            "ReadLAPSPassword": 25
        }        
    },
    "perc_misconfig_sessions": {
        "Low": 10, 
        "High": 1,
        "Customized": 10
    },
    "perc_misconfig_permissions": {
        "Low": 10, 
        "High": 1,
        "Customized": 10
    },
    "perc_misconfig_permissions_on_groups": {
        "Low": 100, 
        "High": 80,
        "Customized": 80
    },
    "perc_misconfig_nesting_groups": {
        "Low": 10,
        "High": 1,
        "Customized": 1
    },
    "misconfig_permissions_to_tier_0": {
        "allow": 1,
        "limit": 10
    },
    "misconfig_group": {
        "acl_ratio": 1,
        "admin_ratio": 1,
        "priority_paws_weight": 3
    },
    "nTiers": 3,
    "Tier_1_Servers": {
        "extraServers": []
    },
    "Admin": {
        "service_account": 15,
        "Admin_Percentage": 20,
    },
    "nodeMisconfig": {
        "admin_regular": 10,
        "user_comp": 10
    },
    "nLocations": 3,
    "convert_to_directed_graphs": 0,
    "seed": 1
}


def get_complementary_value(value):
    return 100 - value
