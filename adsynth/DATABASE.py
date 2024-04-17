import copy
import sys
import warnings

def update_DATABASE_ID(label, NODES_index):
    identifiers = ["name", "objectid"]
    for identifier in identifiers:
        if identifier in NODES[NODES_index]["properties"]:
            check_data = NODES[NODES_index]["properties"][identifier]
            if identifier == "name":
                check_data += "_" + label

            if check_data not in DATABASE_ID[identifier]:
                DATABASE_ID[identifier][check_data] = NODES_index

def node_operation(label, keys, values, id_lookup, identifier = "objectid", is_domain = False):
    global neo4j_id
    NODES_index = -1
    new_node = dict()

    # Multiple nodes have the same name but different type
    # In the hashed map, name + "_" + label
    if identifier == "name":
        id_lookup += "_" + label


    # If name/objectid already exists
    # Retrieve the index of the specified node in the list NODES
    if id_lookup in DATABASE_ID[identifier]:
        NODES_index = DATABASE_ID[identifier][id_lookup]
    else:
        # Create interface
        if not is_domain:
            new_node = copy.deepcopy(AD_NODE)
        else:
            new_node = copy.deepcopy(AD_NODE_ADMIN)

        # Get the NODES_index
        NODES_index = len(NODES)

        # Add to the list NODES
        NODES.append(new_node)

        # Add to the dictionary
        DATABASE_ID[identifier][id_lookup] = NODES_index

        # Add to the NODE_GROUPS
        NODE_GROUPS[label].append(NODES_index)

        # Set Neo4J internal id
        NODES[NODES_index]["id"] = str(neo4j_id)

        # Update Neo4J ID
        neo4j_id += 1


    # Update the node
    for i in range(len(keys)):

        # Set labels/properties
        if keys[i] == "labels":
            if values[i] not in NODES[NODES_index][keys[i]]:
                NODES[NODES_index][keys[i]].append(values[i])
        else:
            NODES[NODES_index]["properties"][keys[i]] = values[i]

    # Set attribute 'owned' of all users and computers to False
    # If an entity is comprommised, mark 'owner' True
    if label == "User" or "Computer":
        NODES[NODES_index]["properties"]["owned"] = False
        
    # Update DATABSE_ID, if required
    update_DATABASE_ID(label, NODES_index)
    
    return NODES_index

def edge_operation(start_index, end_index, relationship_type, props = [], values = []):
    hashed_id_edge = str(start_index) + relationship_type + str(end_index)
    EDGES_index = -1
    new_edge = dict()

    if hashed_id_edge not in dict_edges:
        # Create interface
        new_edge = copy.deepcopy(AD_EDGE)

        # Get EDGES index
        EDGES_index = len(EDGES)

        # Add to the EDGES list
        EDGES.append(new_edge)

        # Add to dictionary
        dict_edges[hashed_id_edge] = EDGES_index

        # Set Neo4J internal id
        EDGES[EDGES_index]["id"] = "r_" + str(EDGES_index)

        # Set label
        EDGES[EDGES_index]["label"] = relationship_type
    
        # Set start node
        EDGES[EDGES_index]["start"]["id"] = NODES[start_index]["id"]
        EDGES[EDGES_index]["start"]["labels"] = NODES[start_index]["labels"]

        # Set end node
        EDGES[EDGES_index]["end"]["id"] = NODES[end_index]["id"]
        EDGES[EDGES_index]["end"]["labels"] = NODES[end_index]["labels"]

        # Store OUs with GpLink
        if NODES[start_index]["labels"][-1] == "GPO" and NODES[end_index]["labels"][-1] == "OU":
            GPLINK_OUS.append(end_index)   
        
  
    else:
        EDGES_index = dict_edges[hashed_id_edge]


    # Update edge
    for i in range(len(props)):
        EDGES[EDGES_index]["properties"][props[i]] = values[i]

def get_node_index(id_lookup, identifier):
    if id_lookup in DATABASE_ID[identifier]:
        return DATABASE_ID[identifier][id_lookup]
    
    # adding a single entry into warnings filter
    warnings.simplefilter('error', UserWarning)
    # displaying the warning
    warnings.warn(f"Node not exisit: {id_lookup} - {identifier}")
    return -1


NODES = []
EDGES = []

neo4j_id = 0

# Local DATABASE for NODES, 
# It will be dumped to a JSON file and import to NEO4J after generating the complete AD graph
DATABASE_ID = {
    "name": dict(),
    "objectid": dict()
}

# Local DATABASE for EDGES
dict_edges = dict()

AD_NODE = {
    "id":"",
    "labels":["Base"],
    "properties": {
    }
}

AD_NODE_ADMIN = {
    "id":"",
    "labels":[],
    "properties": {
    }
}

AD_EDGE = {
    "type": "relationship",
    "id": "",
    "properties": {},
    "start": {},
    "end": {}
}

NODE_GROUPS = {
    "User": list(),
    "Computer": list(),
    "GPO": list(), 
    "Group": list(),
    "Domain": list(),
    "OU": list(),
    "Container": list()
}

GPLINK_OUS = []

GROUP_MEMBERS = dict()

SECURITY_GROUPS = list() # processed names # Tiered

ADMIN_USERS = list() # processed names # Tiered

ENABLED_USERS = list() # processed names # Tiered

DISABLED_USERS = list() # processed names

PAW_TIERS = list() # Tiered

S_TIERS = list() # Tiered

S_TIERS_LOCATIONS = list() # processed names, separated by tiers and locations

WS_TIERS = list() # Tiered

WS_TIERS_LOCATIONS = list() # processed names, separated by tiers and locations

COMPUTERS = list() # All

ridcount = list()

KERBEROASTABLES = list() # processed names

FOLDERS = list() # processed names, separated by tiers and departments

DISTRIBUTION_GROUPS = list() # processed names,  separated by tiers and departments

SEC_DIST_GROUPS = list()

LOCAL_ADMINS = list() # not processed names

