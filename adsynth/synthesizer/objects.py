import random
from adsynth.adsynth_templates.admin_groups import get_t0_admin_groups, get_tn_admin_groups
from adsynth.adsynth_templates.tier_0_assets import get_t0_default_groups
from adsynth.entities.acls import cn
from adsynth.helpers.distinguished_names import set_computer_dn
from adsynth.helpers.getters import get_locations, get_threshold_values
from adsynth.helpers.objects import add_sub_objects, create_sub_objects
from adsynth.templates.computers import get_client_os_list, get_computer_type_list, get_main_dc_os, get_server_os_list
from adsynth.templates.groups import get_departments
from adsynth.utils.computers import generate_client_service_pricipal_names, generate_server_service_pricipal_names, get_computer_name, is_os_vulnerable
from adsynth.helpers.debug import log
from adsynth.utils.domains import get_domain_dn
from adsynth.utils.gpos import get_gpos_container_dn
from adsynth.utils.ous import get_ou_dn
from adsynth.utils.principals import get_cn, get_sid_from_rid
from adsynth.utils.time import generate_timestamp
from adsynth.utils.users import get_user_timestamp, generate_sid_history
from adsynth.utils.boolean import generate_boolean_value
from adsynth.utils.parameters import get_dict_param_value, get_perc_param_value, print_computer_generation_parameters, print_dc_generation_parameters, print_user_generation_parameters
from adsynth.entities.users import get_guest_user, get_default_account, get_administrator_user, get_krbtgt_user,\
    get_forest_user_sid_list
from adsynth.adsynth_templates.default_config import get_complementary_value
from adsynth.DATABASE import ADMIN_USERS, COMPUTERS, DISABLED_USERS, DISTRIBUTION_GROUPS, ENABLED_USERS, FOLDERS, KERBEROASTABLES, LOCAL_ADMINS, SECURITY_GROUPS, node_operation, edge_operation, get_node_index, ridcount


def create_admin_groups(domain_name, domain_sid, nTiers):
    # Tier 0 Admin groups
    # There are multiple groups, but we only simulate the working of "PRINT OPERATORS", "ACCOUNT OPERATORS", "SERVER OPERATORS", "DOMAIN ADMINS"
    # For the remaining groups, we still include as Tier 0 assets
    sub_list = get_t0_default_groups()
    parent_name = f"T0 Admin Groups"
    add_sub_objects(domain_name, parent_name, "OU", sub_list, "Group", "Contains", False)


    # Other Tier Admin groups
    admin_groups = get_tn_admin_groups()
    for i in range(1, nTiers):
        sub_list = [f"T{i} {group}" for group in admin_groups]
        parent_name = f"T{i} Admin Groups"
        create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "Group", "Contains", highvalue = True)     

# Idea Ref: ADSimulator, DBCreator
def generate_users(domain_name, domain_sid, num_nodes, current_time, first_names, last_names, parameters):
    users = list()
    disabled_users = list()

    group_name = "DOMAIN USERS@{}".format(domain_name)
    enabled_perc = get_perc_param_value("User", "enabled", parameters)
    dontreqpreauth_perc = get_perc_param_value(
        "User", "dontreqpreauth", parameters) # CH
    hasspn_perc = get_perc_param_value("User", "hasspn", parameters)
    passwordnotreqd_perc = get_perc_param_value(
        "User", "passwordnotreqd", parameters)
    pwdneverexpires_perc = get_perc_param_value(
        "User", "pwdneverexpires", parameters)
    unconstraineddelegation_perc = get_perc_param_value(
        "User", "unconstraineddelegation", parameters)
    sidhistory_perc = get_perc_param_value("User", "sidhistory", parameters)

    # New properties
    savedcredentials_perc = get_perc_param_value(
        "User", "savedcredentials", parameters)

    print_user_generation_parameters(enabled_perc, dontreqpreauth_perc, hasspn_perc,
                                     passwordnotreqd_perc, pwdneverexpires_perc, unconstraineddelegation_perc, sidhistory_perc)

    for i in range(1, num_nodes + 1):
        first = random.choice(first_names)
        last = random.choice(last_names)
        user_name = "{}{}{:05d}@{}".format(first[0],
                                           last, i, domain_name).upper()
        user_name = user_name.format(first[0], last, i).upper()

        dispname = "{} {}".format(first, last)
        enabled = generate_boolean_value(
            enabled_perc, get_complementary_value(enabled_perc))

        if enabled:
            users.append(user_name)
        else:
            disabled_users.append(user_name)

        dontreqpreauth = generate_boolean_value(
            dontreqpreauth_perc, get_complementary_value(dontreqpreauth_perc))
        hasspn = generate_boolean_value(
            hasspn_perc, get_complementary_value(hasspn_perc))
        passwordnotreqd = generate_boolean_value(
            passwordnotreqd_perc, get_complementary_value(passwordnotreqd_perc))
        pwdneverexpires = generate_boolean_value(
            pwdneverexpires_perc, get_complementary_value(pwdneverexpires_perc))
        unconstraineddelegation = generate_boolean_value(
            unconstraineddelegation_perc, get_complementary_value(unconstraineddelegation_perc))
        sidhistory = generate_sid_history(
            sidhistory_perc, get_complementary_value(sidhistory_perc))
        pwdlastset = get_user_timestamp(current_time, enabled)
        lastlogon = get_user_timestamp(current_time, enabled)
        objectsid = get_sid_from_rid(ridcount[0], domain_sid)

        # New properties
        savedcredentials = generate_boolean_value(
            savedcredentials_perc, get_complementary_value(savedcredentials_perc))

        ridcount[0] += 1
        keys = ["domain", "objectid", "labels", "displayname", "name", "enabled", "pwdlastset", "lastlogon", "lastlogontimestamp",
                  "highvalue", "dontreqpreauth", "hasspn", "passwordnotreqd", "pwdneverexpires", "sensitive", "serviceprincipalnames",
                  "sidhistory", "unconstraineddelegation", "description", "admincount", "savedcredentials"]
        values = [domain_name, objectsid, "User", dispname, user_name, enabled, pwdlastset, lastlogon, lastlogon, False, dontreqpreauth, 
                  hasspn, passwordnotreqd, pwdneverexpires, False, "", sidhistory, unconstraineddelegation, "null", False, savedcredentials]
        id_lookup = objectsid
        node_operation("User", keys, values, id_lookup)

        # All users are MemberOf Domain Users
        start_index = get_node_index(objectsid, "objectid")
        end_index = get_node_index(group_name + "_Group", "name")
        rel_type = "MemberOf"
        edge_operation(start_index, end_index, rel_type)
        
    return users, disabled_users

# Ref: ADSimulator, DBCreator, BadBlood
#      Microsoft, https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-devices
def generate_computers(domain_name, domain_sid, num_nodes, computers, current_time, parameters):
    group_name = "DOMAIN COMPUTERS@{}".format(domain_name)
    props = []
    enabled_perc = get_perc_param_value("Computer", "enabled", parameters)
    has_laps_perc = get_perc_param_value("Computer", "haslaps", parameters)
    unconstrained_delegation_perc = get_perc_param_value("Computer", "unconstraineddelegation", parameters)
    os_perc = get_dict_param_value("Computer", "osProbability", parameters)
    os_list = get_client_os_list(os_perc)
 
    # New params
    privesc_perc = get_perc_param_value("Computer", "privesc", parameters)
    creddump_perc = get_perc_param_value("Computer", "creddump", parameters)
    exploitable_perc = get_perc_param_value("Computer", "exploitable", parameters)

    
 
    # PC List
    computer_type_perc = get_dict_param_value("Computer", "computerProbability", parameters)
    PC_list = get_computer_type_list(computer_type_perc) 
    # print(PC_list)   

    PAW = []
    Server = []
    Workstation =[]

    if num_nodes < 1:
        print("No computers are generated!")
        return computers, PAW, Server, Workstation
 
    print_computer_generation_parameters(enabled_perc, has_laps_perc, unconstrained_delegation_perc, os_perc)
    for i in range(1, num_nodes + 1):
        PC_type = random.choice(PC_list)
        highvalue = False
        if PC_type == 'PAW':
            comp_name = str('PAW')+"-{:05d}@{}".format(len(PAW), domain_name)
            highvalue = True
            PAW.append(comp_name)
        elif PC_type == 'Server':
            comp_name = str('S')+"-{:05d}@{}".format(len(Server), domain_name)
            highvalue = True
            Server.append(comp_name)
        else:
            comp_name = str('WS')+"-{:05d}@{}".format(len(Workstation), domain_name)
            Workstation.append(comp_name)
        
        COMPUTERS.append(comp_name)
        computers.append(comp_name)
        os = random.choice(os_list)
        enabled = generate_boolean_value(enabled_perc, get_complementary_value(enabled_perc))
        has_laps = generate_boolean_value(has_laps_perc, get_complementary_value(has_laps_perc))
        unconstrained_delegation = generate_boolean_value(unconstrained_delegation_perc, get_complementary_value(unconstrained_delegation_perc))
 
        # New params
        privesc = generate_boolean_value(privesc_perc, get_complementary_value(privesc_perc))
        creddump = generate_boolean_value(creddump_perc, get_complementary_value(creddump_perc))
        if is_os_vulnerable(os):
            exploitable = generate_boolean_value(exploitable_perc, get_complementary_value(exploitable_perc))
        else:
            exploitable = False

        computer_property = {
            'id': get_sid_from_rid(ridcount[0], domain_sid),
            'props': {
                'name': comp_name,
                'operatingsystem': os,
                'enabled': enabled,
                'haslaps': has_laps,
                'highvalue': highvalue,
                'lastlogontimestamp': generate_timestamp(current_time),
                'pwdlastset': generate_timestamp(current_time),
                'serviceprincipalnames': generate_client_service_pricipal_names(comp_name),
                'unconstraineddelegation': unconstrained_delegation,
                'privesc': privesc,
                'creddump': creddump,
                'exploitable': exploitable
            }
        }

        ridcount[0] += 1

        # Create a Computer
        keys = [i for i in computer_property['props']]
        keys.extend(['domain', 'labels', 'objectid'])

        values = [computer_property['props'][i] for i in computer_property['props']]
        values.extend([domain_name, "Computer", computer_property['id']])

        id_lookup = computer_property['id']
        node_operation("Computer", keys, values, id_lookup)

        # Regualar computer / Workstations --MemberOf--> Domain Computers Group
        if PC_type == "Workstation":
            start_index = get_node_index(id_lookup, "objectid")
            end_index = get_node_index(group_name + "_Group", "name")
            rel_type = "MemberOf"
            props = ["isacl"]
            values = [False]
            edge_operation(start_index, end_index, rel_type, props, values)

    return computers, PAW, Server, Workstation

# Ref: ADSimulator, DBCreator and Microsoft, https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-authsod/c4012a57-16a9-42eb-8f64-aa9e04698dca
def generate_dcs(domain_name, domain_sid, domain_dn, dcou, current_time, parameters, functional_level):
    dc_properties_list = []
    ou_dn = get_ou_dn("Domain Controllers", domain_dn)
    enabled_perc = get_perc_param_value("DC", "enabled", parameters)
    has_laps_perc = get_perc_param_value("DC", "haslaps", parameters)
    os_perc = get_dict_param_value("DC", "osProbability", parameters)
    os_list = get_server_os_list(os_perc)

    # New params
    privesc_perc = get_perc_param_value("Computer", "privesc", parameters)
    creddump_perc = get_perc_param_value("Computer", "creddump", parameters)
    exploitable_perc = get_perc_param_value("Computer", "exploitable", parameters)

    print_dc_generation_parameters(enabled_perc, has_laps_perc, os_perc)
    dc_properties_list = generate_main_dc(domain_name, domain_sid, domain_dn, dcou, current_time, parameters, dc_properties_list, functional_level)
    domain_controllers = []
    for i in range(2):
        comp_name = get_computer_name(f"LABDC{i}", domain_name)
        group_name = cn("DOMAIN CONTROLLERS", domain_name)
        sid = get_sid_from_rid(ridcount[0], domain_sid)
        enabled = generate_boolean_value(enabled_perc, get_complementary_value(enabled_perc))
        has_laps = generate_boolean_value(has_laps_perc, get_complementary_value(has_laps_perc))
        os = random.choice(os_list)

        # New params
        privesc = generate_boolean_value(privesc_perc, get_complementary_value(privesc_perc))
        creddump = generate_boolean_value(creddump_perc, get_complementary_value(creddump_perc))
        if is_os_vulnerable(os):
            exploitable = generate_boolean_value(exploitable_perc, get_complementary_value(exploitable_perc))
        else:
            exploitable = False

        dc_properties = {
            'name': comp_name,
            'id': sid,
            'operatingsystem': os,
            'enabled': enabled,
            'haslaps': has_laps,
            'highvalue': False,
            'lastlogontimestamp': generate_timestamp(current_time),
            'pwdlastset': generate_timestamp(current_time),
            'serviceprincipalnames': generate_server_service_pricipal_names(comp_name, domain_name),
            'unconstraineddelegation': True,
            'privesc': privesc,
            'creddump': creddump,
            'exploitable': exploitable
        }
        ridcount[0] += 1
        dc_properties_list.append(dc_properties)

        # Extract properties
        sid=sid
        name=comp_name
        os=dc_properties["operatingsystem"]
        enabled=dc_properties["enabled"]
        haslaps=dc_properties["haslaps"]
        highvalue=dc_properties["highvalue"]
        lastlogontimestamp=dc_properties["lastlogontimestamp"]
        pwdlastset=dc_properties["pwdlastset"]
        serviceprincipalnames=dc_properties["serviceprincipalnames"]
        unconstraineddelegation=dc_properties["unconstraineddelegation"]
        privesc=dc_properties["privesc"]
        creddump=dc_properties["creddump"]
        exploitable=dc_properties["exploitable"]

        keys = ["domain", "labels", "objectid", "name", "operatingsystem", "enabled", "haslaps", "highvalue", "lastlogontimestamp", "pwdlastset",
                "serviceprincipalnames", "unconstraineddelegation", "privesc", "creddump", "exploitable"]
        values = [domain_name, "Computer", sid, name, os, enabled, haslaps, highvalue, lastlogontimestamp, pwdlastset,
                serviceprincipalnames, unconstraineddelegation, privesc, creddump, exploitable]
        id_lookup = sid
        node_operation("Computer", keys, values, id_lookup)
        domain_controllers.append(comp_name)

        # Computer DC --MemberOf--> Domain Controllers Group
        start_index = get_node_index(comp_name + "_Computer", "name")
        end_index = get_node_index(group_name + "_Group", "name")
        rel_type = "MemberOf"
        props = ["isacl"]
        values = [False]
        edge_operation(start_index, end_index, rel_type, props, values)
        

        set_computer_dn(comp_name, ou_dn)

        # Domain Controllers OU --Contains--> Computer DC
        start_index = get_node_index(dcou, "objectid")
        end_index = get_node_index(sid, "objectid")
        rel_type = "Contains"
        props = ["isacl"]
        values = [False]
        edge_operation(start_index, end_index, rel_type, props, values)
        
        
        # Computer DC --MemberOf--> ENTERPRISE DOMAIN CONTROLLERS Group
        start_index = get_node_index(sid, "objectid")
        end_index = get_node_index(cn("ENTERPRISE DOMAIN CONTROLLERS", domain_name) + "_Group", "name")
        rel_type = "MemberOf"
        props = ["isacl"]
        values = [False]
        edge_operation(start_index, end_index, rel_type, props, values)

        
        # Domain Admin Group --AdminTo--> DC Computer
        start_index = get_node_index(cn("DOMAIN ADMINS", domain_name) + "_Group", "name")
        end_index = get_node_index(sid, "objectid")
        rel_type = "AdminTo"
        props = ["isacl", "fromgpo"]
        values = [False, False]
        edge_operation(start_index, end_index, rel_type, props, values)


    return dc_properties_list, domain_controllers

def generate_main_dc(domain_name, domain_sid, domain_dn, dcou, current_time, parameters, dc_properties_list, functional_level):
    ou_dn = get_ou_dn("Domain Controllers", domain_dn)
    comp_name = get_computer_name("MAINDC", domain_name)
    group_name = cn("DOMAIN CONTROLLERS", domain_name)
    sid = get_sid_from_rid(ridcount[0], domain_sid)
    has_laps_perc = get_perc_param_value("DC", "haslaps", parameters)
    has_laps = generate_boolean_value(has_laps_perc, get_complementary_value(has_laps_perc))

    # New params
    privesc_perc = get_perc_param_value("Computer", "privesc", parameters)
    creddump_perc = get_perc_param_value("Computer", "creddump", parameters)
    exploitable_perc = get_perc_param_value("Computer", "exploitable", parameters)
    privesc = generate_boolean_value(privesc_perc, get_complementary_value(privesc_perc))
    creddump = generate_boolean_value(creddump_perc, get_complementary_value(creddump_perc))
    exploitable = generate_boolean_value(exploitable_perc, get_complementary_value(exploitable_perc))

    dc_properties = {
        'name': comp_name,
        'id': sid,
        'operatingsystem': get_main_dc_os(functional_level),
        'enabled': True,
        'haslaps': has_laps,
        'highvalue': False,
        'lastlogontimestamp': generate_timestamp(current_time),
        'pwdlastset': generate_timestamp(current_time),
        'serviceprincipalnames': generate_server_service_pricipal_names(comp_name, domain_name),
        'unconstraineddelegation': True,
        'privesc': privesc,
        'creddump': creddump,
        'exploitable': exploitable
    }
    ridcount[0] += 1
    dc_properties_list.append(dc_properties)
    
    sid=sid
    name=comp_name
    os=dc_properties["operatingsystem"]
    enabled=dc_properties["enabled"]
    haslaps=dc_properties["haslaps"]
    highvalue=dc_properties["highvalue"]
    lastlogontimestamp=dc_properties["lastlogontimestamp"]
    pwdlastset=dc_properties["pwdlastset"]
    serviceprincipalnames=dc_properties["serviceprincipalnames"]
    unconstraineddelegation=dc_properties["unconstraineddelegation"]
    privesc=dc_properties["privesc"]
    creddump=dc_properties["creddump"]
    exploitable=dc_properties["exploitable"]
    keys = ["domain", "labels", "objectid", "name", "operatingsystem", "enabled", "haslaps", "highvalue", "lastlogontimestamp", "pwdlastset",
            "serviceprincipalnames", "unconstraineddelegation", "privesc", "creddump", "exploitable"]
    values = [domain_name, "Computer", sid, name, os, enabled, haslaps, highvalue, lastlogontimestamp, pwdlastset,
            serviceprincipalnames, unconstraineddelegation, privesc, creddump, exploitable]
    id_lookup = sid
    node_operation("Computer", keys, values, id_lookup)

    # Computer DC --MemberOf--> Domain Controllers Group
    start_index = get_node_index(comp_name + "_Computer", "name")
    end_index = get_node_index(group_name + "_Group", "name")
    rel_type = "MemberOf"
    props = ["isacl"]
    values = [False]
    edge_operation(start_index, end_index, rel_type, props, values)
    
    set_computer_dn(comp_name, ou_dn)

    # Domain Controllers OU --Contains--> Computer DC
    start_index = get_node_index(dcou, "objectid")
    end_index = get_node_index(sid, "objectid")
    rel_type = "Contains"
    props = ["isacl"]
    values = [False]
    edge_operation(start_index, end_index, rel_type, props, values)
    
    
    # Computer DC --MemberOf--> ENTERPRISE DOMAIN CONTROLLERS Group
    start_index = get_node_index(sid, "objectid")
    end_index = get_node_index(cn("ENTERPRISE DOMAIN CONTROLLERS", domain_name) + "_Group", "name")
    rel_type = "MemberOf"
    props = ["isacl"]
    values = [False]
    edge_operation(start_index, end_index, rel_type, props, values)

    
    # Domain Admin Group --AdminTo--> Computer
    start_index = get_node_index(cn("DOMAIN ADMINS", domain_name) + "_Group", "name")
    end_index = get_node_index(sid, "objectid")
    rel_type = "AdminTo"
    props = ["isacl", "fromgpo"]
    values = [False, False]
    edge_operation(start_index, end_index, rel_type, props, values)

    return dc_properties_list

def create_groups(domain_name, domain_sid, parameters, nTiers):
    locations = get_locations(parameters)
    access_rights = ['Read', 'Modify', 'Write', 'Full']
    thresholds = get_threshold_values("Group", "nResourcesThresholds", parameters)
    lower = thresholds[0]
    upper = thresholds[1]
    folder_name = ['Folder_' + str(i) for i in range(0, max(lower, upper))]


    # Group bounded by Departments
    departments_probs = get_dict_param_value("Group", "departmentProbability", parameters)
    departments_list = get_departments(departments_probs)
    TG = ["Distribution", "Security"]
    lowest_tier_no_admin = min(2, nTiers - 1)
    num_groups = 0

    for i in range(lowest_tier_no_admin, nTiers):
        for t in TG:
        # Generate an OU for each department
            sub_list = [f"T{i} {t} {d}" for d in departments_list]
            parent_name = f"T{i} {t} Groups"
            create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "OU", "Contains")

            for d in departments_list:
                if t == "Distribution":
                    sub_list = [f"T{i} {t} {d}_{s}" for s in locations]
                    DISTRIBUTION_GROUPS[i][d] = [f"T{i} {t} {d}_{s}@{domain_name}" for s in locations]
                else:
                    sub_list = [] # Security groups

                    # For shared resource access
                    for r in access_rights: # For each access right, generate a random number of folders
                        max_number_folders = random.randint(lower, upper)
                        FOLDERS[i][d] = []
                        for n in range(max_number_folders):
                            folder_name = f"T{i}_{d}_Folder{n}_{r}"
                            sub_list.append(folder_name)
                            SECURITY_GROUPS[i].append(cn(folder_name, domain_name))
                            FOLDERS[i][d].append(cn(folder_name, domain_name))

                    # For delegation
                    if d == "IT":
                        thresholds_local_admins = get_threshold_values("Group", "nLocalAdminsPerDepartment", parameters)
                        num_local_admins = random.randint(thresholds_local_admins[0], thresholds_local_admins[1])
                        for j in range(num_local_admins):
                            local_admin_name = f"T{i}_{d} Local Admins {j}"
                            sub_list.append(local_admin_name)
                            LOCAL_ADMINS[i].append(local_admin_name)


                    # Store SECURITY GROUPS to DB, raw name
                    # SECURITY_GROUPS[i].extend(sub_list)

                parent_name = f"T{i} {t} {d}"
                ous_dn = [f"Tier {i}", f"T{i} Groups", f"T{i} {t} Groups", f"T{i} {t} {d}"]
                create_sub_objects(domain_name, domain_sid, parent_name, "OU", sub_list, "Group", "Contains", ous_dn)
                num_groups += len(sub_list)
    
    return num_groups

def create_kerberoastable_users(nTiers, parameters):
    # log("Enabled", enabled_users)
    thresholds = get_threshold_values("User", "Kerberoastable", parameters)
    num_k = random.randint(thresholds[0], thresholds[1])

    lowest_tier_no_admin = min(2, nTiers - 1)
    for i in range(lowest_tier_no_admin):
        KERBEROASTABLES.append("")
    for i in range(lowest_tier_no_admin, nTiers):
        keys = ["labels", "hasspn", "owned"]
        values = ["Compromised", True, True]
        for count in range(num_k):
            try:
                id_lookup = random.choice(ENABLED_USERS[i])
                KERBEROASTABLES.append(id_lookup)
                node_operation("User", keys, values, id_lookup, "name")
            except:
                continue
    
    print("Kerberoastable users: ", KERBEROASTABLES)
    