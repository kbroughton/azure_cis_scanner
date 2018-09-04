# azure_cis_scanner

[![PypI](http://img.shields.io/pypi/v/azure_cis_scanner.svg)](http://img.shields.io/pypi/v/azure_cis_scanner.svg)

Security Compliance Scanning tool using CIS Azure Benchmark 1.0

The purpose of this scanner is to assist organizations in locking down their Azure environments following best practices in the Center for Internet Security Benchmark release Feb 20, 2018.  This repo was inspired by a similar scanner for AWS called Scout2. 

Capabilities:
* scan multiple subscription_ids for a tenant
* test for most of the controls in the CIS Azure Foundation Benchmark 1.0
* save raw and filtered (non-passing) data
* render a report for viewing

## BETA NOTICE

This private beta is intended to expose the Azure CIS Scanner to a small handful of Azure security users for focused, high-quality testing and feedback to help perfect and expand on the tool's capabilities before its official release. While this will be an open source project when it's released, we ask everyone in the beta to please not share internal tool details (such as source code) until after the public release. Please do not join the beta if you can't agree to that.

This project is not yet production ready and should only be run from a local machine not exposed to untrusted networks.

## The scanner can generate reports that mirror the CIS sections.
![azure cis scanner homet](images/cis_test_vm_section.png?raw=true "Section Summary for VMs")

## This scanner also allows tracking progress over time
![Azure Storage: Secure Transfer not Enabled](images/cis_test_secure_transfer_graph.png?raw=true "Finding Detail for `Secure Transfer not Enabled`")


Raw data will have the format as returned by the Azure Api in json format.
Raw data will be per major CIS section in files based on the name.

```
Identity and Access Management       Logging and Monitoring                 
Security Center                      Networking
Storage                              Virtual Machines
SQL Services                         Other Miscellaneous Items

```

Filtered data will be in files named by the finding and have the following format
```
{
 "threat_detection_should_be_turned_on": {
	"metadata": { "columns": ['region', 'server', database' ],
                  "finding": 'threat_detection_should_be_turned_on'}
	"stats": {"items_checked": 10, "items_flagged": 4},
	"items": [
	  ('us-west-1', 'server01', 'db011')
	  ('us-west-2', 'server02', 'db021')
	  ('us-west-2', 'server02', 'db023')
	  ('us-west-2', 'server02', 'db024')
	  ]
	}
  "another_finding_in_this_section": ...
}
```

## Quickstart

### Requirements
*  All platforms require installing the [az cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) \
* Install [python3 for your platform](https://realpython.com/installing-python/). \
* see the install folder for platform specific pre-requisits

### Commandline + pip install

```
pip3 install azure-cis-scanner
azscan
open localhost:5000
```

If you only have one subscription, defaults will work.  If you have multiple
subscriptions, pass in `azscan --subscription-id aaaaa-bbbbbb-111111-444444-xxxxx`.  Run
`azscan --help` to see a list of all options.

### Install from Github
```
git clone https://github.com/praetorian-inc/azure_cis_scanner
cd azure_cis_scanner
virtualenv venv && source venv/bin/activate  # optional`
pip3 install -r requirements.txt
nbstripout --install    # allows githooks to run, strips out ipynb output from commits
python3 setup.py install
azscan 
```

If you do not have an azure account or want to try it on sample data first, run just the report on sample data from the github install
```
azscan --
```

It is possible to only run certain modules and stages
```
azscan --modules "security_center.py,storage_accounts.py" --stages "data,tests"
```

### Install with Docker

If you already have an account and the default subscription is correct,
you can just copy the docker-compose.yml file to a new folder, copy 
.env-sample to .env next to the docker-compose.yml.  Make any modifications
necessary to .env for your environment and run

```
docker-compose up
```
Then find the docker conatiner id, exec into the container and run the scanner 
```
docker ps | grep azure 
docker exec -it <id from above> bash
bash# azscan
```

This will mount ~/.azure into the container and use the default subscription.

### Known Issues
Depending on previous pip installs, you may see
```
error: PyYAML 3.12 is installed but pyyaml~=4.2b4 is required by {'azure-cli-core'}
```
This can be ignored as long as the rest of the pip install succeeds.  You may need to comment out requests from requirements.txt.

Expired tokens:
Message: The access token expiry UTC time '8/21/2018 3:22:00 PM' is earlier than current UTC time '8/21/2018 3:48:45 PM'.
This happens more often if you switch between the container and native environments.
Try the following
```
az account get-access-token
```
or
```
az login
```
Or in rare cases
```
rm ~/.azure/accessTokens.json
az login
```

Occasionally the ~/.azure/azureProfiles.json gets some non-ascii characters causing an error about unicode decoding.  
The current fix is to open the file and delete the (possiby invisible) characters inserted at the start of the file.

No Graphig:
You may see the error "Unable to import matplotlib.  No graphing available" even though matplotlib pip-installed fine.
Check the install/ directory to see if there are specific aids for your platform.  This may be an issue with virtualenvs
not finding python correctly if `import matplotlib` works outside of the virtualenv.

## Detailed Usage

```
$ azscan --help
usage: azscan [-h] [--tenant-id TENANT_ID] [--subscription-id SUBSCRIPTION_ID]
              [--scans-dir SCANS_DIR] [--stages STAGES] [--modules MODULES]
              [--skip-modules SKIP_MODULES]

optional arguments:
  -h, --help            show this help message and exit
  --tenant-id TENANT_ID
                        azure tenant id, if None, use default. Scanner assumes
                        different runs/project dirs for distinct tenants
  --subscription-id SUBSCRIPTION_ID
                        azure subscription id, if None, use default, if "all"
                        use all subscriptions with default tenant
  --scans-dir SCANS_DIR
                        existing base dir of where to place or load files
  --stages STAGES       comma separated list of steps to run in data,test
  --modules MODULES     comma separated list of module names e.g.
                        security_center.py
  --skip-modules SKIP_MODULES
                        comma separated list of module names to skip
```

Best practice is to work inside a docker container to avoid any issues that would arise from a multi-tenant environment.
If running from the native command-line, take care that multi-subscription calls like permissions.sh only see the right target
subscriptions in the `~/.azure/ directory`.  

The Dockerfile.apline container is currently a base of pshchelo/alpine-jupyter-sci-py3 with microsoft/azure-cli Dockerfile 
layered on top.  It builds an 800 Mb container. We will replace the pshchelo base with a more official (nbgallery or jupyter)
docker image and tune the image in the future.  Dockerfile is based on ubuntu / jupyter/scipy-notebook and builds a 4.5 Gb
container. 

We assume you have already created an azure account or have been granted credentials with privileges sufficient to run the scanner.
We will login once outside of the container (merges creds with anything in ~/.azure) to get the correct subscription id, and then
again inside the container to restrict ourselves to the correct creds only.

### Create service principals if using multiple subscriptions
Following the [Azure Documentation](https://docs.microsoft.com/en-us/python/azure/python-sdk-azure-authenticate?view=azure-python) create a service principal for a given subscription:

```
az ad sp create-for-rbac --name "<service-principal-name>" --password "STRONG-SECRET-PASSWORD" > ~/.azure/<service-principal-name>.json

```
where <service-principal-name> can be anything - a good choice might be
scanner-<first-digits-of-subscription> and STRONG-SECRET-PASSWORD is also
chosen randomly.

Now run the scanner providing the --auth-location
```
python3 azure_cis_scanner/controller.py --auth-location ~/.azure/<service-principal-name>.json
```

### Configure

Get the repo (until it is public)
```
$ git clone git@github.com:praetorian-inc/azure_cis_scanner.git && cd azure_cis_scanner
```

Get the repo (public)
```
$ git clone https://github.com/praetorian-inc/azure_cis_scanner.git && cd azure_cis_scanner
``` 

Copy azure_cis_scanner/.env-sample to .env.  This is a special filename that controls docker-compose and is in .gitignore.
```
azure_cis_scanner$ cp .env-sample .env
```
Edit the azure_cis_scanner/.env file as needed.
If you are going to be developing, open docker-compose.yml and uncomment the lines marked with # DEVELOPMENT MODE

### Run the container and exec into it
```
azure_cis_scanner$ docker-compose up
```
In another terminal get the container id and exec into it
```
azure_cis_scanner$ docker ps
azure_cis_scanner$ docker exec -it <container-id> /bin/bash
```

### Login inside the container
The docker-compose creates (on first run) a .azure folder to hold the creds and maps it to /root/.azure.
This allows you to stop and start the container without having to re login for the lifetime of your tokens.
```
bash-4.4$ az login
bash-4.4$ az account list
bash-4.4$ az account set --subscription <choice from above>
```

Edit report/settings.py for your active_subscription_dir.  This can be anything, but convention is the friendly name and the first 8 chars 
from the correct `id` in `account list` above. Since it is mounted into the container, it will change inside and outside the container.

### Sample deploy (optional)
If you have no resource or just want to test the scanner on fresh resources, try some of the automated deployment resources.
Currently, sample-deploy/terraform-azure is working the best.  

Install terraform, and [setup terraform to talk to azure](https://github.com/mitchellh/packer/blob/master/contrib/azure-setup.sh).

If using the container we need to add terraform to the container.
```
apk add terraform
```

For each folder, cd into it and run
```
terraform init
terraform apply
```
If you receive a token expiry error with terraform, run the following:
```
az account get-access-token
```
REMEMBER TO DESTROY YOUR RESOURCES WHEN FINISHED
```
terraform destroy
```
It is best practice to create automated billing alerts via the UI to avoid unpleasant surprises.

### Run the scanner
Change to the scanner directory inside the container and run the scanner using a run_jnb command which 
sets variables in the jupyter notebook and runs it. Alternatively, on your first run, you can use the url 
output from `docker-compose up` to login to the notebook and step through the calls.  Edit the line below
with appropriate arguments for subscription_id and base_dir.

```
bash-4.4$ cd /praetorian-tools/azure_cis_scanner/scanner
scanner$ run_jnb -a '{"subscription_id": "510f92e0-xxxx-yyyy-zzzz-095d37e6a299", "base_dir": "/engagements/cis_test"}' -v azure_cis_scanner.ipynb -t 500
```
If the terminal prompt gets messed up, try modifying the above in an editor and pasting in its entirety into the shell.
There is currently no progress report, but if you open sublime you can watch the files as they are created in base_dir.
If the files are not created as expected, search for clues in the _run_jnb output or, better, go to the jupyter notebook in your browser
and step through the cells until an error occurs.

Note that running the scanner a second time on the same day will clobber the old result.  A new folder is created when the scanner is 
run on a new day.

### Browse the report
At this point your base_dir should have been populated with files as shown below

![raw and filtered generated files](images/cis_test_azure_scanner_files.png?raw=true "Scanner Generated Files")

Inside the container we now run a flask app to server generated html pages with the reports.

```
bash-4.4 scanner$ cd ../report
bash-4.4 report$ flask app.py
```
Browse to 127.0.0.1:5000 to view the report.  The subscription switching via the UI does not work yet.

Currently, graphs will not display until there are two days of data.

If you wish to work with the scanner in an interactive jupyter notebook, open `127.0.0.1:8888` and browse to the azure_cis_scanner.ipynb file.

## Explore in jupyter notebook
A jupyter development notebook is available in your browser at localhost:5000.
If you plan to run the notebook please install [nbstripout](https://github.com/kynan/nbstripout) to ensure no sensitive information is accidentally committed to git.
```
azure_cis_scanner > pip install --upgrade nbstripout
azure_cis_scanner> nbstripout --install
```

## Security considerations

* nbstripout performs Jupyter notebook scrubbing of output cells which may contain sensitive information.  Github pre-commit webhooks perform this automatically.
* All credentials in ~/.azure are mounted into the container when using docker-compose and thus do not get baked into the container.
* A script to remove any files or folders likely to contain sensitive information
  from container in case of `docker save`.

* Github's new static scanner for python was added and [discovered some issues that were fixed](images/azure_cis_scanner_git_vuln_scan.png)! 

## Requesting credentials with the correct RBACs to run the scanner
If you need to run the scanner on someone else's Azure environment, you should ask for the minimum possible
permissions.

### Owner Generates Minimal Permissions Role Definition and Temporary Keys

The following steps should be performed by someone with Owner permissions to generate minimal creds for the tester.
Get the minimal_tester_role.json and permissions.sh scripts used to generate a custom role definition and temporary storage access keys.

```
$ git clone https://github.com/praetorian-inc/azure_cis_scanner.git

```

Fetch the official microsoft container

```
$ docker pull microsoft/azure-cli
```

If you are going to be working over many days and shutting down the container between runs, you may want to create a project-directory
.azure folder which you will mount into the container.  Persisting creds with local mount  `-v .azure/:~/.azure` is optional.

```
$ cd /path/to/working-project
$ cp /path/to/azure_cis_scanner/{permissions.sh,minimal_tester_role.sh} .
working-project$ docker --rm run -it -v .azure/:~/.azure -v .:/workdir
bash-4.3#
```

We are now inside the container at the bash-4.3# prompt.  Time to log in.

```
bash-4.3# az login
```
Complete sign-in via the web UI login.

Modify minimal_tester_role.json with the correct subscription(s)

Modify the permissions.sh with positional variables $1=start_date, $2=end_date, $3=ip_whitelist for the generated storage keys

```
bash-4.3# /workdir/permissions.sh
```

The script creates a AzureSecurityScanner role definition.  The Owner now associates that role to the 
users and can copy the generated (resource_group, account, SAS keys) tuples and send them securely to the pen-tester.

## Constraints

An attempt was made to convert to json everywhere, but the current raw/filtered data used key tuples - eg (resource_group, server, database) -
which are only supported in yaml.  An attempt to use safe_yaml was made, but the tuples caused errors.  The intention is to have `raw` data pulled
as infrequently as possible from the cloud API, and stored as close as possible to the delivered format.  
We may switch from tuple to nested dict in the future.

## Roadmap

* ~~Further development of automation for deployment of an insecure test environment.~~
* Add to remediation scripts in the `remediations` folder to automatically resolve many simple "switch on" issues.
* Use the python sdk instead of bash.  This was attempted but the sdk has multiple auth strategies and isn't well documented.
* Wrap the flask project with praetorian-flask for security.  Only run on a local network until this is complete or switch to django.
* Remove manual steps by generating minimal_tester_role.json with correct subscriptions/resource_group paths.
* The container is currently a base of pshchelo/alpine-jupyter-sci-py3 with microsoft/azure-cli Dockerfile layered on top.
* Replace the pshchelo base with a more official (nbgallery or jupyter) docker image and tune the image in the future.
* ~~Add git hooks to automatically remove cell output of azure_cis_scanner.ipynb to avoid checking in sensitive info~~
* Update to CIS Azure Foundation Benchmark 1.1 - currently in development

## Contributing 
az_scanner uses the python-azure-sdk.  There are a few limitations compared to the azure cli.
Some good resources are: 
*[Azure Samples](https://github.com/Azure-Samples?utf8=%E2%9C%93&q=python&type=&language=)

Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Digging Deeper

A Scanner is a good first tool for securing a cloud environment to ensure best practices and secure configuration settings are employed.
However, this scanner does not assess the health of your IAM policies and roles or network security groups beyond some basic known-bad settings.  Azure is constantly evolving and part of the challenge of a SecOps team is keeping up with best practices in an environment where new tools are released on a monthly basis.

More advanced SecOps teams should consider leveraging automation tools, policy configurations, Azure Quick Templates, EventGrid and many other advanced features.

Need manual penetration testing?  Praetorian has expertise in the Cloud, IOT, NetSec and more.

![Azure Security Journey Stages](images/Azure_Security_Stages.png?raw=true "Azure Security Journey Stages")

