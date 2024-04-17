from adsynth.DATABASE import edge_operation, get_node_index


def extract_hyperedges(start_name, start_type, end_set, end_type, rel_type, props = [], values = []):
    # All nodes are assumed to have a full name, including domain name
    start_index = get_node_index(f"{start_name}_{start_type}", "name")
    for node in end_set:
        end_index = node if isinstance(node, int) else get_node_index(f"{node}_{end_type}", "name")
        edge_operation(start_index, end_index, rel_type, props, values)
