NON_ACLS_LIST = ["CanRDP"] * 25 + ["ExecuteDCOM"] * 25 + \
                ["AllowedToDelegate"] * 25 + ["ReadLAPSPassword"] * 25 + ["CanPSRemote"] * 0

def get_non_acls_list(prob):
    sum = 0
    for key in prob.keys():
        sum += prob[key]
    if sum != 100:
        return NON_ACLS_LIST
    try:
        return ["CanRDP"] * prob["CanRDP"] +\
            ["ExecuteDCOM"] * prob["ExecuteDCOM"] +\
            ["AllowedToDelegate"] * prob["AllowedToDelegate"] +\
            ["ReadLAPSPassword"] * prob["ReadLAPSPassword"] +\
            ["CanPSRemote"] * prob["CanPSRemote"]
            
    except:
        return NON_ACLS_LIST

