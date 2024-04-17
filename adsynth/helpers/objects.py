import math
import random
import uuid
from adsynth.DATABASE import edge_operation, get_node_index, node_operation, ridcount
from adsynth.adsynth_templates.admin_groups import get_t0_admin_groups, get_tn_admin_groups
from adsynth.entities.acls import cn, cs
from adsynth.helpers.distinguished_names import add_dn, get_dn_leaf_objects
from adsynth.utils.domains import get_domain_dn
from adsynth.utils.groups import generate_group_description
from adsynth.utils.ous import get_ou_dn
from adsynth.utils.principals import get_cn, get_sid_from_rid

def segregate_list(array, percentages):

    # Cummulative percentages
    cumulative_percentages = [sum(percentages[:i + 1]) / 100 for i in range(len(percentages))]


    # Convert percentages to indices
    indices = [0]
    indices.extend([math.ceil(percentage * len(array)) for percentage in cumulative_percentages])
    
    # Create subarrays
    result = [array[indices[i]:indices[i + 1]] for i in range(len(indices) - 1)]

    return result

def create_sub_objects(domain_name, domain_sid, parent_name, parent_type, sub_list, sub_type, rel_type, ous_dn = [], highvalue = False):
    # names at first do not have the suffix
    #        /--->B
    # A ----|---->C
    #        \--->D
    domain_dn = get_domain_dn(domain_name)
    for sub in sub_list:
        # Create a sub object
        if sub_type == "OU":
            sid = cs(str(uuid.uuid4()), domain_sid)
        else:
            sid = get_sid_from_rid(ridcount[0], domain_sid)
            ridcount[0] += 1
        sub_name = cn(sub, domain_name)
        keys = ["domain", "name", "objectid", "labels"]
        values = [domain_name, sub_name, sid, sub_type]
        id_lookup = sid
        
        if sub_type == "Group" or sub_type == "OU":
            keys.extend(["distinguishedname", "description", "highvalue"])
            if sub_type == "Group":
                keys.append("admincount")
                domain_dn = get_domain_dn(domain_name)
                dn = get_dn_leaf_objects(sub_name, ous_dn, domain_dn)
                values.extend([dn, generate_group_description(sub_name), highvalue, highvalue])
            else:
                keys.append("blocksInheritance")
                values.extend([get_ou_dn(sub_name, domain_dn), None, False, False])

        node_operation(sub_type, keys, values, id_lookup)

        # Parent --rel_type--> Sub
        if parent_name != domain_name:
            start_name = cn(parent_name, domain_name)
        else:
            start_name = parent_name
        start_index = get_node_index(f"{start_name}_{parent_type}", "name")
        end_index = get_node_index(f"{sub_name}_{sub_type}", "name")
        
        edge_operation(start_index, end_index, rel_type)
    
def add_sub_objects(domain_name, parent_name, parent_type, sub_list, sub_type, rel_type, is_cn, props = [], values = []):
    start_name = cn(parent_name, domain_name)
    for sub in sub_list:
        # Parent --rel_type--> Sub
        if is_cn:
            sub_name = sub
        else:
            sub_name = cn(sub, domain_name)
        start_index = get_node_index(f"{start_name}_{parent_type}", "name")
        end_index = get_node_index(f"{sub_name}_{sub_type}", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

def add_admin_tiers(domain_name, user_name, tier, is_service, server_operators, print_operators, ous_dn):
    # Accounts/Service accounts OU CONTAINS admins
    start_name = f"T{tier} Admin Service Accounts" if is_service \
                    else f"T{tier} Admin Accounts"
    start_index = get_node_index(cn(start_name , domain_name) + "_OU", "name")

    end_index = get_node_index(user_name + "_User", "name")
    rel_type = "Contains"
    edge_operation(start_index, end_index, rel_type)

    # Update distinguished name
    ous_dn.append(get_cn(start_name))
    add_dn(domain_name, user_name, "User", ous_dn)

    
    # Add to an admin group as a member
    # Groups in T0 requires members to be admin accounts
    # Other tiered groups accept admin accounts and service accounts
    # https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/securing-privileged-access-for-the-ad-admin-part-1/ba-p/259166
    if tier != 0 or not is_service:
        start_index = get_node_index(user_name + "_User", "name")
        
        if tier != 0:
            if is_service:
                group = "Service Accounts Group"
            else:
                group = random.choice(get_tn_admin_groups()[:-1])
            end_name = f"T{tier} {group}"
        else:
            end_name = random.choice(get_t0_admin_groups())
        end_index = get_node_index(cn(end_name, domain_name) + "_Group", "name")

        rel_type = "MemberOf"
        edge_operation(start_index, end_index, rel_type)
    
        if tier == 0:
            if end_index == get_node_index(cn("SERVER OPERATORS",domain_name) + "_Group", "name"):
                server_operators.append(user_name)
            elif end_index == get_node_index(cn("PRINT OPERATORS",domain_name) + "_Group", "name"):
                print_operators.append(user_name)
              