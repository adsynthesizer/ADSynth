from adsynth.DATABASE import node_operation
from adsynth.entities.acls import cn
from adsynth.utils.ous import get_ou_dn

# Idea Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/delegating-administration-of-default-containers-and-ous
def create_domain_controllers_ou(domain_name, domain_dn, dcou):
    guid = dcou
    ou = cn("DOMAIN CONTROLLERS", domain_name)
    ou_dn = get_ou_dn("Domain Controllers", domain_dn)
    dn = ou_dn
    description = "Default container for domain controllers"
    
    keys = ["domain", "name", "objectid", "blocksInheritance", "highvalue", "distinguishedname", "description", "labels"]
    values = [domain_name, ou, guid, False, False, dn, description, "OU"]
    id_lookup = guid
    node_operation("OU", keys, values, id_lookup)
    