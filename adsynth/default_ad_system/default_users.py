import random
from adsynth.DATABASE import edge_operation, get_node_index, node_operation
from adsynth.entities.users import get_administrator_user, get_default_account, get_forest_user_sid_list, get_guest_user, get_krbtgt_user
from adsynth.adsynth_templates.default_config import get_complementary_value
from adsynth.utils.boolean import generate_boolean_value
from adsynth.utils.parameters import get_perc_param_value
from adsynth.utils.principals import get_cn

# Idea Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts


def generate_guest_user(domain_name, domain_sid, parameters):
    guest_user = get_guest_user(domain_name, domain_sid)
    create_user(guest_user, parameters)

def generate_default_account(domain_name, domain_sid, parameters):
    default_account = get_default_account(domain_name, domain_sid)
    create_user(default_account, parameters)

def generate_administrator(domain_name, domain_sid, parameters):
    administrator_user = get_administrator_user(domain_name, domain_sid)
    create_user(administrator_user, parameters)

def generate_krbtgt_user(domain_name, domain_sid, parameters):
    krbtgt_user = get_krbtgt_user(domain_name, domain_sid)
    create_user(krbtgt_user, parameters)

def create_user(user, parameters):
    if get_cn(user["Properties"]["name"]) == "GUEST":
        enabled_property = random.choice([True, False])
        pwdneverexpires_property = random.choice([True, False])
    else:
        enabled_property = user["Properties"]["enabled"]
        pwdneverexpires_property = user["Properties"]["pwdneverexpires"]

    # New properties
    savedcredentials_perc = get_perc_param_value(
        "User", "savedcredentials", parameters)
    savedcredentials = generate_boolean_value(
        savedcredentials_perc, get_complementary_value(savedcredentials_perc))

    # Properties
    name = user["Properties"]["name"]
    sid = user["ObjectIdentifier"]
    highvalue = user["Properties"]["highvalue"]
    domain = user["Properties"]["domain"]
    distinguishedname = user["Properties"]["distinguishedname"]
    description = user["Properties"]["description"]
    admincount = user["Properties"]["admincount"]
    dontreqpreauth = user["Properties"]["dontreqpreauth"]
    passwordnotreqd = user["Properties"]["passwordnotreqd"]
    unconstraineddelegation = user["Properties"]["unconstraineddelegation"]
    sensitive = user["Properties"]["sensitive"]
    enabled = enabled_property,
    pwdneverexpires = pwdneverexpires_property,
    lastlogon = user["Properties"]["lastlogon"]
    lastlogontimestamp = user["Properties"]["lastlogontimestamp"]
    pwdlastset = user["Properties"]["pwdlastset"]
    serviceprincipalnames = user["Properties"]["serviceprincipalnames"]
    hasspn = user["Properties"]["hasspn"]
    displayname = user["Properties"]["displayname"]
    email = user["Properties"]["email"]
    title = user["Properties"]["title"]
    homedirectory = user["Properties"]["homedirectory"]
    userpassword = user["Properties"]["userpassword"]
    sidhistory = user["Properties"]["sidhistory"]
    savedcredentials = savedcredentials

    keys = ["labels", "name", "objectid", "highvalue", "domain", "distinguishedname", "description",
            "admincount", "dontreqpreauth", "passwordnotreqd", "unconstraineddelegation", "sensitive",
            "enabled", "pwdneverexpires", "lastlogon", "lastlogontimestamp", "pwdlastset", "serviceprincipalnames",
            "hasspn", "displayname", "email", "title", "homedirectory", "userpassword", "sidhistory", "savedcredentials"]
    values = ["User", name, sid, highvalue, domain, distinguishedname, description, admincount, dontreqpreauth, passwordnotreqd,
              unconstraineddelegation, sensitive, enabled, pwdneverexpires, lastlogon, lastlogontimestamp, pwdlastset, serviceprincipalnames,
              hasspn, displayname, email, title, homedirectory, userpassword, sidhistory, savedcredentials]
    id_lookup = sid
    node_operation("User", keys, values, id_lookup)

def link_default_users_to_domain(domain_name, domain_sid):
    standard_users_list = get_forest_user_sid_list(domain_name, domain_sid)
    for user in standard_users_list:
        add_contains_object_on_domain_relationship(user)

def add_contains_object_on_domain_relationship(ad_object):
    start_index = get_node_index(ad_object["DomainId"], "objectid")
    end_index = get_node_index(ad_object["ObjectId"], "objectid")
    rel_type = "Contains"
    props = ["isacl"]
    values = [False]
    edge_operation(start_index, end_index, rel_type, props, values)
