import copy
from adsynth.DATABASE import ADMIN_USERS, DISABLED_USERS, DISTRIBUTION_GROUPS, ENABLED_USERS, FOLDERS, KERBEROASTABLES, LOCAL_ADMINS, PAW_TIERS, S_TIERS, S_TIERS_LOCATIONS, SECURITY_GROUPS, WS_TIERS, WS_TIERS_LOCATIONS
from adsynth.adsynth_templates.servers import T1_SERVERS
from adsynth.helpers.getters import get_list_param_value, get_locations
from adsynth.helpers.objects import create_sub_objects

# Idea Ref: Microsoft, https://www.microsoft.com/en-au/download/details.aspx?id=36036
def create_ad_skeleton(domain_name, domain_sid, parameters, nTiers):
    # Domain
    high_privileged_ous = ['Admin', 'Tier 1 Servers']

    if nTiers == 1:
        high_privileged_ous[1] = 'Tier 0'
    elif nTiers == 2:
        high_privileged_ous[1] = 'Tier 1'

    sub_list = high_privileged_ous
    sub_list.extend([f"Tier {i}" for i in range(2, nTiers)])
    parent_name = domain_name

    create_sub_objects(domain_name, domain_sid, parent_name, "Domain", sub_list, "OU", "Contains")

    # AdminOU
    # Child OUs - admin tiers
    sub_list = [f"T{i} Admin" for i in range(0, nTiers)]
    parent_name = "Admin"
    create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")

    # Each child OU - admin tier - contains subOUs, including Accounts, Devices, Groups and Service Accounts
    AS = ["Accounts", "Devices", "Groups", "Service Accounts"]
    for i in range(nTiers):
        sub_list = [f"T{i} Admin {sub}" for sub in AS]
        parent_name = f"T{i} Admin"
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")


    # Tier 1 Servers OU
    if nTiers > 2:
        sub_list = copy.deepcopy(T1_SERVERS)
        sub_list.extend(get_list_param_value("Tier_1_Servers", "extraServers", parameters)) # Get extra services
        parent_name = 'Tier 1 Servers'
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")


    # Tiered OUs
    TS = ["Groups", "Workstations", "User Accounts", "Servers"]
    UA = ["Enabled User Accounts", "Disabled User Accounts"]
    TG = ["Distribution Groups", "Security Groups"]
    locations = get_locations(parameters)
    lowest_tier_not_admin = min(2, nTiers - 1)
    for i in range(lowest_tier_not_admin, nTiers):
        sub_list = [f"T{i} {sub}" for sub in TS]
        parent_name = f"Tier {i}"
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")

        # Child OUs - User Accounts
        sub_list = [f"T{i} {sub}" for sub in UA]
        parent_name = f"T{i} User Accounts"
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")


        # Child OUs - Workstations - Geographical subdivisions
        sub_list = [f"T{i} Workstations {sub}" for sub in locations]
        parent_name = f"T{i} Workstations"
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")


        # Child OUs - Groups
        sub_list = [f"T{i} {sub}" for sub in TG]
        parent_name = f"T{i} Groups"
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")

        # Child OUs - Servers - Geographical subdivisions
        sub_list = [f"T{i} Servers {sub}" for sub in locations]
        parent_name = f"T{i} Servers"
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")


    # Initialize storage for admin users, normal users and PAW, groups and computers
    ADMIN_USERS.extend([[] for _ in range(nTiers)])
    ENABLED_USERS.extend([[] for _ in range(nTiers)])
    DISABLED_USERS.extend([[] for _ in range(nTiers)])
    PAW_TIERS.extend([[] for _ in range(nTiers)])
    S_TIERS.extend([[] for _ in range(nTiers)])
    WS_TIERS.extend([[] for _ in range(nTiers)])
    SECURITY_GROUPS.extend([[] for _ in range(nTiers)])
    LOCAL_ADMINS.extend([[] for _ in range(nTiers)])
    KERBEROASTABLES.extend([])
    FOLDERS.extend([dict() for _ in range(nTiers)])
    DISTRIBUTION_GROUPS.extend([dict() for _ in range(nTiers)])
    S_TIERS_LOCATIONS.extend([dict() for _ in range(nTiers)])
    WS_TIERS_LOCATIONS.extend([dict() for _ in range(nTiers)])
    
    locations = get_locations(parameters)
    for i in range(nTiers):
        for l in locations:
            S_TIERS_LOCATIONS[i][l] = list()
            WS_TIERS_LOCATIONS[i][l] = list()  
 