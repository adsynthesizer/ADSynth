
import math
from adsynth.DATABASE import ADMIN_USERS, DISABLED_USERS, ENABLED_USERS, FOLDERS, NODE_GROUPS, NODES, PAW_TIERS, S_TIERS, S_TIERS_LOCATIONS, SECURITY_GROUPS, WS_TIERS, WS_TIERS_LOCATIONS, edge_operation, get_node_index, node_operation, ridcount
from adsynth.adsynth_templates.servers import T1_SERVERS
from adsynth.entities.acls import cn
from adsynth.helpers.distinguished_names import add_dn
from adsynth.helpers.getters import get_list_param_value, get_locations, get_threshold_values
from adsynth.helpers.objects import add_sub_objects, create_sub_objects, add_admin_tiers
from adsynth.adsynth_templates.default_config import get_complementary_value
from adsynth.templates.groups import get_departments_list
from adsynth.utils.boolean import generate_boolean_value
from adsynth.utils.parameters import get_dict_param_value, get_perc_param_value
from adsynth.utils.principals import get_sid_from_rid
import random
import copy

def place_computers_in_tiers(domain_name, domain_sid, nTiers, parameters, PAW, Servers, Workstations, misconfig_users_comps):
    place_paws_in_tiers(domain_name, domain_sid, PAW, nTiers)
    place_servers_in_tiers(domain_name, domain_sid, parameters, Servers, nTiers)
    place_workstations_in_tiers(domain_name, domain_sid, Workstations, misconfig_users_comps, nTiers, parameters)

def place_paws_in_tiers(domain_name, domain_sid, PAW, nTiers):
    # Generate default PAWs for each tier
    for i in range(0, nTiers):
        sub_list = [f"T{i} DEFAULT PAW"]
        # print(sub_list[0])
        PAW_TIERS[i].append(cn(sub_list[0], domain_name))
        parent_name = f"T{i} Admin Devices"
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "Computer", "Contains")
        
        # Add/Update distinguished name
        ous_dn = ["Admin", f"T{i} Admin", f"T{i} Admin Devices"]
        add_dn(domain_name, cn(sub_list[0], domain_name), "Computer", ous_dn)


    for pc in PAW:
        # Tn Admin Devices --Contains--> Computer
        tier = random.randrange(0, nTiers)
        PAW_TIERS[tier].append(pc)
        start_name = f"T{tier} Admin Devices"
        start_index = get_node_index(cn(start_name, domain_name) + "_OU", "name")
        end_index = get_node_index(pc + "_Computer", "name")
        rel_type = "Contains"
        edge_operation(start_index, end_index, rel_type)

        # Add/Update distinguished name
        ous_dn = ["Admin", f"T{tier} Admin", f"T{tier} Admin Devices"]
        add_dn(domain_name, pc, "Computer", ous_dn)

def place_servers_in_tiers(domain_name, domain_sid, parameters, Servers, nTiers):
    # Locations
    locations = get_locations(parameters)

    # Default Tier 1 Servers
    t1_servers = copy.deepcopy(T1_SERVERS)
    t1_servers.extend(get_list_param_value("Tier_1_Servers", "extraServers", parameters)) # Get extra services
    
    # Default Tier 1 servers
    if nTiers > 2:
        for s in t1_servers:
            sub_list = [f"T1 DEFAULT {s} SERVER"]
            parent_name = s
            S_TIERS[1].append(cn(sub_list[0], domain_name))
            create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "Computer", "Contains")
            
            # Add/Update distinguished name
            ous_dn = ["Tier 1 Servers", s]
            add_dn(domain_name, cn(sub_list[0], domain_name), "Computer", ous_dn)

    lowest_tier_no_admin = min(1, nTiers - 1)

    for comp in Servers:
        tier = random.randrange(lowest_tier_no_admin, nTiers)
        if tier == 1 and nTiers > 2:
            parent_name = random.choice(t1_servers)
            ous_dn = ["Tier 1 Servers", parent_name]
        else:
            l = random.choice(locations)
            parent_name = f"T{tier} Servers {l}"
            ous_dn = [f"Tier {tier}", f"T{tier} Servers", parent_name]
            S_TIERS_LOCATIONS[tier][l].append(comp)
        
        # Add/Update distinguished name
        add_dn(domain_name, comp, "Computer", ous_dn)
        S_TIERS[tier].append(comp)
        
        sub_list = [comp]
        add_sub_objects(domain_name, parent_name, "OU", sub_list, "Computer", "Contains", True)

def place_workstations_in_tiers(domain_name, domain_sid, Workstations, misconfig_users_comps, nTiers, parameters):
    locations = get_locations(parameters)
    lowest_tier_no_admin = min(2, nTiers - 1)

    def place_object_in_ous(array, object_type):
        for obj in array:
            tier = random.randrange(lowest_tier_no_admin, nTiers)
            l = random.choice(locations)
            if object_type == "Computer":
                WS_TIERS[tier].append(obj)
                WS_TIERS_LOCATIONS[tier][l].append(obj)

            sub_list = [obj]
            parent_name = f"T{tier} Workstations {l}"
            add_sub_objects(domain_name, parent_name, "OU", sub_list, object_type, "Contains", True)
            
            # Add/Update distinguished name
            ous_dn = [f"Tier {tier}", f"T{tier} Workstations", parent_name]
            add_dn(domain_name, obj, object_type, ous_dn)
    
    place_object_in_ous(Workstations, "Computer")
    place_object_in_ous(misconfig_users_comps, "User")

def place_admin_users_in_tiers(domain_name, domain_sid, nTiers, admin, misconfig_regular_users, server_operators, print_operators, parameters):
    # DEFAULT ADMIN USERS for each tier
    for i in range(0, nTiers):
        # Create an admin user
        user = cn(f"T{i} DEFAULT ADMIN USER", domain_name) 
        ADMIN_USERS[i].append(user)
        guid = get_sid_from_rid(ridcount[0], domain_sid)
        ridcount[0] += 1

        keys = ["domain", "name", "objectid", "labels", "highvalue"]
        values = [domain_name, user, guid, "User", True]
        id_lookup = guid
        node_operation("User", keys, values, id_lookup)
        
        ous_dn = ["Admin", f"T{i} Admin"]

        #Add to an admin OU and admin group
        add_admin_tiers(domain_name, user, i, False, server_operators, print_operators, ous_dn)

    # ADMIN USERS
    service_account_perc = get_perc_param_value("Admin", "service_account", parameters)
    keys = ["admincount", "highvalue"]
    values = [True, True]

    for user in admin:
        tier = random.randrange(nTiers)
        account_type = generate_boolean_value(service_account_perc, get_complementary_value(service_account_perc)) #Admin Accounts or Admin Service Accounts
        ADMIN_USERS[tier].append(user)
        
        node_operation("User", keys, values, user, "name")
        ous_dn = ["Admin", f"T{tier} Admin"]
        add_admin_tiers(domain_name, user, tier, account_type, server_operators, print_operators, ous_dn)

    # Misconfigured regular users in Admin OUs
    keys = ["admincount"]
    values = [False]
    for user in misconfig_regular_users:
        tier = random.randrange(nTiers)
        account_type = False
        ADMIN_USERS[tier].append(user)

        node_operation("User", keys, values, user, "name")
        ous_dn = ["Admin", f"T{tier} Admin"]
        add_admin_tiers(domain_name, user, tier, account_type, server_operators, print_operators, ous_dn)

def place_normal_users_in_tiers(domain_name, enabled_users, disabled_users, misconfig_admin, misconfig_workstations, nTiers):
    def add_normal_users(domain_name, nTiers, user_list, object_type, is_enabled, is_admin = False):
        lowest_tier_not_admin = min(2, nTiers - 1)
        ou_name = "Enabled User Accounts" if is_enabled else "Disabled User Accounts"
        rel_type = "Contains"
        for user in user_list:
            tier = random.randrange(lowest_tier_not_admin, nTiers)  
            start_name = f"T{tier} {ou_name}"
            start_index = get_node_index(cn(start_name, domain_name) + "_OU", "name")
            end_index = get_node_index(f"{user}_{object_type}", "name") 
            
            edge_operation(start_index, end_index, rel_type)

            if object_type == "Computer":
                continue

            if is_enabled:
                keys = ["admincount"]
                if not is_admin:
                    values = [False]
                else:
                    values = [True]
                node_operation("User", keys, values, user, "name")
                ENABLED_USERS[tier].append(user)
                parent_name = f"T{tier} Enabled Users"
            else:
                DISABLED_USERS[tier].append(user)
                parent_name = f"T{tier} Disabled Users"
            ous_dn = [f"Tier {tier}", f"T{tier} Users", parent_name]
            add_dn(domain_name, user, object_type, ous_dn)
    
    add_normal_users(domain_name, nTiers, enabled_users, "User", True)
    add_normal_users(domain_name, nTiers, disabled_users, "User", False)
    add_normal_users(domain_name, nTiers, misconfig_admin, "User", True, True)
    add_normal_users(domain_name, nTiers, misconfig_workstations, "Computer", True)

def place_users_in_groups(domain_name, nTiers, parameters):
    locations = get_locations(parameters)
    it_users = []
    departments_probs = get_dict_param_value("Group", "departmentProbability", parameters)
    departments_list = get_departments_list(departments_probs)
    for i in range(nTiers):
        for user in ENABLED_USERS[i]:
            # Add to a distribution group
            d = random.choice(departments_list)
            if d == 'IT':
                it_users.append(user)
            s = random.choice(locations)
            dist_group = f"T{i} Distribution {d}_{s}"
            start_index = get_node_index(f"{user}_User", "name")
            end_index = get_node_index(cn(dist_group, domain_name) + "_Group", "name")
            edge_operation(start_index, end_index, "MemberOf")

            # Add to several security groups
            thresholds_group_member = get_threshold_values("Group", "nGroupsPerUsers", parameters)
            num_groups = random.randint(thresholds_group_member[0], thresholds_group_member[1])
            group_list = random.sample(SECURITY_GROUPS[i], min(num_groups, len(SECURITY_GROUPS[i])))
            
            for g in group_list:
                sec_group = g
                end_index = get_node_index(sec_group + "_Group", "name")
                edge_operation(start_index, end_index, "MemberOf")
    
    return it_users

# Idea Ref: DBCreator and ADSimulator
def nest_groups(domain_name, parameters):
    num_groups = len(NODE_GROUPS["Group"])
    max_nest = int(round(math.log10(num_groups)))
    nesting_perc = get_perc_param_value("Group", "nestingGroupProbability", parameters)

    # Aim at security groups
    for g in NODE_GROUPS["Group"]:
        if generate_boolean_value(nesting_perc, get_complementary_value(nesting_perc)):
            try:
                num_nest = random.randrange(1, max_nest)
            except ValueError:
                num_nest = 1
            
            # Info of chosen group
            name = NODES[g]["properties"]["name"].split("@")[0]
            try:
                tier, dept, resource, resource_permission = name.split("_")
                tier = int(tier[1:])
            except:
                continue

            # Groups within the department
            department_groups = FOLDERS[tier][dept]

            # Condition check
            if num_nest > len(department_groups):
                num_nest = random.randrange(1, len(department_groups))

            # Sample groups to nest
            nesting_groups = random.sample(department_groups, num_nest)

            # Nest current group into sampled groups
            rel_type = "MemberOf"
            props = ["isacl"]
            values = [False]
            for to_nest_group in nesting_groups:
                if not to_nest_group == g:
                    start_index = g
                    end_index = get_node_index(to_nest_group + "_Group", "name")
                    edge_operation(start_index, end_index, rel_type, props, values)
