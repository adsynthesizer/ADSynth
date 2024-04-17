from adsynth.DATABASE import edge_operation, get_node_index, node_operation
from adsynth.entities.acls import cn
from adsynth.entities.groups import get_forest_default_group_members_list, get_forest_default_groups_list

# Idea Ref: ADSimulator, DBCreator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
def create_default_groups(domain_name, domain_sid, old_domain_name):
    default_groups_list = get_forest_default_groups_list(
        domain_name, domain_sid, old_domain_name)
    for default_group in default_groups_list:
        default_group_properties = default_group["Properties"]
        gname = default_group["Properties"]["name"]
        sid = default_group["ObjectIdentifier"]

        highvalue = default_group["Properties"]["highvalue"] if "highvalue" in default_group_properties else "null"
        domain = default_group["Properties"]["domain"] if "domain" in default_group_properties else "null"
        distinguishedname = default_group["Properties"]["distinguishedname"] if "distinguishedname" in default_group_properties else "null"
        description = default_group["Properties"]["description"] if "description" in default_group_properties else "null"
        admincount = default_group["Properties"]["admincount"] if "admincount" in default_group_properties else "null"

        keys = ["domain", "name", "labels", "objectid", "highvalue",
                "distinguishedname", "description", "admincount"]
        values = [domain, gname, "Group", sid, highvalue,
                    distinguishedname, description, admincount]
        id_lookup = default_group["ObjectIdentifier"]

        node_operation("Group", keys, values, id_lookup)

# Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
def generate_default_member_of(domain_name, domain_sid, old_domain_name):
    standard_group_members_list = get_forest_default_group_members_list(
        domain_name, domain_sid, old_domain_name)
    for group_member in standard_group_members_list:
        add_member_of_relationship(group_member)


def add_member_of_relationship(ad_object):
    try:
        start_index = get_node_index(ad_object["MemberId"], "objectid")
        end_index = get_node_index(ad_object["GroupId"], "objectid")
        rel_type = "MemberOf"
        props = ["isacl"]
        values = [False]
        if start_index >= 0 and end_index >= 0:
            edge_operation(start_index, end_index, rel_type, props, values)
    except:
        pass

# Idea Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
def create_adminstrator_memberships(domain_name):
    name = cn("ADMINISTRATOR", domain_name)
    highvalue_groups = ["PRINT OPERATORS", "BACKUP OPERATORS", "SERVER OPERATORS",
                        "ACCOUNT OPERATORS", "ENTERPRISE ADMINS", "DOMAIN ADMINS", "DOMAIN CONTROLLERS", 
                        "GROUP POLICY CREATOR OWNERS"]
    
    start_index = get_node_index(name + "_User", "name")
    rel_type = "MemberOf"
    
    for group in highvalue_groups:
        end_index = get_node_index(cn(group, domain_name) + "_Group", "name")
        edge_operation(start_index, end_index, rel_type)

