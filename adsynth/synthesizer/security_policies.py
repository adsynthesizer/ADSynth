import random
import uuid
from adsynth.DATABASE import GPLINK_OUS, NODE_GROUPS, edge_operation, get_node_index, node_operation
from adsynth.adsynth_templates.default_config import get_complementary_value
from adsynth.entities.acls import cn, cs
from adsynth.utils.boolean import generate_boolean_value
from adsynth.utils.gpos import get_gpos_container_dn
from adsynth.utils.parameters import get_int_param_value, get_perc_param_value

# Idea Ref: https://learn.microsoft.com/en-us/previous-versions/windows/desktop/policy/group-policy-storage
def create_gpos_container(domain_name, domain_dn, gpos_container):
    guid = gpos_container
    name = cn("Group Policy Objects Container", domain_name)
    dn = get_gpos_container_dn(domain_dn)

    keys = ["domain", "name", "objectid", "highvalue", "distinguishedname", "labels"]
    values = [domain_name, name, guid, True, dn, "Container"]

    id_lookup = guid
    node_operation("Container", keys, values, id_lookup)

def apply_gpos(domain_name, domain_sid, nTiers):
    # A ---GpLink---> B
    # C ---GpLink---> D
    # E ---GpLink---> F

    if nTiers == 1:
        return
    
    lowest_tier_no_admin = min(2, nTiers - 1)

    # Idea Ref: Russell Smith, https://petri.com/keep-active-directory-secure-using-privileged-access-workstations/, https://volkandemirci.org/2022/01/17/privileged-access-workstations-kurulumu-ve-yapilandirilmasi-2/
    gpos_map = {
        'Admins Configuration': ['Admin'],
        # 'New_PC Configuration': ['Quarantine'],
        'Restrict Workstation Logon': [f"T{i} Workstations" for i in range(lowest_tier_no_admin, nTiers)],
        'Normal_Users Configuration': [f"T{i} User Accounts" for i in range(lowest_tier_no_admin, nTiers)],
        'Group Configuration': [f"T{i} Groups" for i in range(lowest_tier_no_admin, nTiers)],
        'Server Configuration': [f"T{i} Servers" for i in range(lowest_tier_no_admin, nTiers)],
        'PAW Configuration': ['T0 Admin Devices'],
        'PAW Outbound restrictions': ['T0 Admin Devices'],
        'RestrictedAdmin Required -Computer': [f"T{i} Admin Devices" for i in range(1, nTiers)]
    }

    if nTiers > 2:
        gpos_map.update({'Restrict Server Logon': ['Tier 1 Servers']})

    for gpo in gpos_map:
        # Create GPO
        guid = cs(str(uuid.uuid4()), domain_sid)
        gpo_name = cn(gpo, domain_name)
        keys = ["domain", "name", "objectid", "labels"]
        values = [domain_name, gpo_name, guid, "GPO"]
        id_lookup = guid
        node_operation("GPO", keys, values, id_lookup)

        # GPO --GpLink--> OU
        start_index = get_node_index(gpo_name + "_GPO", "name")
        rel_type = "GpLink"
        for ou in gpos_map[gpo]:
            end_index = get_node_index(cn(ou, domain_name) + "_OU", "name")
            edge_operation(start_index, end_index, rel_type)
    

def apply_restriction_gpos(domain_name, domain_sid, parameters):
    unlinked_OUs = list(set(NODE_GROUPS["OU"]) - set(GPLINK_OUS))

    # Idea Ref: https://learn.microsoft.com/en-us/windows-server/identity/software-restriction-policies/administer-software-restriction-policies
    #           https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/access-this-computer-from-the-network
    #           https://activedirectorypro.com/group-policy-examples-most-useful-gpos-for-security/
    
    GPO_names = ["Network_Restriction_", "Data_Access_Restriction_", "System_Restriction_","Software_Restriction_"]
    
    
    for i in range(get_int_param_value("GPO", "nGPOs", parameters)):
        # Randomly choose a Restriction GPO type
        gpo_name = cn(random.choice(GPO_names)+str(i), domain_name)

        # Create the GPO
        guid = cs(str(uuid.uuid4()), domain_sid)
        exploitable_perc = get_perc_param_value("GPO", "exploitable", parameters)
        exploitable = generate_boolean_value(exploitable_perc, get_complementary_value(exploitable_perc))
        keys = ["domain", "name", "objectid", "exploitable", "labels"]
        values = [domain_name, gpo_name, guid, exploitable, "GPO"]
        id_lookup = guid
        node_operation("GPO", keys, values, id_lookup)
        
        # GpLink to a unlinked_OU
        start_index = get_node_index(gpo_name + "_GPO", "name")
        end_index = random.choice(unlinked_OUs)
        rel_type = "GpLink"
        edge_operation(start_index, end_index, rel_type)

def place_gpos_in_container(domain_name, gpos_container):
    start_index = get_node_index(gpos_container, "objectid")
    rel_type = "Contains"
    for i in NODE_GROUPS["GPO"]:
        end_index = i
        edge_operation(start_index, end_index, rel_type)
    