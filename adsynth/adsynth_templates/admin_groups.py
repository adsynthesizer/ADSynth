T0_ADMIN_GROUPS = ["PRINT OPERATORS", "ACCOUNT OPERATORS", "SERVER OPERATORS", "DOMAIN ADMINS"]

Tn_ADMIN_GROUPS = ["Admin Accounts Group", "PAW Maintenance", "Server Management", "Service Accounts Group"]

def get_t0_admin_groups():
  return T0_ADMIN_GROUPS

def get_tn_admin_groups():
  return Tn_ADMIN_GROUPS

def get_admin_groups(tier):
  if tier == 0:
    return T0_ADMIN_GROUPS
  
  admin_groups = [f"T{tier} {g}" for g in Tn_ADMIN_GROUPS]
  return admin_groups
