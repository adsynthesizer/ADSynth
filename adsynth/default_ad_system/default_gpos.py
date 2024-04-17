import uuid
from adsynth.DATABASE import edge_operation, get_node_index, node_operation
from adsynth.utils.gpos import get_gpc_path, get_gpo_dn
from adsynth.entities.acls import cn

# Idea Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-gpod/566e983e-3b72-4b2d-9063-a00ebc9514fd
def create_default_gpos(domain_name, domain_dn, ddp, ddcp):
    default_gpos = {
        "DEFAULT DOMAIN POLICY": ddp,
        "DEFAULT DOMAIN CONTROLLERS POLICY": ddcp
    }

    for element in default_gpos:
        guid = default_gpos[element]
        gpo = cn(element, domain_name)
        cn_ = "{" + str(uuid.uuid4()).upper() + "}"
        dn = get_gpo_dn(cn_, domain_dn)
        gpc_path = get_gpc_path(cn_, domain_name)
        exploitable = False

        keys = ["domain", "name", "objectid", "highvalue", "distinguishedname", "gpcpath", "labels", "exploitable"]
        values = [domain_name, gpo, guid, False, dn, gpc_path, "GPO", exploitable]
        id_lookup = guid
        node_operation("GPO", keys, values, id_lookup)

# Ref: DBCreator, ADSimulator
def apply_default_gpos(domain_name, ddp, ddcp, dcou):
    # DEFAULT DOMAIN POLICY --GpLink--> Domain
    start_index = get_node_index(ddp, "objectid")
    end_index = get_node_index(domain_name + "_Domain", "name")
    rel_type = "GpLink"
    props = ["isacl", "enforced"]
    values = [False, False]

    edge_operation(start_index, end_index, rel_type, props, values)
    
    # Domain --Contains--> DCOU
    start_index = get_node_index(domain_name+"_Domain", "name")
    end_index = get_node_index(dcou, "objectid")
    rel_type = "Contains"
    props = ["isacl"]
    values = [False]

    edge_operation(start_index, end_index, rel_type, props, values)

    # DEFAULT DOMAIN CONTROLLERS POLICY --GpLink--> DCOU
    start_index = get_node_index(ddcp, "objectid")
    end_index = get_node_index(dcou, "objectid")
    rel_type = "GpLink"
    props = ["isacl", "enforced"]
    values = [False, False]

    edge_operation(start_index, end_index, rel_type, props, values)
