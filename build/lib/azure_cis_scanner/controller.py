from azure_cis_scanner import utils
import argparse
import os
import subprocess
import time
from importlib.util import spec_from_file_location, module_from_spec
from os.path import splitext, basename

from azure.common.client_factory import get_client_from_cli_profile, get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient

def loadModule(moduleName, **kwargs):
    name = splitext(basename(moduleName))[0]
    print(name)
    spec = spec_from_file_location(name, moduleName)
    module = module_from_spec(spec)
    module.config = kwargs
    spec.loader.exec_module(module)
    return module

def dprint(thing):
    print(str(thing))
    print(thing)


def ddprint(thing):
    dprint(thing)
    print(type(thing))
    print(dir(thing))

MODULES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules')

def _get_modules(modules):
    if modules:
        return modules
    else:
        return [x for x in os.listdir(MODULES_PATH) if x.endswith('.py')]
    
def _get_data(config):
    raw_data_dir, filtered_data_dir = config['raw_data_dir'], config['filtered_data_dir']
    modules = _get_modules(config['modules'])
    for module in modules:
        print('Getting data for {}'.format(module.strip('.py')))
        module_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules', module)
        try:
            mod = loadModule(module_path, **dict(raw_data_dir=raw_data_dir, filtered_data_dir=filtered_data_dir))
            mod.get_data()
        except Exception as e:
            print("Exception was thrown! Unable to run get_data() for {}".format(module))
            print("Module path {}".format(module_path))
            print(e)

def _test_controls(config):
    raw_data_dir, filtered_data_dir = config['raw_data_dir'], config['filtered_data_dir']
    modules = _get_modules(config['modules'])
    for module in modules:
        print('Testing controls for {}'.format(module.strip('.py')))
        module_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules', module)
        try:
            mod = loadModule(module_path, **dict(raw_data_dir=raw_data_dir, filtered_data_dir=filtered_data_dir))
            mod.test_controls()
        except Exception as e:
            print("Exception was thrown! Unable to run test_controls() for {}".format(module))
            print(e)



def main():
    mainparser = argparse.ArgumentParser()
    mainparser.add_argument('--subscription-id', default=None, help='azure subscription id')
    # TODO, set default in __init__.py or somewhere and make it windows compatible
    mainparser.add_argument('--scans-dir', default='~/engagements/cis_test', help='base dir of where to place or load files')
    mainparser.add_argument('--stages', default='data,test,report', help='comma separated list of steps to run in data,test,render')
    mainparser.add_argument('--modules', default=None, help='comma separated list of module names e.g. security_center')

    parser = mainparser.parse_args()

    print("Checking to see if there is an Azure account associated with this session.")

    account_list = utils.call("az account list")

    scans_dir = parser.scans_dir

    if parser.subscription_id:
        if utils.verify_subscription_id_format(parser.subscription):
            subscription_id = parser.subscription_id
            try:
                account = utils.call("az account set --subscription subscription_id")
            except:
                raise ValueError("Unable to set subscription {}".format(subscription_id))
        else:
            raise ValueError("supplied subscription id '{}' is invalid".format(parser.subscription_id))
    else:
        try:
            account = utils.get_active_account()
        except:
            print("No Azure account associated with this session. Please authenticate to continue.")
            utils.call("az login")
            account = utils.get_active_account()
            print("Pausing for 5 seconds")
            subscription_id = account['id']
            subscription_name = account['name']
            print("Using current subscription_id {} {}".format(subscription_id, subscription_name))
            print("Re-run with --subscription-id if you wish to change")
            time.sleep(5)
    subscription_id = account['id']
    subscription_name = account['name']
    # create a part-friendly/part-uniquie-id name
    access_token, token_expiry = utils.get_access_token()
    subscription_dirname = subscription_name.split(' ')[0] + '-' + subscription_id.split('-')[0]
    scan_data_dir, raw_data_dir, filtered_data_dir = utils.set_data_paths(subscription_dirname, scans_dir)

    modules = parser.modules
    if modules:
        modules = modules.split(',')
    config = dict(raw_data_dir=raw_data_dir, filtered_data_dir=filtered_data_dir, modules=modules )

    stages = parser.stages.split(',')

    if 'data' in stages:
        _get_data(config)
    if 'test' in stages:
        print('test', config)
        _test_controls(config)
    if 'report' in stages:
        report_path = os.path.join( os.path.dirname(__file__), '../', 'report')
        subprocess.Popen("flask app.py", cwd=report_path)


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
