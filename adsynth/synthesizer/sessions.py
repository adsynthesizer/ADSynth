import random
from adsynth.DATABASE import ADMIN_USERS, ENABLED_USERS, edge_operation, get_node_index, node_operation
from adsynth.helpers.getters import get_list_perc_param_value
from adsynth.utils.parameters import get_int_param_value, get_perc_param_value


def create_sessions_per_set(parameters, U, C, tier_list, perc_sessions, priority_session_weight, restricted = False):
    lowest_tier = tier_list[0]
    total_comps_from_current_to_above = 0

    for tier in tier_list:
        weights = [1 for i in range(lowest_tier, tier + 1)]
        weights[-1] = priority_session_weight
        total_comps_from_current_to_above += len(C[tier])
        for user in U[tier]:
            # Only a small set of users with special roles can log on to servers
            if restricted:
                perc_special_roles = get_perc_param_value("User", "perc_special_roles", parameters)
                is_special_role = random.choice([True] * perc_special_roles + [False] * (100 - perc_special_roles))
                if is_special_role:
                    # Update the user with flag special_role
                    keys = ["special_role"]
                    values = [True]
                    id_lookup = user
                    node_operation("User", keys, values, id_lookup, "name")
                else:
                    continue

            end_index = get_node_index(user + "_User", "name")
            num_sessions = random.randint(0, int(total_comps_from_current_to_above * perc_sessions / 100))
            for i in range(num_sessions):
                comp_tier = random.choices(range(lowest_tier, tier + 1), weights)[0]
                try:
                    comp = random.choice(C[comp_tier])
                except:
                    continue
                start_index = get_node_index(comp + "_Computer", "name")
                edge_operation(start_index, end_index, "HasSession")
          
def create_sessions(nTiers, PAW, Servers, Workstations, parameters):
    lowest_tier_no_admin = min(2, nTiers - 1)
    perc_sessions = get_list_perc_param_value("User", "sessionsPercentages", parameters)
    priority_session_weight = get_int_param_value("User", "priority_session_weight", parameters) # Cross-tier sessions in Tier Administrative Model
    # log("PAW", PAW)
    # Sessions for ADMIN USERS per tier
    create_sessions_per_set(parameters, ADMIN_USERS, PAW, [i for i in range(nTiers)], perc_sessions[0], priority_session_weight)

    # # Sessions for normal users using WS
    create_sessions_per_set(parameters, ENABLED_USERS, Workstations, [i for i in range(lowest_tier_no_admin, nTiers)], perc_sessions[1], priority_session_weight)

    # # Sessions for normal users using Servers
    create_sessions_per_set(parameters, ENABLED_USERS, Servers, [i for i in range(lowest_tier_no_admin, nTiers)], perc_sessions[2], priority_session_weight, True)

    # # Sessions for Tier 1 Servers
    if nTiers > 2:
        create_sessions_per_set(parameters, ADMIN_USERS, Servers, [1], perc_sessions[1], priority_session_weight)

# Idea Ref: Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
def create_dc_sessions(domain_controllers, server_operators, print_operators):
    for OP in server_operators + print_operators:
        for DC in domain_controllers:
            if random.choice([True, False]):
                start_index = get_node_index(OP + "_User", "name")
                end_index = get_node_index(DC + "_Computer", "name")
                rel_type = "HasSession"
                edge_operation(start_index, end_index, rel_type)
 