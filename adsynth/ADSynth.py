# Requirements - pip install neo4j-driver
# This script is used to create randomized sample databases.
# Commands
# 	dbconfig - Set the credentials and URL for the database you're connecting too
#	connect - Connects to the database using supplied credentials
# 	setparams - Set the settings JSON file
# 	setdomain - Set the domain name
# 	cleardb - Clears the database and sets the schema properly
#	generate - Connects to the database, clears the DB, sets the schema, and generates random data

from neo4j import GraphDatabase
import cmd
from collections import defaultdict
import uuid
import time
import random
import os
from adsynth.default_ad_system.default_acls import create_administrators_acls, create_default_AllExtendedRights, create_default_GenericAll, create_default_GenericWrite, create_default_dc_groups_acls, create_default_groups_acls, create_default_owns, create_default_users_acls, create_default_write_dacl_owner, create_domain_admins_acls, create_enterprise_admins_acls
from adsynth.default_ad_system.default_gpos import apply_default_gpos, create_default_gpos
from adsynth.default_ad_system.default_groups import create_adminstrator_memberships, create_default_groups, generate_default_member_of
from adsynth.default_ad_system.default_ous import create_domain_controllers_ou
from adsynth.default_ad_system.default_users import generate_administrator, generate_default_account, generate_guest_user, generate_krbtgt_user, link_default_users_to_domain
from adsynth.default_ad_system.domains import create_domain
from adsynth.entities.acls import cs
from adsynth.helpers.about import print_adsynth_software_information
from adsynth.helpers.getters import get_num_tiers, get_single_int_param_value
from adsynth.helpers.objects import segregate_list
from adsynth.synthesizer.misconfig import create_misconfig_group_nesting, create_misconfig_permissions_on_groups, create_misconfig_permissions_on_individuals, create_misconfig_sessions
from adsynth.synthesizer.object_placement import nest_groups, place_admin_users_in_tiers, place_computers_in_tiers, place_normal_users_in_tiers, place_users_in_groups
from adsynth.synthesizer.objects import create_admin_groups, create_groups, create_kerberoastable_users, generate_computers, generate_dcs, generate_users
from adsynth.synthesizer.ou_structure import create_ad_skeleton
from adsynth.synthesizer.permissions import assign_administration_to_admin_principals, assign_local_admin_rights, create_control_management_permissions
from adsynth.synthesizer.security_policies import apply_gpos, apply_restriction_gpos, create_gpos_container, place_gpos_in_container
from adsynth.synthesizer.sessions import create_dc_sessions, create_sessions
from adsynth.utils.data import get_names_pool, get_surnames_pool, get_parameters_from_json, get_domains_pool
from adsynth.utils.domains import get_domain_dn
from adsynth.utils.parameters import print_all_parameters, get_int_param_value, get_perc_param_value
from adsynth.adsynth_templates.default_config import DEFAULT_CONFIGURATIONS
from adsynth.DATABASE import *
import json
from timeit import default_timer as timer
from datetime import datetime

def reset_DB():
    NODES.clear()
    EDGES.clear()

    for item in DATABASE_ID:
        DATABASE_ID[item].clear()

    dict_edges.clear()

    for item in NODE_GROUPS:
        NODE_GROUPS[item].clear()

    GPLINK_OUS.clear()

    GROUP_MEMBERS.clear()

    SECURITY_GROUPS.clear()

    LOCAL_ADMINS.clear()

    ADMIN_USERS.clear()

    ENABLED_USERS.clear() # processed names # Tiered

    DISABLED_USERS.clear() # processed names

    PAW_TIERS.clear() # Tiered

    S_TIERS.clear() # Tiered

    WS_TIERS.clear() # Tiered

    COMPUTERS.clear() # All

    ridcount.clear()

    KERBEROASTABLES.clear() # processed names

class Messages():
    def title(self):
        print(
        """
                                                                       ,----,            
                                                           ,--.      ,/   .`|       ,--, 
   ,---,           ,---,      .--.--.                    ,--.'|    ,`   .'  :     ,--.'| 
  '  .' \        .'  .' `\   /  /    '.      ,---,   ,--,:  : |  ;    ;     /  ,--,  | : 
 /  ;    '.    ,---.'     \ |  :  /`. /     /_ ./|,`--.'`|  ' :.'___,/    ,',---.'|  : ' 
:  :       \   |   |  .`\  |;  |  |--`,---, |  ' :|   :  :  | ||    :     | |   | : _' | 
:  |   /\   \  :   : |  '  ||  :  ;_ /___/ \.  : |:   |   \ | :;    |.';  ; :   : |.'  | 
|  :  ' ;.   : |   ' '  ;  : \  \    `.  \  \ ,' '|   : '  '; |`----'  |  | |   ' '  ; : 
|  |  ;/  \   \\'   | ;  .  |  `----.   \  ;  `  ,''   ' ;.    ;    '   :  ; '   |  .'. | 
'  :  | \  \ ,'|   | :  |  '  __ \  \  |\  \    ' |   | | \   |    |   |  ' |   | :  | ' 
|  |  '  '--'  '   : | /  ;  /  /`--'  / '  \   | '   : |  ; .'    '   :  | '   : |  : ; 
|  :  :        |   | '` ,/  '--'.     /   \  ;  ; |   | '`--'      ;   |.'  |   | '  ,/  
|  | ,'        ;   :  .'      `--'---'     :  \  \\'   : |          '---'    ;   : ;--'   
`--''          |   ,.'                      \  ' ;;   |.'                   |   ,/       
               '---'                         `--` '---'                     '---'        
                                                                                         
                                                                                                                                                                                              
        """
        )
        print("Synthesizing realisitc Active Directory attack graphs\n")
        print("==================================================================")

    # Ref: DBCreator
    def input_default(self, prompt, default):
        return input("%s [%s] " % (prompt, default)) or default
    
    def input_security_level(self, prompt, default):
        user_input = input("%s [%s] " % (prompt, default)) or default
        if not user_input:
            return default
        
        try:
            user_input = int(user_input)
            if user_input in [1, 2, 3]:
                    return user_input
        except:
            pass
        return default

    # Ref: DBCreator
    def input_yesno(self, prompt, default):
        temp = input(prompt + " " + ("Y" if default else "y") + "/" + ("n" if default else "N") + " ")
        if temp == "y" or temp == "Y":
            return True
        elif temp == "n" or temp == "N":
            return False
        return default



class MainMenu(cmd.Cmd):
    # The main functions to generate realistic Active Directory attack graphs using metagraphs belong to ADSynth.
    # In case of code re-use from previous work, LICENSING is provided at the top of a file
    # In case of code modification or ideas related to fundamental concepts of Active Directory, clear references are mentioned at the top of such functions.

    def __init__(self):
        self.m = Messages()
        self.url = "bolt://localhost:7687"
        self.username = "neo4j"
        self.password = "neo4j"
        self.use_encryption = False
        self.driver = None
        self.connected = False
        self.old_domain = None
        self.domain = "TESTLAB.LOCALE"
        self.current_time = int(time.time())
        self.base_sid = "S-1-5-21-883232822-274137685-4173207997"
        self.first_names = get_names_pool()
        self.last_names = get_surnames_pool()
        self.domain_names = get_domains_pool()
        self.parameters_json_path = "DEFAULT"
        self.parameters = DEFAULT_CONFIGURATIONS
        self.json_file_name = None
        self.level = "Customized"

        cmd.Cmd.__init__(self)

    
    def cmdloop(self):
        while True:
            self.m.title()
            self.do_help("")
            try:
                try:
                    cmd.Cmd.cmdloop(self)
                except EOFError:
                    break
                    return True

            except KeyboardInterrupt:
                if self.driver is not None:
                    self.driver.close()
                return True

    
    def help_dbconfig(self):
        print("Configure database connection parameters")


    def help_connect(self):
        print("Test connection to the database and verify credentials")

 
    def help_setdomain(self):
        print("Set domain name (default 'TESTLAB.LOCALE')")

 
    def help_cleardb(self):
        print("Clear the database and set constraints")

 
    def help_generate(self):
        print("Connect to the database, clear the db, set the schema, and generate random data")


    def help_setparams(self):
        print("Import the settings JSON file containing the parameters for the graph generation")


    def help_about(self):
        print("View information about adsynth")

 
    def help_exit(self):
        print("Exit")
    
    def help_remove_constraints(self):
        print("Remove Neo4J constraints")
      

    def do_about(self, args):
        print_adsynth_software_information()

 
    def do_dbconfig(self, args):
        print("Current Settings")
        print("DB Url: {}".format(self.url))
        print("DB Username: {}".format(self.username))
        print("DB Password: {}".format(self.password))
        print("Use encryption: {}".format(self.use_encryption))
        print("")

        self.url = self.m.input_default("Enter DB URL", self.url)
        self.username = self.m.input_default(
            "Enter DB Username", self.username)
        self.password = self.m.input_default(
            "Enter DB Password", self.password)

        self.use_encryption = self.m.input_yesno(
            "Use encryption?", self.use_encryption)
        
        # Level of security
        security_settings = {
            1: "Customized",
            2: "Low",
            3: "High"
        }
        security_settings_code = {
            "Customized": 1,
            "Low": 2,
            "High": 3
        }

        level_code = self.m.input_security_level(
            "Enter level of security  (type a number 1/2/3) - Cuztomized (1), Low (2), High (3): ", security_settings_code[self.level])
        self.level = security_settings[level_code]

        print("")
        print("Confirmed Settings:")
        print("DB Url: {}".format(self.url))
        print("DB Username: {}".format(self.username))
        print("DB Password: {}".format(self.password))
        print("Use encryption: {}".format(self.use_encryption))
        print("Level of Security: {}".format(self.level))
        print("")
        print("Testing DB Connection")
        self.test_db_conn()

 
    def do_setdomain(self, args):
        passed = args
        if passed != "":
            try:
                self.domain = passed.upper()
                return
            except ValueError:
                pass

        self.domain = self.m.input_default("Domain", self.domain).upper()
        print("")
        print("New Settings:")
        print("Domain: {}".format(self.domain))


    def do_exit(self, args):
        raise KeyboardInterrupt

 
    def do_connect(self, args):
        self.test_db_conn()


    def do_remove_constraints(self, session):
        # Remove constraint - From DBCreator
        print("Resetting Schema")
        for constraint in session.run("SHOW CONSTRAINTS"):
            session.run("DROP CONSTRAINT {}".format(constraint['name']))

        icount = session.run(
            "SHOW INDEXES YIELD name RETURN count(*)")
        for r in icount:
            ic = int(r['count(*)'])
                
        while ic >0:
            print("Deleting indices from database")
        
            showall = session.run(
                "SHOW INDEXES")
            for record in showall:
                name = (record['name'])
                session.run("DROP INDEX {}".format(name))
            ic = 0
         
        # Setting constraints
        print("Setting constraints")

        constraints = [
                "CREATE CONSTRAINT FOR (n:Base) REQUIRE n.neo4jImportId IS UNIQUE;",
                "CREATE CONSTRAINT FOR (n:Domain) REQUIRE n.neo4jImportId IS UNIQUE;",
                "CREATE CONSTRAINT FOR (n:Computer) REQUIRE n.neo4jImportId IS UNIQUE;",
                "CREATE CONSTRAINT FOR (n:User) REQUIRE n.neo4jImportId IS UNIQUE;",
                "CREATE CONSTRAINT FOR (n:OU) REQUIRE n.neo4jImportId IS UNIQUE;",
                "CREATE CONSTRAINT FOR (n:GPO) REQUIRE n.neo4jImportId IS UNIQUE;",
                "CREATE CONSTRAINT FOR (n:Compromised) REQUIRE n.neo4jImportId IS UNIQUE;",
                "CREATE CONSTRAINT FOR (n:Group) REQUIRE n.neo4jImportId IS UNIQUE;",
                "CREATE CONSTRAINT FOR (n:Container) REQUIRE n.neo4jImportId IS UNIQUE;",
        ]

        for constraint in constraints:
            try:
                session.run(constraint)
            except:
                continue
        

        session.run("match (a) -[r] -> () delete a, r")
        session.run("match (a) delete a")


    def do_cleardb(self, args):
        if not self.connected:
            print("Not connected to database. Use connect first")
            return

        print("Clearing Database")
        d = self.driver
        session = d.session()

        # Delete nodes and edges with batching into 10k objects - From DBCreator
        total = 1
        while total > 0:
            result = session.run(
                "MATCH (n) WITH n LIMIT 10000 DETACH DELETE n RETURN count(n)")
            for r in result:
                total = int(r['count(n)'])
        
        self.do_remove_constraints(session)

        session.close()

        print("DB Cleared and Schema Set")
    

    def do_setparams(self, args):
        passed = args
        if passed != "":
            try:
                json_path = passed
                self.parameters = get_parameters_from_json(json_path)
                self.parameters_json_path = json_path
                print_all_parameters(self.parameters)
                return
            except ValueError:
                pass

        json_path = self.m.input_default("Parameters JSON file", self.parameters_json_path)
        self.parameters = get_parameters_from_json(json_path)
        if self.parameters == DEFAULT_CONFIGURATIONS:
            self.parameters_json_path = "DEFAULT"
        else:
            self.parameters_json_path = json_path

        print_all_parameters(self.parameters)


    def test_db_conn(self):
        self.connected = False
        if self.driver is not None:
            self.driver.close()
        try:
            self.driver = GraphDatabase.driver(
                self.url, auth=(self.username, self.password), encrypted=self.use_encryption)
            self.connected = True
            print("Database Connection Successful!")
        except:
            self.connected = False
            print("Database Connection Failed. Check your settings.")

    def do_generate(self, args):
        
        print(self.level)
        passed = args
        if passed != "":
            try:
                self.json_file_name = passed
            except ValueError:
                self.json_file_name = None

        self.test_db_conn()
        self.do_cleardb("a")
        reset_DB()
        
        self.generate_data()
        self.old_domain = self.domain


    def generate_data(self):
        start_ = timer()
        seed_number = get_single_int_param_value("seed", self.parameters)
        if seed_number > 0:
            random.seed()
        if not self.connected:
            print("Not connected to database. Use connect first")
            return
        
        domain_dn = get_domain_dn(self.domain)

        nTiers = get_num_tiers(self.parameters)

        # RIDs below 1000 are used for default principals.
        # RIDs of other objects should start from 1000.
        # Idea Ref: DBCreator and https://www.itprotoday.com/security/q-what-are-exact-roles-windows-accounts-sid-and-more-specifically-its-rid-windows-security
        ridcount.extend([1000])  

        computers = []
        
        users = []

        convert_to_digraph = get_single_int_param_value("convert_to_directed_graphs", self.parameters)
        
        session = self.driver.session()

        print(f"Initiating the Active Directory Domain - {self.domain}")
        functional_level = create_domain(self.domain, self.base_sid, domain_dn, self.parameters) # Ref: ADSimulator, DBCreator
        
        print("Building the fundamental framework of a tiered Active Directory model")
        create_ad_skeleton(self.domain, self.base_sid, self.parameters, nTiers)

        # -------------------------------------------------------------
        # Active Directory Default OUs, Groups and GPOs
        # Ref: DBCreator and ADSimulator have produced some default AD objects and relationships in their code
        # Utilising Microsoft documentation as a knowledge base, I migrated their codes into ADSynth built-in database.
        
        print("Creating the default domain groups")
        create_default_groups(self.domain, self.base_sid, self.old_domain) # Ref: ADSimulator, DBCreator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
        
        print("Creating the admin groups")
        create_admin_groups(self.domain, self.base_sid, nTiers)
        
        ddp = cs(str(uuid.uuid4()), self.base_sid).upper()
        ddcp = cs(str(uuid.uuid4()), self.base_sid).upper()
        dcou = cs(str(uuid.uuid4()), self.base_sid).upper()
        gpos_container = cs(str(uuid.uuid4()), self.base_sid).upper()

        print("Creating GPOs container")
        create_gpos_container(self.domain, domain_dn, gpos_container)
        
        print("Creating default GPOs")
        create_default_gpos(self.domain, domain_dn, ddp, ddcp) # Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-gpod/566e983e-3b72-4b2d-9063-a00ebc9514fd

        print("Creating Domain Controllers OU")
        create_domain_controllers_ou(self.domain, domain_dn, dcou) # Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/delegating-administration-of-default-containers-and-ous

        print("Applying Default GPOs")
        apply_default_gpos(self.domain, ddp, ddcp, dcou) # Ref: DBCreator, ADSimulator

        
        # ENTERPRISE ADMINS
        # Adding Ent Admins -> High Value Targets
        print("Creating Enterprise Admins ACLs")
        create_enterprise_admins_acls(self.domain) # Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups


        # ADMINISTRATORS
        # Adding Administrators -> High Value Targets
        print("Creating Administrators ACLs")
        create_administrators_acls(self.domain) # Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups


        # DOMAIN ADMINS
        # Adding Domain Admins -> High Value Targets
        print("Creating Domain Admins ACLs")
        create_domain_admins_acls(self.domain) # Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups


        # DC Groups
        # Extra ENTERPRISE READ-ONLY DOMAIN CONTROLLERS
        print("Generating DC groups ACLs")
        create_default_dc_groups_acls(self.domain) # Ref: DBCreator, ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups

        # DOMAIN CONTROLLERS
        # Ref: ADSimulator, DBCreator and Microsoft, https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-authsod/c4012a57-16a9-42eb-8f64-aa9e04698dca
        print("Creating Domain Controllers")
        dc_properties_list, domain_controllers = generate_dcs(self.domain, self.base_sid, domain_dn, dcou, self.current_time, self.parameters, functional_level) # O(1)

        # -------------------------------------------------------------
        # GPOs - Creating GPOs for the root OUs in a Tier Model
        print("Applying GPOs to critical OUs and tiers")
        apply_gpos(self.domain, self.base_sid, nTiers) # Ref: Russell Smith, https://petri.com/keep-active-directory-secure-using-privileged-access-workstations/, https://volkandemirci.org/2022/01/17/privileged-access-workstations-kurulumu-ve-yapilandirilmasi-2/
        

        # Impose restriction on non-privileged OU
        apply_restriction_gpos(self.domain, self.base_sid, self.parameters)


        # Place all GPOs in the GPOs container
        place_gpos_in_container(self.domain, gpos_container)
            
        # -------------------------------------------------------------
        # DEFAULT USERS and group relationships
        # Ref: ADSimulator produced these in their code
        # Utilising Microsoft documentation as a knowledge base, I migrated their code into ADSynth built-in database.
        # https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts
        print("Generating default users")
        generate_guest_user(self.domain, self.base_sid, self.parameters)
        generate_default_account(self.domain, self.base_sid, self.parameters)
        generate_administrator(self.domain, self.base_sid, self.parameters)
        generate_krbtgt_user(self.domain, self.base_sid, self.parameters)
        link_default_users_to_domain(self.domain, self.base_sid)
        
        # Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts
        print("Creating ACLs for default users")
        create_default_users_acls(self.domain, self.base_sid)

        # Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
        # Adminstrator account is Member of High value groups
        print("Creating memberships for Administrator group")
        create_adminstrator_memberships(self.domain)

        # Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
        print("Assigning members to default groups")
        generate_default_member_of(self.domain, self.base_sid, self.old_domain)

        # Ref: ADSimulator and Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-b--privileged-accounts-and-groups-in-active-directory
        print("Creating ACLs for default groups")
        create_default_groups_acls(self.domain, self.base_sid)


        # -------------------------------------------------------------
        # Creating users
        num_users = get_int_param_value("User", "nUsers", self.parameters)
        print(f"Creating {num_users} users")

        # Get a list of enabled and disabled users
        users, disabled_users = generate_users(self.domain, self.base_sid, num_users, self.current_time, self.first_names, self.last_names, self.parameters) # Ref: ADSimulator, DBCreator

        # Segragate admin and regular users
        perc_admin = get_perc_param_value("Admin", "Admin_Percentage", self.parameters)
        all_admins, all_enabled_users = segregate_list(users, [perc_admin, 100 - perc_admin])

        # Segregate admins and misconfigured admins in regular Users OU
        misconfig_admin_regular_perc = get_perc_param_value("nodeMisconfig", "admin_regular", self.parameters)
        if misconfig_admin_regular_perc > 50:
            misconfig_admin_regular_perc = DEFAULT_CONFIGURATIONS["nodeMisconfig"]["admin_regular"]
        admin, misconfig_admin = segregate_list(all_admins, [100 - misconfig_admin_regular_perc, misconfig_admin_regular_perc])

        # Segregate regular users, misconfigured users in Admin OU and in Computers OU
        misconfig_user_comp_perc = get_perc_param_value("nodeMisconfig", "user_comp", self.parameters)
        if misconfig_admin_regular_perc + misconfig_user_comp_perc > 50:
            misconfig_admin_regular_perc = DEFAULT_CONFIGURATIONS["nodeMisconfig"]["admin_regular"]
            misconfig_user_comp_perc = DEFAULT_CONFIGURATIONS["nodeMisconfig"]["user_comp"]
        enabled_users, misconfig_regular_users, misconfig_users_comps = \
            segregate_list(all_enabled_users, [100 - misconfig_admin_regular_perc - misconfig_user_comp_perc, misconfig_admin_regular_perc, misconfig_user_comp_perc])
 

        # -------------------------------------------------------------
        # Creating COMPUTERS
        num_computers = get_int_param_value("Computer", "nComputers", self.parameters)
        print("Generating", str(num_computers), "computers")

        # Ref: ADSimulator, DBCreator, BadBlood
        #      Microsoft, https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-devices
        computers, PAW, Servers, Workstations = generate_computers(self.domain, self.base_sid, num_computers, computers, self.current_time, self.parameters)

        Workstations, misconfig_workstations = segregate_list(Workstations, [100 - misconfig_user_comp_perc, misconfig_user_comp_perc])
        place_computers_in_tiers(self.domain, self.base_sid, nTiers, self.parameters, PAW, Servers, Workstations, misconfig_users_comps)

        
        # -------------------------------------------------------------
        # Admin Users
        print("Allocate Admin Users to tiers")

        # Retrieve members of server operators and print operators
        # to later generate sessions on Domain Controllers
        server_operators = [] # Server Operators 
        print_operators = []  # Print Operators 
        
        place_admin_users_in_tiers(self.domain, self.base_sid, nTiers, admin, misconfig_regular_users, server_operators, print_operators, self.parameters)
        
        # Non-admin Users
        print("Allocate non-admin users to tiers")
        place_normal_users_in_tiers(self.domain, enabled_users, disabled_users, misconfig_admin, misconfig_workstations, nTiers)


        # -------------------------------------------------------------
        # Creating GROUPS
        print("Creating distribution groups and security groups")
        num_regular_groups = create_groups(self.domain, self.base_sid, self.parameters, nTiers)
        
        print("Nesting groups")
        nest_groups(self.domain, self.parameters) # Ref: DBCreator and ADSimulator

        # Adding Users to Groups
        # Admin users have been place into admistrative tiers. Now comes the normal users
        print("Adding users to groups")
        it_users = place_users_in_groups(self.domain, nTiers, self.parameters)


        # -------------------------------------------------------------
        print("Generate sessions")
        create_sessions(nTiers, PAW_TIERS, S_TIERS, WS_TIERS, self.parameters)
        
        print("Generate cross-tier sessions")
        create_misconfig_sessions(nTiers, self.level, self.parameters, len(enabled_users) + len(admin))

        # Print Operators and Server Operators can log into Domain Controllers
        # Idea Ref: Microsoft, https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
        print("Print Operators and Server Operators can log into Domain Controllers")
        create_dc_sessions(domain_controllers, server_operators, print_operators) # O(num of Domain Controllers)
    
        
        # -------------------------------------------------------------
        # Generate non-ACL Permissions
        print("Generating non-ACL permissions")
        create_control_management_permissions(self.domain, nTiers, False, self.parameters, convert_to_digraph)
        
        print("Generating misconfigured non-ACL permissions on individuals")
        create_misconfig_permissions_on_individuals(nTiers, ADMIN_USERS, ENABLED_USERS, self.level, self.parameters, len(enabled_users) + len(admin))
        
        print("Generating misconfigured permissions on sets - From groups to OUs")
        num_local_admin_groups = sum(len(subarray) for subarray in LOCAL_ADMINS)
        create_misconfig_permissions_on_groups(self.domain, nTiers, self.level, self.parameters, num_local_admin_groups)     

        print("Generating misconfigured membership - Group Nesting")
        create_misconfig_group_nesting(self.domain, nTiers, self.level, self.parameters, num_regular_groups)

        # -------------------------------------------------------------
        #  Generate ACL Permissions, including genericall, genericwrite, writeowner, ....
        print("Creating ACLs permissions")
        create_control_management_permissions(self.domain, nTiers, True, self.parameters, convert_to_digraph)

        # -------------------------------------------------------------
        print("Adding Admin rights")
        assign_administration_to_admin_principals(self.domain, nTiers, convert_to_digraph)
        
        print("Adding Local Admin rights")
        assign_local_admin_rights(self.domain, nTiers, self.parameters, convert_to_digraph) 

        
        # -------------------------------------------------------------
        # Default ACLs
        # Ref: ADSimulator
        create_default_AllExtendedRights(self.domain, nTiers, convert_to_digraph) # Ref: ADSimulator 
        create_default_GenericWrite(self.domain, nTiers, self.parameters, convert_to_digraph) # Ref: ADSimulator
        create_default_owns(self.domain, convert_to_digraph) # Ref: ADSimulator
        create_default_write_dacl_owner(self.domain, nTiers, self.parameters, convert_to_digraph) # Ref: ADSimulator
        create_default_GenericAll(self.domain, nTiers, self.parameters, convert_to_digraph) # Ref: ADSimulator

        
        # -------------------------------------------------------------
        # Kerberoastable users
        print("Creating Kerberoastable users")
        create_kerberoastable_users(nTiers, self.parameters) # O(nUsers * perc of Kerberoastable)
        
        num_nodes = len(NODES)
        num_edges = len(dict_edges)
        print("Num of nodes = ", len(NODES))
        print("Num of edges = ", len(dict_edges))

        try:
            print("Graph density = ", round(num_edges / (num_nodes * (num_nodes - 1)), 5))
        except:
            pass

        for i in NODE_GROUPS:
            print("Number of ", i, " = ", len(NODE_GROUPS[i]))
        
        perc_misconfig_sessions = get_perc_param_value("perc_misconfig_sessions", "Low", self.parameters) / 100
        num_misconfig = int(perc_misconfig_sessions * (len(enabled_users) + len(admin)))
        print(f"Number of regular users = {len(enabled_users) + len(admin)} --- Num misconfig sessions = {num_misconfig}")

        perc_misconfig_permissions = get_perc_param_value("perc_misconfig_permissions", "Low", self.parameters) / 100
        num_misconfig = int(perc_misconfig_permissions * (len(enabled_users) + len(admin)))
        print(f"Number of regular users = {len(enabled_users) + len(admin)} --- Num misconfig permissions = {num_misconfig}")

        print("Dump to JSON file")
        current_datetime = datetime.now()
        # Format the date and time to include seconds
        filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        with open(f"generated_datasets/{filename}.json", "w") as f:
            for obj in NODES:
                obj["type"] = "node"
                # Use json.dumps() to convert the object to a JSON string without square brackets
                json_str = json.dumps(obj, separators=(',', ':'))
                # Write the JSON string to the file with a newline character
                f.write(json_str + '\n')

        # Open the file in append mode
        with open(f"generated_datasets/{filename}.json", 'a') as f:
            for obj in EDGES:
                # Use json.dumps() to convert the object to a JSON string without square brackets
                json_str = json.dumps(obj, separators=(',', ':'))
                # Write the JSON string to the file with a newline character
                f.write(json_str + '\n')
        # ===============================================
        
        end_ = timer()
        print("Execution time = ", end_ - start_)

        path = f"{os.getcwd()}/generated_datasets/{filename}.json"
        query = f"PROFILE CALL apoc.periodic.iterate(\"CALL apoc.import.json('{path}')\", \"RETURN 1\", {{batchSize:1000}})"
        # session.run(query)
        session.close()

        print("Database Generation Finished!")


    def write_json(self, session):
        json_path = os.getcwd() + "/" + self.json_file_name
        query = "CALL apoc.export.json.all('" + json_path + "',{useTypes:true})"
        session.run(query)
        print("Graph exported in", json_path)



    def do_graph(self, args):
        passed = args
        data =[]
        if passed != "":
            try:
                json_path = passed
                with open(json_path, 'r') as file:
                    for line in file:
                        json_data = json.loads(line)
                        data.append(json_data)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
        
        nodes = []
        for i in data:
            if i['type']=='node':
                nodes.append(i)

        class Nodes():
            def __init__(self, ID:str, labels:list, properties:dict):
                self.id = ID
                self.labels = labels
                self.properties = properties
                self.name = self.properties['name']

        n_dict = {}
        for i in nodes:
            n_dict[i['id']] = Nodes(i['id'],i['labels'],i['properties'])

        cluster_relation = []
        edges = []
        member_relation = []
        session_relation = []

        for i in data:
            if i['type']=='relationship':
                if i['label']=='Contains':
                    if ('Container' in i['start']['labels']) and ('Container' not in i['end']['labels']):
                        #cluster_relation.append(i)
                        pass
                    elif ('OU' in i['start']['labels']) and ('OU' not in i['end']['labels']):
                        cluster_relation.append(i)
                    else:
                        edges.append(i)
                
                elif i['label']=='MemberOf':
                    member_relation.append(i)
        
                elif i['label']=='HasSession':
                    session_relation.append(i)
        
                else:
                    edges.append(i)
        
        cluster ={}
        for i in cluster_relation:
            if i['start']['id'] not in cluster.keys():
                cluster[i['start']['id']] = list([i['end']['id']])
            else:
                cluster[i['start']['id']].append(i['end']['id'])

        edges_pair ={}
        edges_filtered =[]

        for e in edges:
            if e['label']=='Contains':
                if e['end']['id'] not in edges_pair.keys():
                    edges_pair[e['end']['id']] = list([e['start']['id']])
                    edges_filtered.append(e)
                elif e['end']['id'] in edges_pair.keys() and e['start']['id'] not in edges_pair[e['end']['id']]:
                    edges_pair[e['end']['id']].append(e['start']['id'])
                    edges_filtered.append(e)
                else:
                    pass
            else:
                if e['start']['id'] not in edges_pair.keys():
                    edges_pair[e['start']['id']] = list([e['end']['id']])
                    edges_filtered.append(e)
                elif e['start']['id'] in edges_pair.keys() and e['end']['id'] not in edges_pair[e['start']['id']]:
                    edges_pair[e['start']['id']].append(e['end']['id'])
                    edges_filtered.append(e)
                else:
                    pass

        ##create dot file
        dot_string = ['digraph {',
                      '  compound=true;',
                      '  overlap = false;', #overlap = scale
                      '  splines=true;',
                      '  rankdir=LR;'] #layout=neato;rankdir=LR;

        ##create nodes from n_dict
        for node in n_dict.values():
            if "Compromised" in node.labels:
                dot_string.append(f'  "{node.id}" [style=filled, fillcolor=red, label="{node.name}"];')
            elif "OU" in node.labels:
                dot_string.append(f'  "{node.id}" [style=filled, fillcolor=pink, label="{node.name}"];')
            elif "GPO" in node.labels:
                dot_string.append(f'  "{node.id}" [style=filled, fillcolor=lightgreen, label="{node.name}"];')
            elif "User" in node.labels:
                dot_string.append(f'  "{node.id}" [style=filled, fillcolor=violet, label="{node.name}"];')
            elif "Group" in node.labels:
                dot_string.append(f'  "{node.id}" [style=filled, fillcolor=yellow, label="{node.name}"];')
            elif "Domain" in node.labels:
                dot_string.append(f'  "{node.id}" [style=filled, fillcolor=gold, label="{node.name}"];')
            else:
                dot_string.append(f'  "{node.id}" [label="{node.name}"];')


        ##create cluster for set
        for s in cluster.items():
            dot_string.append(f'  subgraph cluster_{s[0]} '"{")
            dot_string.append(f'  style=filled;')
            dot_string.append(f'  color=lightblue;')
            dot_string.append(f'  pencolor=blue;')
            nod = ""
            for n in s[1]:
                nod += '"'
                nod += n      
                nod += '" '
            dot_string.append(f'  {nod};')
            dot_string.append("  }")
            pt_cluster = ""
            pt_cluster += s[1][0]
            #dot_string.append(f'  "{pt_cluster}" -> "{s[0]}" [ltail=cluster_{s[0]}, label="Contains_in", color=blue];')
            dot_string.append(f'  "{s[0]}" -> "{pt_cluster}" [lhead=cluster_{s[0]}, label="Contains", color=blue];')
    
        ##create edges from edges
        for e in edges_filtered:
            #if e['label']=='Contains':
            #    dot_string.append(f'  "{e["end"]["id"]}" -> "{e["start"]["id"]}" [label="Contains_in"];')
            #else:
            #    dot_string.append(f'  "{e["start"]["id"]}" -> "{e["end"]["id"]}" [label="{e["label"]}"];')
            dot_string.append(f'  "{e["start"]["id"]}" -> "{e["end"]["id"]}" [label="{e["label"]}"];')

        dot_string.append('}')


        folder = 'generated_graphs'
        # Check if the folder exists, and create it if it doesn't
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        print("Dump to dot file")
        filename = 'metagraph_wip'
        with open(f"generated_graphs/{filename}.gv", 'w') as file:
            for line in dot_string:
                file.write(line+'\n')
        
        from graphviz import Source

        with open(f"generated_graphs/{filename}.gv", 'r') as file:
            dot_contents = file.read()
    
        graph = Source(dot_contents)
        outpath = f"generated_graphs/{filename}.pdf"
        graph.render(outfile = outpath)
        print("Graph generation success")

        with open(f"generated_graphs/{filename}_membership.txt", 'w') as file:
            for line in member_relation:
                file.write(str(line)+'\n')
        



