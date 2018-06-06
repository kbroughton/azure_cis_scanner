# azure_cis_scanner
Security Compliance Scanning tool for CIS Azure Benchmark 1.0

The purpose of this scanner is to assist organizations in locking down their Azure environments following best practices in the Center for Internet Security Benchmark release Feb 20, 2018.  This repo was inspired by a similar scanner for AWS called Scout2.


The scanner can generate reports that mirror the CIS sections.
![alt text](https://raw.githubusercontent.com/praetorian-inc/azure_cis_scanner/master/images/azure_cis_splash.png)

This scanner also allows tracking progress over time
![alt text](https://raw.githubusercontent.com/praetorian-inc/azure_cis_scanner/master/images/to/azure_cis_graph.png)


Raw data will have the format as returned by the Azure Api in json format.
Raw data will be per major CIS section in files based on the name.

```
Identity and Access Management       Logging and Monitoring                 
Security Center                      Networking
Storage                              Virtual Machines
SQL Services                         Other Miscellaneous Items

```

Filtered data will be in files named by the finding and have the following format

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

## Getting Started
Best practice is to work inside a docker container to avoid any issues that would arise from a multi-tenant environment.
If running from the native command-line, take care that multi-subscription calls like permissions.sh only see the right target
subscriptions in the `~/.azure/ directory`.  


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
working-project$ docker run -it -v .azure/:~/.azure -v .:/workdir
bash-4.3#
```

We are now inside the container at the bash-4.3# prompt.  Time to log in.

```
bash-4.3# az login
```
Complete the web UI login.

Modify minimal_tester_role.json with the correct subscription(s)

Modify the permissions.sh with positional variables $1=start_date, $2=end_date, $3=ip_whitelist for the generated storage keys

```
bash-4.3# /workdir/permissions.sh
```

The script creates a AzureSecurityScanner role definition.  The Owner now associates that role to the users.

Copy the generated (resource_group, account, SAS keys) tuples and send them securely to the pen-tester.

### Running the azure_cis_scanner

Follow the steps for the Owner above except for running the permissions script.

As a user with the AzureSecurityScanner role and the sas keys stored to ./sas_keys.txt
and modifications made to scanner_conf.yaml for your environment:

```
bash-4.3# cd /workdir
bash-4.3# python cis_azure_scanner.py scan
```

The scanner creates scans/Y-m-d/ folders for each day that the scan is run, clobbering old results if run multiple times in a day.
This allows progress to be tracked over time.

To view the results
```
bash-4.3# python cis_azure_scanner.py report
```

This will run a simple flask app which you can view at localhost:5000

## Constraints
An attempt was made to convert to json everywhere, but the current raw/filtered data used key tuples (eg (resource_group, server, database))
which only supported in yaml.  An attempt to use safe_yaml was made, but the tuples caused errors.  The intention is to have `raw` data pulled
as infrequently as possible from the cloud api, stored as close as possible to the delivered format.  
We may switch from tuple to nested dict in the future.

## Roadmap
Further development of automation for deployment of an insecure test environment.
Remediation scripts to automatically resolve many simple "switch on" issues.
Use the python sdk instead of bash.
Wrap the flask project with praetorian-flask for security.  Only run on a local network until this is complete.
Remove manual steps by generating minimal_tester_role.json with correct subscriptions/resource_group paths.

## Digging Deeper
A Scanner is a good first tool for securing a cloud environment to ensure best practices and secure configuration settings are employed.
However, this scanner does not assess the health of your IAM policies and roles or network security groups beyond some basic known-bad settings.  Azure is constantly evolving and part of the challenge of a SecOps team is keeping up with best practices in an environment where new tools are released on a monthly basis.

More advanced SecOps teams should consider leveraging automation tools, policy configurations, Azure Quick Templates, EventGrid and many other advanced features.

Need manual penetration testing?  Praetorian has expertise in the Cloud, IOT, NetSec and more.

