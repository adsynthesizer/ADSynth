from adsynth.entities.acls import cn, get_dc_ou_isinherited_value, get_default_group_aces_list, get_default_user_aces_list
from adsynth.entities.groups import get_group_member_id
from adsynth.helpers.metagraph_extractor import extract_hyperedges
from adsynth.helpers.objects import add_sub_objects
from adsynth.templates.groups import DEPARTMENTS, STANDARD_GROUPS, get_departments, get_departments_list
from adsynth.utils.parameters import get_dict_param_value
from adsynth.DATABASE import ADMIN_USERS, DISABLED_USERS, DISTRIBUTION_GROUPS, ENABLED_USERS, LOCAL_ADMINS, NODE_GROUPS, NODES, FOLDERS, SECURITY_GROUPS, edge_operation, get_node_index

# Idea Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-b--privileged-accounts-and-groups-in-active-directory
def create_default_groups_acls(domain_name, domain_sid):
    standard_group_aces_list = get_default_group_aces_list(domain_name, domain_sid)
    for ace in standard_group_aces_list:
        grant_permissions(ace)
 
# Idea Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts
def create_default_users_acls(domain_name, domain_sid):
    standard_user_aces_list = get_default_user_aces_list(domain_name, domain_sid)
    for ace in standard_user_aces_list:
        grant_permissions(ace)
 
 
def grant_permissions(ad_object):
    start_index = get_node_index(ad_object["IdentityReferenceId"], "objectid")
    end_index = get_node_index(ad_object["ObjectId"], "objectid")
    rel_type = ad_object["Right"]
    keys = ["isacl", "isinherited"]
    values = [True, ad_object["IsInherited"]]
    edge_operation(start_index, end_index, rel_type, keys, values)


# Idea Ref: ADSimulator
def create_default_AllExtendedRights(domain_name, nTiers, convert_to_digraph = 0):
    rel_type = "AllExtendedRights"

    # Target DOMAIN
    props = ["isacl", "isInherited"]
    values = [True, False]
    for g in ["DOMAIN ADMINS", "ADMINISTRATORS"]:
        start_index = get_node_index(cn(g, domain_name) + "_Group", "name")
        end_index = get_node_index(domain_name + "_Domain", "name")
        edge_operation(start_index, end_index, rel_type, props, values)
    
    # Target Admin Accounts in Tier 0
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [True, False, "All"]
    for g in ["ENTERPRISE ADMINS", "DOMAIN ADMINS", "ADMINISTRATORS"]:
        start_index = get_node_index(cn(g, domain_name) + "_Group", "name")
        
        end_index = get_node_index(cn("T0 Admin Accounts", domain_name) + "_OU", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

        end_index = get_node_index(cn("T0 Admin Service Accounts", domain_name) + "_OU", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

        # Extract hyperedges
        if convert_to_digraph:
            props_hyperedge = ["isacl", "isInherited"]
            values_hyperedge = [True, False]
            extract_hyperedges(cn(g, domain_name), "Group", ADMIN_USERS[0], "User", rel_type, props_hyperedge, values_hyperedge)


    # Target other users
    ## Tier Admin Accounts > 0
    lowest_tier_no_admin = min(2, nTiers - 1)
    values = [True, True, "All"]
    add_default_acls(domain_name, "ADMINISTRATORS", rel_type, props, values, nTiers, 1, "Admin Accounts")
    add_default_acls(domain_name, "ADMINISTRATORS", rel_type, props, values, nTiers, 1, "Admin Service Accounts")

    # Extract hyperedges
    if convert_to_digraph:
        props_hyperedge = ["isacl", "isInherited"]
        values_hyperedge = [True, False]
        for i in range(1, nTiers):
            extract_hyperedges(cn("ADMINISTRATORS", domain_name), "Group", ADMIN_USERS[i], "User", rel_type, props_hyperedge, values_hyperedge)

    ## Normal users
    add_default_acls(domain_name, "ADMINISTRATORS", rel_type, props, values, nTiers, lowest_tier_no_admin, "User Accounts")
    # Extract hyperedges
    if convert_to_digraph:
        props_hyperedge = ["isacl", "isInherited"]
        values_hyperedge = [True, False]
        for i in range(lowest_tier_no_admin, nTiers):
            extract_hyperedges(cn("ADMINISTRATORS", domain_name), "Group", ENABLED_USERS[i], "User", rel_type, props_hyperedge, values_hyperedge)
            extract_hyperedges(cn("ADMINISTRATORS", domain_name), "Group", DISABLED_USERS[i], "User", rel_type, props_hyperedge, values_hyperedge)


# Leaf nodes includes all users (admin & non-admin), computers (PAWs, Servers & WS) and non-admin groups
def create_control_over_leaf_objects(domain_name, rel_type, identity_name, nTiers, parameters, convert_to_digraph = 0):
    # Starting node
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [True, False, "All"]
    start_index = get_node_index(cn(identity_name, domain_name) + "_Group", "name")
    
    # Target Admin users in Tier 0
    end_index = get_node_index(cn("T0 Admin Accounts", domain_name) + "_OU", "name")
    edge_operation(start_index, end_index, rel_type, props, values)

    end_index = get_node_index(cn("T0 Admin Service Accounts", domain_name) + "_OU", "name")
    edge_operation(start_index, end_index, rel_type, props, values)

    if convert_to_digraph:
        props_hyperedge = props[:2]
        values_hyperedge = values[:2]
        extract_hyperedges(cn(identity_name, domain_name), "Group", ADMIN_USERS[0], "User", rel_type, props_hyperedge, values_hyperedge)

    
    # Target all objects - Workstations, Servers, T1 Servers and PAWs, groups, etc.
    values = [True, True, "All"]
    create_control_over_leaf_objects_not_t0_users(domain_name, rel_type, identity_name, nTiers, props, values, parameters, convert_to_digraph)
    

def create_control_over_leaf_objects_not_t0_users(domain_name, rel_type, identity_name, nTiers, props, values, parameters, convert_to_digraph = 0):
    start_index = get_node_index(cn(identity_name, domain_name) + "_Group", "name")
    props_hyperedge = props[:2]
    values_hyperedge = values[:2]

    # PAWs
    add_default_acls(domain_name, identity_name, rel_type, props, values, nTiers, 0, "Admin Devices")


    # Tier 1 servers
    if nTiers > 2:
        end_index = get_node_index(cn("Tier 1 Servers", domain_name) + "_OU", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

    # Workstations & Servers T >= 2
    lowest_tier_no_admin = min(2, nTiers - 1)
    add_default_acls(domain_name, identity_name, rel_type, props, values, nTiers, lowest_tier_no_admin, "Servers")
    add_default_acls(domain_name, identity_name, rel_type, props, values, nTiers, lowest_tier_no_admin, "Workstations")

    # Target non-admin groups
    add_default_acls(domain_name, identity_name, rel_type, props, values, nTiers, lowest_tier_no_admin, "Groups")


    # Target admin users, excluding users in DA / Tier 0
    add_default_acls(domain_name, identity_name, rel_type, props, values, nTiers, 1, "Admin Accounts")
    add_default_acls(domain_name, identity_name, rel_type, props, values, nTiers, 1, "Admin Service Accounts")


    # Target normal users
    add_default_acls(domain_name, identity_name, rel_type, props, values, nTiers, lowest_tier_no_admin, "User Accounts")

    # Extract hyperedges
    if convert_to_digraph:
        props_hyperedge = props[:2]
        values_hyperedge = values[:2]

        # All computers
        extract_hyperedges(cn(identity_name, domain_name), "Group", NODE_GROUPS["Computer"], "Computer", rel_type, props_hyperedge, values_hyperedge)

        # All non-admin groups and normal users
        for i in range(lowest_tier_no_admin, nTiers):
            # Normal users
            extract_hyperedges(cn(identity_name, domain_name), "Group", ENABLED_USERS[i], "User", rel_type, props_hyperedge, values_hyperedge)
            extract_hyperedges(cn(identity_name, domain_name), "Group", DISABLED_USERS[i], "User", rel_type, props_hyperedge, values_hyperedge)

            departments_probs = get_dict_param_value("Group", "departmentProbability", parameters)
            departments_list = get_departments(departments_probs)
            for d in departments_list:
                # Security groups
                extract_hyperedges(cn(identity_name, domain_name), "Group", FOLDERS[i][d], "Group", rel_type, props_hyperedge, values_hyperedge)

                # Distribution groups
                extract_hyperedges(cn(identity_name, domain_name), "Group", DISTRIBUTION_GROUPS[i][d], "Group", rel_type, props_hyperedge, values_hyperedge)
            
            # Process names for Local Admin groups
            local_admins = [cn(group, domain_name) for group in LOCAL_ADMINS[i]]
            extract_hyperedges(cn(identity_name, domain_name), "Group", local_admins, "Group", rel_type, props_hyperedge, values_hyperedge)


# Idea Ref: ADSimulator
def create_default_GenericWrite(domain_name, nTiers, parameters, convert_to_digraph = 0):
    rel_type = "GenericWrite"
    identity_name = "ADMINISTRATORS"
    create_control_over_leaf_objects(domain_name, rel_type, identity_name, nTiers, parameters, convert_to_digraph)

    # DOMAIN ADMINS & ENTERPRISE ADMINS
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [True, False, "All"]
    end_index = get_node_index(cn("Group Policy Objects Container", domain_name) + "_Container", "name")
    for g in ["DOMAIN ADMINS", "ENTERPRISE ADMINS"]:
        start_index = get_node_index(cn(g, domain_name) + "_Group", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

        # Extract hyperedges
        if convert_to_digraph:
            props_hyperedge = ["isacl", "isInherited"]
            values_hyperedge = [True, False]
            extract_hyperedges(cn(g, domain_name), "Group", NODE_GROUPS["GPO"], "GPO", rel_type, props_hyperedge, values_hyperedge)


# Idea Ref: ADSimulator
def create_default_owns(domain_name, convert_to_digraph = 0):
    rel_type = "Owns"
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [True, False, "All"]

    start_index = get_node_index(cn("DOMAIN ADMINS", domain_name) + "_Group", "name")
    end_index = get_node_index(domain_name + "_Domain", "name")
    edge_operation(start_index, end_index, rel_type, props, values)

    # DOMAIN ADMINS --Owns--> All GPOs
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [True, False, "All"]
    start_index = get_node_index(cn("DOMAIN ADMINS", domain_name) + "_Group", "name")
    end_index = get_node_index(cn("Group Policy Objects Container", domain_name) + "_Container", "name")
    edge_operation(start_index, end_index, rel_type, props, values)

    # Extract hyperedges
    if convert_to_digraph:
        props_hyperedge = ["isacl", "isInherited"]
        values_hyperedge = [True, False]
        extract_hyperedges(cn("DOMAIN ADMINS", domain_name), "Group", NODE_GROUPS["GPO"], "GPO", rel_type, props_hyperedge, values_hyperedge)


# Idea Ref: ADSimulator
def create_default_write_dacl_owner(domain_name, nTiers, parameters, convert_to_digraph = 0):
    acl_types = ["WriteDacl", "WriteOwner"]
    for rel_type in acl_types:
        # ADMINISTRATORS
        create_control_over_leaf_objects(domain_name, rel_type, "ADMINISTRATORS", nTiers, parameters, convert_to_digraph) # O(tier)

        # DOMAIN ADMINS & ENTERPRISE ADMINS
        # Refer to GenericWrite
        props = ["isacl", "isInherited", "inheritanceType"]
        values = [True, False, "All"]
        end_index = get_node_index(cn("Group Policy Objects Container", domain_name) + "_Container", "name")
        for g in ["DOMAIN ADMINS", "ENTERPRISE ADMINS"]:
            start_index = get_node_index(cn(g, domain_name) + "_Group", "name")
            edge_operation(start_index, end_index, rel_type, props, values)

            # Extract hyperedges
            if convert_to_digraph:
                props_hyperedge = ["isacl", "isInherited"]
                values_hyperedge = [True, False]
                extract_hyperedges(cn(g, domain_name), "Group", NODE_GROUPS["GPO"], "GPO", rel_type, props_hyperedge, values_hyperedge)

        # Permissions over KRBTGT users
        end_index = get_node_index(cn("KRBTGT", domain_name) + "_User", "name")
        props = ["isacl", "isInherited"]
        values = [True, False]

        for g in ["DOMAIN ADMINS", "ENTERPRISE ADMINS"]:
            start_index = get_node_index(cn(g, domain_name) + "_Group", "name")
            edge_operation(start_index, end_index, rel_type, props, values)
                

        # ACLs over DC OU
        for g in ["DOMAIN ADMINS", "ADMINISTRATORS"]:
            start_index = get_node_index(cn(g, domain_name) + "_Group", "name")
            end_index = get_node_index(cn("DOMAIN CONTROLLERS", domain_name) + "_OU", "name")
            
            # Retrieve sid of the group
            group_sid = NODES[start_index]["properties"]["objectid"]
            isInherited = get_dc_ou_isinherited_value(group_sid, domain_name)

            props = ["isacl", "isInherited"]
            values = [True, isInherited]
            for rel_type in acl_types:
                edge_operation(start_index, end_index, rel_type, props, values)


# Idea Ref: ADSimulator
def create_default_GenericAll(domain_name, nTiers, parameters, convert_to_digraph):
    rel_type = "GenericAll"
    props = ["isacl", "isInherited", "inheritanceType"]
    values = [True, True, "All"]
    
    for g in ["ACCOUNT OPERATORS", "ENTERPRISE ADMINS", "DOMAIN ADMINS"]:
        if g == "ENTERPRISE ADMINS":
            values[1] = True
        else:
            values[1] = False

        create_control_over_leaf_objects_not_t0_users(domain_name, rel_type, g, nTiers, props, values, parameters, convert_to_digraph)
    
    # Ent Admins --> DCOU
    values = [True, True, "All"]
    start_index = get_node_index(cn("ENTERPRISE ADMINS", domain_name) + "_Group", "name")
    end_index = get_node_index(cn("DOMAIN CONTROLLERS", domain_name) + "_OU", "name")
    edge_operation(start_index, end_index, rel_type, props, values)

    # Ent Admins + DA --> OUs
    sub_list = ["Admin", "Tier 1 Servers"]
    
    if nTiers == 1:
        sub_list[1] = 'Tier 0'
    elif nTiers == 2:
        sub_list[1] = 'Tier 1'

    sub_list.extend([f"Tier {i}" for i in range(2, nTiers)])

    for g in ["ENTERPRISE ADMINS", "DOMAIN ADMINS"]:
        if g == "ENTERPRISE ADMINS":
            values[1] = True
        else:
            values[1] = False
        
        add_sub_objects(domain_name, g, "Group", sub_list, "OU", rel_type, False, props, values)
    

    # DA + Acc Operators --> DC Comps
    values = [True, False, "All"]
    for g in ["ACCOUNT OPERATORS", "DOMAIN ADMINS"]:
        start_index = get_node_index(cn(g, domain_name) + "_Group", "name")
        end_index = get_node_index(cn("DOMAIN CONTROLLERS", domain_name) + "_OU", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

 
def add_default_acls(domain_name, start_name, acl_type, props, values, nTiers, lowest_tier, target_suffix):
    start_index = get_node_index(cn(start_name, domain_name) + "_Group", "name")

    for t in range(lowest_tier, nTiers):
        ou_name = f"T{t} {target_suffix}"
        ou_index = get_node_index(cn(ou_name, domain_name) + "_OU", "name")
        edge_operation(start_index, ou_index, acl_type, props, values)


def add_default_acls_gpos(domain_name, start_name, acl_type, props, values):
    start_index = get_node_index(cn(start_name, domain_name) + "_Group", "name")
    for t in NODE_GROUPS["GPO"]:
        edge_operation(start_index, t, acl_type, props, values)

# Idea Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
def create_enterprise_admins_acls(domain_name):
    # Ent Admins
    group_name = "ENTERPRISE ADMINS@{}".format(domain_name)
    start_index = get_node_index(group_name + "_Group", "name")

    # Ent Admins --GenericAll---> Domain
    end_index = get_node_index(domain_name + "_Domain", "name")
    rel_type = "GenericAll"
    props = ["isacl", "isinherited"]
    values = [True, False]
    edge_operation(start_index, end_index, rel_type, props, values)
    
    # Ent Admins --MemberOf--> Adminstrators
    end_index = get_node_index(cn("ADMINISTRATORS",domain_name) + "_Group", "name")
    rel_type = "MemberOf"
    edge_operation(start_index, end_index, rel_type)


    # Ent Admins -> High Value Targets in STANDARD GROUPS
    props = ["isacl"]
    values = [True]

    rel_type = "GenericWrite"
    targets = ["BACKUP OPERATORS", "PRINT OPERATORS", "SERVER OPERATORS", "DOMAIN ADMINS", "DOMAIN CONTROLLERS"]

    for group in targets:
        group_highvalue = cn(group,domain_name)
        end_index = get_node_index(group_highvalue + "_Group", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

    rel_type = "WriteDacl"
    targets = ["ADMINISTRATORS", "DOMAIN ADMINS", "ACCOUNT OPERATORS", "GROUP POLICY CREATOR OWNERS"]

    for group in targets:
        group_highvalue = cn(group,domain_name)
        end_index = get_node_index(group_highvalue + "_Group", "name")
        edge_operation(start_index, end_index, rel_type, props, values)
 
# Idea Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
def create_administrators_acls(domain_name):
    # Administrators -> Domain Node
    group_name = "ADMINISTRATORS@{}".format(domain_name)
    start_index = get_node_index(group_name + "_Group", "name")
    end_index = get_node_index(domain_name + "_Domain", "name")
    relationships = ["Owns", "WriteOwner", "WriteDacl", "GetChanges", "GetChangesAll"]
    props = ["isacl", "isinherited"]
    values = [True, False]
 
    # Administrators -> DCSync Rights
    for rel_type in relationships:
        edge_operation(start_index, end_index, rel_type, props, values)
    
    # Administrators -> High Value Targets in STANDARD GROUPS
    props = ["isacl"]
    values = [True]

    # --GenericWrite--> 
    rel_type = "GenericWrite"
    targets = ["DOMAIN CONTROLLERS", "SERVER OPERATORS", "BACKUP OPERATORS", "PRINT OPERATORS"]

    for group in targets:
        group_highvalue = cn(group,domain_name)
        end_index = get_node_index(group_highvalue + "_Group", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

    # --WriteDacl--> 
    rel_type = "WriteDacl"
    targets = ["ENTERPRISE ADMINS", "DOMAIN ADMINS", "ACCOUNT OPERATORS", "GROUP POLICY CREATOR OWNERS"]

    for group in targets:
        group_highvalue = cn(group,domain_name)
        end_index = get_node_index(group_highvalue + "_Group", "name")
        edge_operation(start_index, end_index, rel_type, props, values)
 
# Idea Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
def create_domain_admins_acls(domain_name):
    # Domain Admins -> Domain Node
    group_name = "DOMAIN ADMINS@{}".format(domain_name)
    start_index = get_node_index(group_name + "_Group", "name")
    end_index = get_node_index(domain_name + "_Domain", "name")
    relationships = ["WriteOwner", "WriteDacl", "AllExtendedRights"]
    props = ["isacl", "isinherited"]
    values = [True, False]
 
    for rel_type in relationships:
        if rel_type == "AllExtendedRights":
            edge_operation(start_index, end_index, rel_type, ["isacl"], [True])
        else:
            edge_operation(start_index, end_index, rel_type, props, values)
    

    # Domain Admins -> High Value Targets
    props = ["isacl"]
    values = [True]

    # --Owns-->
    rel_type = "Owns"
    targets = ["ADMINISTRATORS", "ACCOUNT OPERATORS", "ENTERPRISE ADMINS"]

    for group in targets:
        group_highvalue = cn(group,domain_name)
        end_index = get_node_index(group_highvalue + "_Group", "name")
        edge_operation(start_index, end_index, rel_type, props, values)

    # --GenericWrite-->
    rel_type = "GenericWrite"
    targets = ["PRINT OPERATORS", "BACKUP OPERATORS", "SERVER OPERATORS", "DOMAIN CONTROLLERS"]

    for group in targets:
        group_highvalue = cn(group,domain_name)
        end_index = get_node_index(group_highvalue + "_Group", "name")
        edge_operation(start_index, end_index, rel_type, props, values)


# Idea Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups 
def create_default_dc_groups_acls(domain_name):
    end_index = get_node_index(domain_name + "_Domain", "name")

    props = ["isacl", "isinherited"]
    values = [True, False]

    # DC Groups -> Domain Node
    group_name = "ENTERPRISE DOMAIN CONTROLLERS@{}".format(domain_name)
    start_index = get_node_index(group_name + "_Group", "name")
    rel_type = "GetChanges"
    edge_operation(start_index, end_index, rel_type, props, values)

    group_name = "ENTERPRISE READ-ONLY DOMAIN CONTROLLERS@{}".format(domain_name)
    start_index = get_node_index(group_name + "_Group", "name")
    rel_type = "GetChanges"
    edge_operation(start_index, end_index, rel_type, props, values)
    
    group_name = "DOMAIN CONTROLLERS@{}".format(domain_name)
    start_index = get_node_index(group_name + "_Group", "name")
    rel_type = "GetChangesAll"
    edge_operation(start_index, end_index, rel_type, props, values)


def create_account_operators_acls(domain_name, domain_sid):
    adg_name= cn("ADMINISTRATORS", domain_name)
    adg_index = get_node_index(adg_name + "_Group", "name")

    # Find members of ADMINISTRATORS group
    adg_members = STANDARD_GROUPS[0]["Members"]
    adg_members_indices = []
    for group in adg_members:
        if group["MemberType"] == "Group":
            objectid = get_group_member_id(group["MemberId"], domain_name, domain_sid)
            print(objectid)
            index = get_node_index(objectid, "objectid")
            adg_members_indices.append(index)

    # ACCOUNT OPERATORS' permissions
    start_index = get_node_index(cn("ACCOUNT OPERATORS", domain_name) + "_Group", "name")
    for g in NODE_GROUPS["Group"]:
        # Account Operators group has GenericAll on all users, computers 
        # and groups (excluding ADMINISTRATORS and its members)
        if g != adg_index and g not in adg_members_indices:
            edge_operation(start_index, g, "GenericAll")
        
        # Todo: All users + computers, considering DC
  