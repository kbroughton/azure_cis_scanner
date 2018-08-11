from azure_cis_scanner import utils
from azure_cis_scanner.utils import get_resource_groups, get_credentials_from_cli
import argparse
import logging
import json
import os
import subprocess
import traceback
import time
from importlib.util import spec_from_file_location, module_from_spec
from os.path import splitext, basename


from azure.common.client_factory import get_client_from_cli_profile, get_client_from_auth_file
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient

_LOGGER = logging.getLogger(__name__)
print(_LOGGER)

def load_module(module_name, **kwargs):
    name = splitext(basename(module_name))[0]
    spec = spec_from_file_location(name, module_name)
    module = module_from_spec(spec)
    module.config = kwargs
    spec.loader.exec_module(module)
    return module

def dprint(*thing):
    print(str(thing))
    print(thing)


def ddprint(*thing):
    dprint(thing)
    print(type(thing))
    print(dir(thing))

MODULES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules')

def _get_modules(modules=None, skip_modules=None):
    """
    Returns specified modules, all modules or all modules - skipped modules
    """
    if modules and skip_modules:
        print("WARNING: both modules and skip_modules specified, ignoring skip_modules")
    all_modules = [x for x in os.listdir(MODULES_PATH) if x.endswith('.py')]
    if modules:
        intersect_modules = set(all_modules).intersection(set(modules))
        diff_modules = set(modules).difference(intersect_modules)
        if diff_modules:
            print("Warning, requested modules {} were not found.  Proceeding with {}".format(diff_modules, intersect_modules))
        return list(intersect_modules)
    if skip_modules:
        return list(set(all_modules).difference(set(skip_modules)))
    return all_modules
    
def _get_data(config):
    raw_data_dir, filtered_data_dir, cli_credentials, subscription_id = config['raw_data_dir'], \
        config['filtered_data_dir'], config['cli_credentials'], config['subscription_id']

    modules = _get_modules(config['modules'], config['skip_modules'])
    for module in modules:
        print('Getting data for {}'.format(module.strip('.py')))
        module_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules', module)
        try:
            # mod = load_module(module_path, **dict(raw_data_dir=raw_data_dir, 
            #                                       filtered_data_dir=filtered_data_dir, 
            #                                       cli_credentials=cli_credentials,
            #                                       subscription_id=subscription_id))
            mod = load_module(module_path, **config)

            mod.get_data()
        except Exception as e:
            print("Exception was thrown! Unable to run get_data() for {}".format(module))
            print("Module path {}".format(module_path))
            print(e)
            print(traceback.format_exc())

def _test_controls(config):
    raw_data_dir, filtered_data_dir = config['raw_data_dir'], config['filtered_data_dir']
    modules = _get_modules(config['modules'], config['skip_modules'])
    for module in modules:
        print('Testing controls for {}'.format(module.strip('.py')))
        module_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules', module)
        try:
            mod = load_module(module_path, **config)
            #mod = load_module(module_path, **dict(raw_data_dir=raw_data_dir, filtered_data_dir=filtered_data_dir))
            mod.test_controls()
        except Exception as e:
            print("Exception was thrown! Unable to run test_controls() for {}".format(module))
            print("Module path {}".format(module_path))
            print(e)
            print(traceback.format_exc())


def set_credentials_tuples(parser):

    # While we have a mixture of azcle and az-python-sdk we need to set the subscription_id 
    # both with az account set, and with subscription_client using a modified credentials.py
    use_api_for_auth = parser.use_api_for_auth

    if parser.subscription_id:
        if utils.verify_subscription_id_format(parser.subscription_id):
            subscription_id = parser.subscription_id
            try:
                if use_api_for_auth:
                    credentials_tuples = get_credentials_from_cli(subscription_id=subscription_id)
                    tenant_id, subscription_id, subscription_name, credentials = credentials_tuples[0]
                    if parser.tenant_id and (tenant_id != parser.tenant_id):
                        raise(ValueError("subscription {} does not belong to tenant {}".format(subscription_id, parser.tenant_id))) 

                else:
                    utils.call("az account set --subscription {}".format(subscription_id))
                    account = json.loads(utils.call("az account show"))
                    if parser.tenant_id:
                        if account['tenantId'] != parser.tenant_id:
                            raise(ValueError("subscription {} does not belong to tenant {}".format(subscription_id, parser.tenant_id))) 
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                raise ValueError("Unable to set or find subscription {}".format(subscription_id))
        else:
            raise ValueError("supplied subscription id '{}' is invalid".format(parser.subscription_id))
    else:
        try:
            if parser.tenant_id:
                if not use_api_for_auth:
                    raise(ValueError("use_api_for_auth=False is only supported for default tenant.  Create an issue or PR"))
                tenant_id = parser.tenant_id
                print("No subscription specified, running on all subscriptions for supplied tenant {}".format(tenant_id))
                credentials_tuples = get_credentials_from_cli(tenant_id=tenant_id)
                print(credentials_tuples)
            else:
                print("No tenant or subscription specified, getting active account")
                account = utils.get_active_account()
                print('account', account)
                subscription_id = account['id']
                credentials_tuples = get_credentials_from_cli(subscription_id=subscription_id)

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print("No Azure account associated with this session. Please authenticate to continue.")
            utils.call("az login")
            account = utils.get_active_account()

    if not use_api_for_auth:
        subscription_id = account['id']
        subscription_name = account['name']
        print("Using subscription_id {} {}".format(subscription_id, subscription_name))
        print("Re-run with --subscription-id if you wish to change")
        credentials_tuples = get_credentials_from_cli(subscription_id=subscription_id)

    return credentials_tuples


def main():
    mainparser = argparse.ArgumentParser()
    mainparser.add_argument('--tenant-id', default=None, help='azure tenant id, if None, use default.  Scanner assumes different runs/project dirs for distinct tenants')
    mainparser.add_argument('--subscription-id', default=None, help='azure subscription id, if None, use default, if "all" use all subscriptions with default tenant')
    # TODO, set default in __init__.py or somewhere and make it windows compatible
    mainparser.add_argument('--scans-dir', default='/engagements/cis_test', help='base dir of where to place or load files')
    mainparser.add_argument('--stages', default='data,test,report', help='comma separated list of steps to run in data,test')
    mainparser.add_argument('--modules', default=None, help='comma separated list of module names e.g. security_center.py')
    mainparser.add_argument('--skip-modules', default=[], help='comma separated list of module names to skip')
    mainparser.add_argument('--use-api-for-auth', default=True, help='if false, use azure cli calling subprocess, else use python-azure-sdk')
    mainparser.add_argument('--refresh-sp-credentials', action='store_true', help='refresh service principal creds needed for keyvault')
    mainparser.add_argument('--loglevel', default='info', help='loglevel in ["info", "debug", "trace"]')
    parser = mainparser.parse_args()

    loglevel = parser.loglevel

    if loglevel != 'info':
        print("Checking to see if there is an Azure account associated with this session.")
        account_list = utils.call("az account list")
        print("Running with arguments {}".format(parser))

    if True: #loglevel == "debug":
        _LOGGER.setLevel(logging.DEBUG)

    credentials_tuples = set_credentials_tuples(parser)

    for tenant_id, subscription_id, subscription_name, credentials in credentials_tuples:

        sp_credentials = utils.get_service_principal_credentials(subscription_id, auth_type='sdk', refresh_sp_credentials=parser.refresh_sp_credentials)
        print("sp_credentials", sp_credentials, type(sp_credentials))
        _LOGGER.debug("DEBUGGER WORKS! running stages for {} {} {}".format(tenant_id, subscription_id, subscription_name))
        print("running stages for {} {} {}".format(tenant_id, subscription_id, subscription_name))
        
        access_token, token_expiry = utils.get_access_token()
        # create a part-friendly/part-uniquie-id name
        subscription_dirname = subscription_name.split(' ')[0] + '-' + subscription_id.split('-')[0]
        scans_dir = parser.scans_dir
        scan_data_dir, raw_data_dir, filtered_data_dir = utils.set_data_paths(subscription_dirname, scans_dir)

        modules = parser.modules
        if modules:
            modules = modules.split(',')
        skip_modules = parser.skip_modules
        if skip_modules:
            skip_modules = skip_modules.split(',')

        config = dict(raw_data_dir=raw_data_dir, 
            filtered_data_dir=filtered_data_dir, 
            modules=modules,
            skip_modules=skip_modules,
            cli_credentials=credentials,
            sp_credentials=sp_credentials,
            subscription_id=subscription_id
            )

        ### Get some data common to most modules
        resource_groups_path = os.path.join(raw_data_dir, "resource_groups.json")
        rm_client = ResourceManagementClient(credentials, subscription_id)
        resource_groups = get_resource_groups(rm_client, subscription_id, resource_groups_path)

        stages = parser.stages.split(',')

        if 'data' in stages:
            _get_data(config)
        if 'test' in stages:
            print('test', config)
            _test_controls(config)


def az_login():
    from azure.common.client_factory import get_client_from_cli_profile
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
    from msrestazure.azure_active_directory import MSIAuthentication

    client = get_client_from_cli_profile(SubscriptionClient)
    accounts = [ x.as_dict() for x in list(client.subscriptions.list())]
    print(accounts)


if __name__ == "__main__":
    main()
