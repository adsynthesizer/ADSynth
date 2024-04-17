from adsynth.DATABASE import node_operation
from adsynth.utils.computers import get_computer_dn
from adsynth.utils.domains import get_domain_dn
from adsynth.utils.principals import get_cn


def get_dn_leaf_objects(name, ous, domain_dn):
    ldap_path = ""
    for i in range(len(ous) - 1, -1, -1):
        ldap_path += f"OU={ous[i]},"
    cn = get_cn(name)
    return "CN=" + cn + "," + ldap_path + domain_dn    

def add_dn(domain_name, name, object_type, ous_dn):
    domain_dn = get_domain_dn(domain_name)
    dn = get_dn_leaf_objects(name, ous_dn, domain_dn)
    keys = ["distinguishedname"]
    values = [dn]
    node_operation(object_type, keys, values, name, "name")

def set_computer_dn(computer_name, ou_dn):
    computer_dn = get_computer_dn(computer_name, ou_dn)
    keys = ["distinguishedname"]
    values = [computer_dn]
    id_lookup = computer_name
    node_operation("Computer", keys, values, id_lookup, "name")
