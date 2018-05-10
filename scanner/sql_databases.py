def get_sql_servers(sql_servers_path):
    sql_servers = !az sql server list
    sql_servers = yaml.load(sql_servers.nlstr)
    with open(sql_servers_path, 'w') as f:
        yaml.dump(sql_servers, f)
    return sql_servers

def load_sql_servers(sql_servers_path):
    with open(sql_servers_path, 'r') as f:
        sql_servers = yaml.load(f)
    return sql_servers

def get_dbs(sql_servers, sql_dbs_path):
    server_dbs = {}
    for server in sql_servers:
        server_name = server['name']
        resource_group = server['resourceGroup']
        dbs = !az sql db list --resource-group $resource_group --server $server_name
        dbs = yaml.load(dbs.nlstr)
        server_dbs[(resource_group, server_name)] = dbs
        
    with open(sql_dbs_path, 'w') as f:
        yaml.dump(server_dbs, f)
    return server_dbs

def load_dbs(sql_dbs_path):
    with open(sql_dbs_path, 'r') as f:
        server_dbs = yaml.load(f)
    return server_dbs

def get_sql_policies(sql_dbs, sql_policies_path):
    """
    For each db in sql_dbs fetch the policies and write to disk
    """
    sql_policies = {}
    for (resource_group, server_name), dbs in sql_dbs.items():
        for db in dbs:
            #print(db)
            db_name = db['name']
            if db_name == 'master':
                continue
            #print('az sql db threat-policy show --resource-group {resource_group} --server {server_name} --name {db_name}'.format(resource_group=resource_group,
            #                                                                                                                    server_name=server_name,
            #                                                                                                                    db_name=db_name))
            threat_policy = !az sql db threat-policy show --resource-group {resource_group} --server {server_name} --name {db_name}
            threat_policy = yaml.load(threat_policy.nlstr)

            #print('here1')
            audit_policy = !az sql db audit-policy show --resource-group {resource_group} --server {server_name} --name {db_name}
            audit_policy = yaml.load(audit_policy.nlstr)

            #print('here2')
            tde_policy = !az sql db tde show --resource-group {resource_group} --server {server_name} --database {db_name}
            print(tde_policy)
            print(tde_policy.nlstr)
            tde_policy = yaml.load(tde_policy.nlstr)

            sql_policy = {}
            sql_policy['threat'] = threat_policy
            sql_policy['audit'] = audit_policy
            sql_policy['tde'] = tde_policy
            sql_policies[(resource_group, server_name, db_name)] = sql_policy
        
    with open(sql_policies_path, 'w') as f:
        yaml.dump(sql_policies, f)
    return sql_policies

def load_sql_policies(sql_policies_path):
    """
    Load sql policies
    """
    with open(sql_policies_path, 'r') as f:
        server_policies = yaml.load(f)
    return server_policies

################
# Tests
################

results = {}
def sql_services_tests(sql_policies):


        
    def wrap(pre, post):
        global results
        def decorate(func):
            global results
            def call(*args, **kwargs):
                global results
                pre(func, *args, **kwargs)
                result = func(*args, **kwargs)
                post(func, result, results, *args, **kwargs)
                return result
            return call
        return decorate
    


    def trace_in(func, *args, **kwargs):
        global results

    def trace_out(func, result, *args, **kwargs):
        global results
        if not result:
            pairs = results.get(func.__name__, [])
            pairs.append((resource_group, server_name, db))
            results[func.__name__] = pairs


    @wrap(trace_in, trace_out)
    def auditing_is_set_to_on_4_2_1(audit_policy):
        if audit_policy['state'] != 'Enabled':
            return False
        else:
            return True
  
    @wrap(trace_in, trace_out)
    def threat_detection_is_set_to_on_4_2_2(threat_policy):
        if threat_policy['state'] != 'Enabled':
            return False
        else:
            return True
        
    @wrap(trace_in, trace_out)
    def threat_detection_types_is_set_to_all_4_2_3(threat_policy):
        if threat_policy['disabledAlerts'] in ['All', '']:
            return True
        else:
            print('threat_detection_types_is_set_to_all_4_2_3 disabledAlerts', threat_policy['disabledAlerts'])
            return False
        
    @wrap(trace_in, trace_out)
    def send_alerts_to_is_set_4_2_4(threat_policy):
        if threat_policy['emailAddresses']:
            print('send_alerts_to_is_set_4_2_4 emailAddresses', threat_policy['emailAddresses'])
            return set(threat_policy['emailAddresses'])
        else:
            return False
        
    @wrap(trace_in, trace_out)
    def email_service_and_co_administrators_is_enabled_4_2_5(threat_policy):
        if threat_policy['emailAccountAdmins'] != "Enabled":
            return False
        else:
            return True
        
#         email_service_and_co_administrators_is_enabled_failed_list.append(db_name)
#         email_service_and_co_administrators_is_enabled_failed_count += len(no_email_enabled_list)
#         email_service_and_co_administrators_is_enabled_failed[(resource_group, server_name)] = no_email_enabled_list
        
#         stats['email_service_and_co_administrators_is_enabled_failed_count'] = email_service_and_co_administrators_is_enabled_failed_count
#         return no_email_enabled, stats
        
    
    @wrap(trace_in, trace_out)
    def data_encryption_is_set_to_on_4_2_6(tde_policy):
        if tde_policy['status'] != "Enabled":
            return False
        else:
            return True

    @wrap(trace_in, trace_out)
    def auditing_retention_is_greater_than_90_days_4_2_7(audit_policy):
        if audit_policy['retentionDays'] <= 90:
            return False
        else:
            return True

    @wrap(trace_in, trace_out)
    def threat_retention_is_greater_than_90_days_4_2_8(threat_policy):
        if audit_policy['retentionDays'] <= 90:
            return False
        else:
            return True
        
    sql_dbs = {}
    stats = {}
    
    count = 0
    for (resource_group, server_name, db), sql_policies in sql_policies.items():
        
        audit_policy = sql_policies['audit']
        threat_policy = sql_policies['threat']
        tde_policy = sql_policies['tde']            
        
        auditing_is_set_to_on_4_2_1(audit_policy)
        threat_detection_is_set_to_on_4_2_2(threat_policy)
        threat_detection_types_is_set_to_all_4_2_3(threat_policy)
        send_alerts_to_is_set_4_2_4(threat_policy)
        email_service_and_co_administrators_is_enabled_4_2_5(threat_policy)
        data_encryption_is_set_to_on_4_2_6(tde_policy)
        auditing_retention_is_greater_than_90_days_4_2_7(audit_policy)
        threat_retention_is_greater_than_90_days_4_2_8(threat_policy)

    return results

def get_data():
    sql_servers_path = os.path.join(raw_data_dir, 'sql_servers.json')
    get_sql_servers(sql_servers_path)
    sql_servers = load_sql_servers(sql_servers_path)
    
    sql_dbs_path = os.path.join(raw_data_dir, 'sql_dbs.json')
    get_dbs(sql_servers, sql_dbs_path)
    
    sql_policies_path = os.path.join(raw_data_dir, 'sql_policies.json')
    get_sql_policies(sql_dbs, sql_policies_path)

    return {"sql_servers": sql_servers, "sql_databases": sql_dbs, "sql_policies": sql_policies}

def run_tests():
    sql_results = sql_services_tests(sql_policies)
    return sql_results