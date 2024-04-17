import re
from adsynth.DATABASE import DISABLED_USERS, DISTRIBUTION_GROUPS, ENABLED_USERS, FOLDERS, S_TIERS_LOCATIONS, WS_TIERS_LOCATIONS
from adsynth.adsynth_templates.default_config import DEFAULT_CONFIGURATIONS
from adsynth.adsynth_templates.servers import T1_SERVERS
from adsynth.templates.groups import get_departments
from adsynth.templates.ous import STATES
from adsynth.utils.parameters import get_dict_param_value

def get_list_perc_param_value(node, key, parameters):
    try:
        list = parameters[node][key]
        if len(list) != 3:
            return DEFAULT_CONFIGURATIONS[node][key]
        
        for i in range(len(list)):
            if list[i] < 0 or list[i] > 100:
                list[i] = 100       
        return list
    except:
        return DEFAULT_CONFIGURATIONS[node][key]

def get_misconfig_dict_param_value(node, parameters):
    try:
        value = parameters[node]
        if type(value) == dict:
            if (value["allow"] == 0 or value["allow"] == 1) and type(value["limit"]) == int:
                return value["allow"], int(value["limit"])
            else:
                return DEFAULT_CONFIGURATIONS[node]
    except:
        return DEFAULT_CONFIGURATIONS[node]

def get_single_int_param_value(key, parameters):
    try:
        value = parameters[key]
        if type(value) == int and value >= 0:
            return value
        else:
            return DEFAULT_CONFIGURATIONS[key]
    except:
        return DEFAULT_CONFIGURATIONS[key]

def get_num_tiers(parameters):
    try:
        value = parameters["nTiers"]
        if type(value) == int and value > 0:
            return value
        else:
            return DEFAULT_CONFIGURATIONS["nTiers"]
    except:
        return DEFAULT_CONFIGURATIONS["nTiers"]
        
def get_list_param_value(node, key, parameters):
    try:
        value = parameters[node][key]
        if type(value) == list:
            return value
        else:
            return DEFAULT_CONFIGURATIONS[node][key]
    except:
        return DEFAULT_CONFIGURATIONS[node][key]

def get_threshold_values(node, key, parameters):
    try:
        value = parameters[node][key]
        if type(value) == list and len(value) == 2 and value[0] > 0 and value[1] >= value[0]:
            return value
        else:
            return DEFAULT_CONFIGURATIONS[node][key] 
    except:
        return DEFAULT_CONFIGURATIONS[node][key]

def get_total_resources(tier, nTiers, locations, parameters, object_types = ["C"]):
        resources = list()
        if nTiers > 2 and tier < 2:
            resources.extend(get_t1_servers())
            resources.extend(get_list_param_value("Tier_1_Servers", "extraServers", parameters))
        
        lowest_tier_not_admin = min(2, nTiers - 1)
        starting_tier = max(lowest_tier_not_admin, tier)
        departments_probs = get_dict_param_value("Group", "departmentProbability", parameters)
        departments_list = get_departments(departments_probs)

        for i in range(starting_tier, nTiers):
            for type in object_types:
                if type == "C":
                    resources.extend(f"T{i} Workstations {l}" for l in locations)
                    resources.extend(f"T{i} Servers {l}" for l in locations)

                if type == "U":
                    resources.append(f"T{i} Enabled User Accounts")
                    resources.append(f"T{i} Disabled User Accounts")
                
                if type == "G":
                    resources.extend(f"T{i} Distribution {d}" for d in departments_list)
                    resources.extend(f"T{i} Security {d}" for d in departments_list)


        return resources

def get_ou_elements(ou_name):
        patterns = {
            "Workstations": r'T(\d+) Workstations (\w+)', 
            "Servers": r'T(\d+) Servers (\w+)',
            "Distribution": r'T(\d+) Distribution (\S+)',
            "Security": r'T(\d+) Security (\S+)',
            "Enabled": r'T(\d+) Enabled User Accounts',
            "Disabled": r'T(\d+) Disabled User Accounts'       
        }

        # Check the type of OU
        for type in patterns:
            if type in ou_name:
                match = re.match(patterns[type], ou_name)
                if len(match.groups()) > 1:
                    tier = int(match.group(1))
                    department_or_location = match.group(2)
        
                    if type == "Workstations":
                        return WS_TIERS_LOCATIONS[tier][department_or_location], "Computer"
                    if type == "Servers":
                        return S_TIERS_LOCATIONS[tier][department_or_location], "Computer"
                    if type == "Distribution":
                        return DISTRIBUTION_GROUPS[tier][department_or_location], "Group"
                    if type == "Security":
                        return FOLDERS[tier][department_or_location], "Group"

                else:
                    tier = int(match.group(1))
                    if type == "Enabled":
                        return ENABLED_USERS[tier], "User"
                    else:
                        return DISABLED_USERS[tier], "User"
        return [], ""

def get_num_total_resources(tier, nTiers, locations, parameters):
    num_resources = 0
    if nTiers > 2 and tier < 2:
        num_resources += len(get_t1_servers())
        num_resources += len(get_list_param_value("Tier_1_Servers", "extraServers", parameters))
    
    lowest_tier_not_admin = min(2, nTiers - 1)
    starting_tier = max(lowest_tier_not_admin, tier)

    # Number of tiers to target: nTiers - starting_tier
    # Each targeted tier has:
    # + OUs across all locations for Workstations and Servers
    # + 2 OUs for users (enabled & disabled)
    # + OUs across all departments for security and distribution groups
    departments_probs = get_dict_param_value("Group", "departmentProbability", parameters)
    departments_list = get_departments(departments_probs)
    num_resources += (nTiers - starting_tier) * (len(locations) * 2 + 2 + 2 * len(departments_list))

    return num_resources  

def get_t1_servers():
    return T1_SERVERS

def get_locations(parameters):
    num_locations = get_single_int_param_value("nLocations", parameters)
    if num_locations > len(STATES) or num_locations == 0:
        num_locations = DEFAULT_CONFIGURATIONS["nLocations"]
        
    return STATES[:num_locations]    