import random
from adsynth.DATABASE import node_operation
from adsynth.templates.domains import get_functional_level_list
from adsynth.utils.parameters import get_dict_param_value, print_domain_generation_parameters

# Idea Ref: ADSimulator, DBCreator
def create_domain(domain_name, domain_sid, domain_dn, parameters):
    prob = get_dict_param_value("Domain", "functionalLevelProbability", parameters)
    functional_level = random.choice(get_functional_level_list(prob))
    print_domain_generation_parameters(prob)
    
    keys = ["domain", "name", "labels", "highvalue", "objectid", "distinguishedname", "functionallevel"]
    values = [domain_name, domain_name, "Domain", True, domain_sid, domain_dn, functional_level]
    id_lookup = domain_sid
    node_operation("Domain", keys, values, id_lookup)

    return functional_level
