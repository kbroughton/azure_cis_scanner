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

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


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
    all_modules = [x for x in os.listdir(MODULES_PATH) if x.endswith('.py') and x != '__init__.py']
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
            mod.test_controls()
        except Exception as e:
            print("Exception was thrown! Unable to run test_controls() for {}".format(module))
            print("Module path {}".format(module_path))
            print(e)
            print(traceback.format_exc())


def main():
    mainparser = argparse.ArgumentParser()
    mainparser.add_argument('--tenant-id', default=None, help='azure tenant id, if None, use default.  Scanner assumes different runs/project dirs for distinct tenants')
    mainparser.add_argument('--subscription-id', default=None, help='azure subscription id, if None, use default, if "all" use all subscriptions with default tenant')
    # TODO, set default in __init__.py or somewhere and make it windows compatible
    mainparser.add_argument('--scans-dir', default='/engagements/cis_test/scans', help='existing base dir of where to place or load files')
    mainparser.add_argument('--stages', default='data,test,report', help='comma separated list of steps to run in [data,test,report]')
    mainparser.add_argument('--modules', default=None, help='comma separated list of module names e.g. security_center.py')
    mainparser.add_argument('--skip-modules', default=[], help='comma separated list of module names to skip')
    mainparser.add_argument('--use-api-for-auth', default=True, help='if false, use azure cli calling subprocess, else use python-azure-sdk')
    mainparser.add_argument('--refresh-sp-credentials', action='store_true', help='refresh service principal creds needed for keyvault')
    mainparser.add_argument('--loglevel', default='info', help='loglevel in ["debug", "info", "warning", "error"]')
    mainparser.add_argument('--example-scan', action='store_true', help='allow running without credentials on example_scan data')
    parser = mainparser.parse_args()

    loglevel = parser.loglevel

    if loglevel != 'info':
        print("Checking to see if there is an Azure account associated with this session.")
        print("Running with arguments {}".format(parser))

    if loglevel == "debug":
        logger.setLevel(logging.DEBUG)
    elif loglevel == "info":
        logger.setLevel(logging.INFO)
    elif loglevel == "warning":
        logger.setLevel(logging.INFO)
    elif loglevel == "error":
        logger.setLevel(logging.ERROR)


    credentials_tuples = utils.set_credentials_tuples(parser)

    scans_dir = os.path.realpath(parser.scans_dir)
    scans_dir = utils.set_scans_dir(scans_dir)

    stages = parser.stages.split(',')


    for tenant_id, subscription_id, subscription_name, credentials in credentials_tuples:

        sp_credentials = None

        if parser.example_scan:
            stages = ['report']
        else:
            try:
                sp_credentials = utils.get_service_principal_credentials(subscription_id, auth_type='sdk', refresh_sp_credentials=parser.refresh_sp_credentials)
                print("sp_credentials", sp_credentials, type(sp_credentials))
                logger.debug("DEBUGGER WORKS! running stages for {} {} {}".format(tenant_id, subscription_id, subscription_name))
                print("running stages for {} {} {}".format(tenant_id, subscription_id, subscription_name))
            except Exception as e:
                logger.warning("Cannot get service principal credentials.  Python SDK auth will not be available")
                logger.warning(traceback.format_exc())

            access_token, token_expiry = utils.get_access_token()
            # create a part-friendly/part-uniquie-id name
        subscription_dirname = utils.get_subscription_dirname(subscription_id, subscription_name)

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
        if not parser.example_scan:
            resource_groups_path = os.path.join(raw_data_dir, "resource_groups.json")
            rm_client = ResourceManagementClient(credentials, subscription_id)
            resource_groups = get_resource_groups(rm_client, subscription_id, resource_groups_path)

        if 'data' in stages:
            _get_data(config)
        if 'test' in stages:
            print('test', config)
            _test_controls(config)
        if 'report' in stages:
            from azure_cis_scanner.report import app
            app.main(parser=parser)

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
