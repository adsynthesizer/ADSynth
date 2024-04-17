import random
import re
from adsynth.DATABASE import LOCAL_ADMINS, NODE_GROUPS, PAW_TIERS, S_TIERS_LOCATIONS, WS_TIERS_LOCATIONS, edge_operation, get_node_index
from adsynth.adsynth_templates.admin_groups import get_admin_groups
from adsynth.adsynth_templates.permissions import get_non_acls_list
from adsynth.entities.acls import cn
from adsynth.helpers.getters import get_locations, get_threshold_values, get_total_resources, get_ou_elements
from adsynth.helpers.metagraph_extractor import extract_hyperedges
from adsynth.helpers.objects import add_sub_objects
from adsynth.templates.acls import get_acls_list
from adsynth.utils.parameters import get_dict_param_value, get_perc_param_value


def create_control_management_permissions(domain_name, nTiers, is_acl, parameters, convert_to_digraph):
    # Set up parameters depending on ACL/Non-ACL
    permission_type = "nonACLs"
    permission_percentage_call = "nonACLsPercentage"
    permission_prob_call = "nonACLsProbability"
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [is_acl, False, "All"]
    if is_acl:
        if nTiers == 1:
            return
        permission_type = "ACLs"
        permission_percentage_call = "ACLPrincipalsPercentage"
        permission_prob_call = "ACLsProbability"
    
    permission_probs = get_dict_param_value(permission_type, permission_prob_call, parameters) 
    
    # An admin group can have control over objects at the same tier or below
    if is_acl:
        PERMISSIONS = get_acls_list(permission_probs)
    else:
        PERMISSIONS = get_non_acls_list(permission_probs)

    locations = get_locations(parameters)
    perc_target = get_perc_param_value(permission_type, permission_percentage_call, parameters)

    # Permission generation
    for i in range(nTiers):
        if is_acl:
            all_targets = get_total_resources(i, nTiers, locations, parameters, ["C", "U", "G"])
            group_targets = get_total_resources(i, nTiers, locations, parameters, ["G"])
        else:
            all_targets = get_total_resources(i, nTiers, locations, parameters)

        num_permissions = int(len(all_targets) * perc_target / 100)
        
        AG = get_admin_groups(i)
        if i == 0:
            AG = AG[:-1]

        for g in AG:
            start_index = get_node_index(cn(g, domain_name) + "_Group", "name")
            for j in range(num_permissions):
                rel_type = random.choice(PERMISSIONS)
                try:
                    if rel_type == "AddMember" or rel_type == "AddSelf":
                        target = random.choice(group_targets)
                    else:
                        target = random.choice(all_targets)
                except:
                    continue
                end_index = get_node_index(f"{cn(target, domain_name)}_OU", "name")
                edge_operation(start_index, end_index, rel_type, props, values)
                if convert_to_digraph:
                    ou_elements, type = get_ou_elements(target)
                    if len(ou_elements) == 0:
                        continue
                        
                    extract_hyperedges(cn(g, domain_name), "Group", ou_elements, type, rel_type)

def assign_administration_to_admin_principals(domain_name, nTiers, convert_to_digraph = 0):
    rel_type = "AdminTo"
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [False, False, "All"]
    
    DA = cn("DOMAIN ADMINS", domain_name)
    start_index = get_node_index(DA + "_Group", "name")
    end_index = get_node_index(cn("DOMAIN COMPUTERS", domain_name) + "_Group", "name")
    edge_operation(start_index, end_index, rel_type, props, values)
    
    # DOMAIN ADMINS --AdminTo--> All computers
    lowest_tier_no_admin = min(2, nTiers - 1)

    # PAWs
    sub_list = [f"T{i} Admin Devices" for i in range(nTiers)]
    
    # Servers
    if nTiers > 2:
        sub_list.append("Tier 1 Servers")
    sub_list.extend([f"T{i} Servers" for i in range(lowest_tier_no_admin, nTiers)])
    
    # Workstations
    sub_list.extend([f"T{i} Workstations" for i in range(lowest_tier_no_admin, nTiers)])
    
    add_sub_objects(domain_name, "DOMAIN ADMINS", "Group", sub_list, "OU", rel_type, False, props, values)

    # Extract hyperedges
    props = ["isacl", "isInherited"]
    values = [False, False]
    if convert_to_digraph:
        extract_hyperedges(DA, "Group", NODE_GROUPS["Computer"], "Computer", rel_type, props, values)
    

    
    # Tn Admin Groups --AdminTo--> PAWs at the tier (Tn Admin Devices)
    for i in range(1, nTiers):
        AG = cn(f"T{i} Admin Accounts Group", domain_name)
        AD = cn(f"T{i} Admin Devices", domain_name)
        start_index = get_node_index(AG + "_Group", "name")
        end_index = get_node_index(AD + "_OU", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

        if convert_to_digraph:
            extract_hyperedges(AG, "Group", PAW_TIERS[i], "Computer", rel_type, props, values)

def assign_local_admin_rights(domain_name, nTiers, parameters, convert_to_digraph):
    rel_type = "AdminTo"
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [False, False, "All"]
    locations = get_locations(parameters)

    # Extract tier and location of a computer
    pattern_ws = r'T(\d+) Workstations (\w+)'
    pattern_s = r'T(\d+) Server (\w+)'

    def extract_tier_location(ou_name, pattern_ws, pattern_s):
        # Match against Workstations
        match = re.match(pattern_ws, ou_name)
        is_ou_ws = True # Check whether Workstations or Servers
        if not match:
            match = re.match(pattern_s, ou_name)
            is_ou_ws = False
            
        tier = int(match.group(1))
        location = match.group(2)

        return is_ou_ws, tier, location
        

    lowest_tier_not_admin = min(2, nTiers - 1)
    for i in range(lowest_tier_not_admin, nTiers):
        for g in LOCAL_ADMINS[i]:
            thresholds_to_admin = get_threshold_values("Group", "nOUsPerLocalAdmins", parameters)
            num_local_admins = random.randint(thresholds_to_admin[0], thresholds_to_admin[1])
            num_local_admins = min(num_local_admins, len(locations))
            targets = [f"T{i} Workstations {l}" for l in locations]
            targets.extend(f"T{i} Servers {l}" for l in locations)
            sub_list = random.sample(targets, num_local_admins)

            add_sub_objects(domain_name, g, "Group", sub_list, "OU", rel_type, False, props, values)

            if convert_to_digraph:
                props_digraph = ["isacl", "isInherited"]
                values_digraph = [False, False]
                for ou in targets:
                    try:
                        is_ou_ws, tier, location = extract_tier_location(ou, pattern_ws, pattern_s)
                        if is_ou_ws:
                            extract_hyperedges(cn(g, domain_name), "Group", WS_TIERS_LOCATIONS[tier][location], "Computer", rel_type, props_digraph, values_digraph)
                        else:
                            extract_hyperedges(cn(g, domain_name), "Group", S_TIERS_LOCATIONS[tier][location], "Computer", rel_type, props_digraph, values_digraph)
                    except:
                        continue
 