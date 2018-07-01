
.. role:: raw-html-m2r(raw)
   :format: html



azure_cis_scanner
=================

Security Compliance Scanning tool for CIS Azure Benchmark 1.0

The purpose of this scanner is to assist organizations in locking down their Azure environments following best practices in the Center for Internet Security Benchmark release Feb 20, 2018.  This repo was inspired by a similar scanner for AWS called Scout2.

This project is not yet production ready and should only be run from a local machine not exposed to untrusted networks.

The scanner can generate reports that mirror the CIS sections.
--------------------------------------------------------------

.. image:: images/cis_test_vm_section.png?raw=true
   :target: images/cis_test_vm_section.png?raw=true
   :alt: azure cis scanner homet



This scanner also allows tracking progress over time
----------------------------------------------------

.. image:: images/cis_test_secure_transfer_graph.png?raw=true
   :target: images/cis_test_secure_transfer_graph.png?raw=true
   :alt: Azure Storage: Secure Transfer not Enabled



Raw data will have the format as returned by the Azure Api in json format.
Raw data will be per major CIS section in files based on the name.

.. code-block::

   Identity and Access Management       Logging and Monitoring                 
   Security Center                      Networking
   Storage                              Virtual Machines
   SQL Services                         Other Miscellaneous Items


Filtered data will be in files named by the finding and have the following format

.. code-block::

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


Getting Started
---------------

Best practice is to work inside a docker container to avoid any issues that would arise from a multi-tenant environment.
If running from the native command-line, take care that multi-subscription calls like permissions.sh only see the right target
subscriptions in the ``~/.azure/ directory``.  

The container is currently a base of pshchelo/alpine-jupyter-sci-py3 with microsoft/azure-cli Dockerfile layered on top.
We will replace the pshchelo base with a more official (nbgallery or jupyter) docker image and tune the image in the future.

We assume you have already created an azure account or have been granted credentials with privileges sufficient to run the scanner.
We will login once outside of the container (merges creds with anything in ~/.azure) to get the correct subscription id, and then
again inside the container to restrict ourselves to the correct creds only.

Configure
^^^^^^^^^

Get the repo (until it is public)

.. code-block::

   $ git clone git@github.com:praetorian-inc/azure_cis_scanner.git && cd azure_cis_scanner


Get the repo (public)

.. code-block::

   $ git clone https://github.com/praetorian-inc/azure_cis_scanner.git && cd azure_cis_scanner


Copy azure_cis_scanner/.env-sample to .env.  This is a special filename that controls docker-compose and is in .gitignore.

.. code-block::

   azure_cis_scanner$ cp .env-sample .env


Edit the azure_cis_scanner/.env file as needed.
If you are going to be developing, open docker-compose.yml and uncomment the lines marked with # DEVELOPMENT MODE

Run the container and exec into it
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

   azure_cis_scanner$ docker-compose up


In another terminal get the container id and exec into it

.. code-block::

   azure_cis_scanner$ docker ps
   azure_cis_scanner$ docker exec -it <container-id> /bin/bash


Login inside the container
^^^^^^^^^^^^^^^^^^^^^^^^^^

The docker-compose creates (on first run) a .azure folder to hold the creds and maps it to /root/.azure.
This allows you to stop and start the container without having to re login for the lifetime of your tokens.

.. code-block::

   bash-4.4$ az login
   bash-4.4$ az account list
   bash-4.4$ az account set --subscription <choice from above>


Edit report/settings.py for your active_subscription_dir.  This can be anything, but convention is the friendly name and the first 8 chars 
from the correct ``id`` in ``account list`` above. Since it is mounted into the container, it will change inside and outside the container.

Sample deploy (optional)
^^^^^^^^^^^^^^^^^^^^^^^^

If you have no resource or just want to test the scanner on fresh resources, try some of the automated deployment resources.
Currently, sample-deploy/terraform-azure is working the best.  First we need to add terraform to the container.

.. code-block::

   apk add terraform


For each folder, cd into it and run

.. code-block::

   terraform init
   terraform apply


You will likely have to re-login as terraform has short timeouts on tokens.
REMEMBER TO DESTROY YOUR RESOURCES WHEN FINISHED

.. code-block::

   terraform destroy


It is best practice to create automated billing alerts via the UI to avoid unpleasant surprises.

Run the scanner
^^^^^^^^^^^^^^^

Change to the scanner directory inside the container and run the scanner using a run_jnb command which 
sets variables in the jupyter notebook and runs it. Alternatively, on your first run, you can use the url 
output from ``docker-compose up`` to login to the notebook and step through the calls.  Edit the line below
with appropriate arguments for subscription_id and base_dir.

.. code-block::

   bash-4.4$ cd /praetorian-tools/azure_cis_scanner/scanner
   scanner$ run_jnb -a '{"subscription_id": "510f92e0-xxxx-yyyy-zzzz-095d37e6a299", "base_dir": "/engagements/cis_test"}' -v azure_cis_scanner.ipynb -t 500


If the terminal prompt gets messed up, try modifying the above in an editor and pasting in its entirety into the shell.
There is currently no progress report, but if you open sublime you can watch the files as they are created in base_dir.
If the files are not created as expected, search for clues in the _run_jnb output or, better, go to the jupyter notebook in your browser
and step through the cells until an error occurs.

Note that running the scanner a second time on the same day will clobber the old result.  A new folder is created when the scanner is 
run on a new day.

Browse the report
^^^^^^^^^^^^^^^^^

At this point your base_dir should have been populated with files as shown below

.. image:: images/cis_test_azure_scanner_files.png?raw=true
   :target: images/cis_test_azure_scanner_files.png?raw=true
   :alt: raw and filtered generated files



Inside the container we now run a flask app to server generated html pages with the reports.

.. code-block::

   bash-4.4 scanner$ cd ../report
   bash-4.4 report$ python3 app.py


Browse to 127.0.0.1:5000 to view the report.  The subscription switching via the UI does not work yet.

Currently, graphs will not display until there are two days of data.

Requesting credentials with the correct RBACs to run the scanner
----------------------------------------------------------------

If you need to run the scanner on someone else's Azure environment, you should ask for the minimum possible
permissions.

Owner Generates Minimal Permissions Role Definition and Temporary Keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following steps should be performed by someone with Owner permissions to generate minimal creds for the tester.
Get the minimal_tester_role.json and permissions.sh scripts used to generate a custom role definition and temporary storage access keys.

.. code-block::

   $ git clone https://github.com/praetorian-inc/azure_cis_scanner.git


Fetch the official microsoft container

.. code-block::

   $ docker pull microsoft/azure-cli


If you are going to be working over many days and shutting down the container between runs, you may want to create a project-directory
.azure folder which you will mount into the container.  Persisting creds with local mount  ``-v .azure/:~/.azure`` is optional.

.. code-block::

   $ cd /path/to/working-project
   $ cp /path/to/azure_cis_scanner/{permissions.sh,minimal_tester_role.sh} .
   working-project$ docker run -it -v .azure/:~/.azure -v .:/workdir
   bash-4.3#


We are now inside the container at the bash-4.3# prompt.  Time to log in.

.. code-block::

   bash-4.3# az login


Complete sign-in via the web UI login.

Modify minimal_tester_role.json with the correct subscription(s)

Modify the permissions.sh with positional variables $1=start_date, $2=end_date, $3=ip_whitelist for the generated storage keys

.. code-block::

   bash-4.3# /workdir/permissions.sh


The script creates a AzureSecurityScanner role definition.  The Owner now associates that role to the 
users and can copy the generated (resource_group, account, SAS keys) tuples and send them securely to the pen-tester.

Constraints
-----------

An attempt was made to convert to json everywhere, but the current raw/filtered data used key tuples - eg (resource_group, server, database) -
which only supported in yaml.  An attempt to use safe_yaml was made, but the tuples caused errors.  The intention is to have ``raw`` data pulled
as infrequently as possible from the cloud API, stored as close as possible to the delivered format.\ :raw-html-m2r:`<br>`
We may switch from tuple to nested dict in the future.

Roadmap
-------


* Further development of automation for deployment of an insecure test environment.
* Add to remediation scripts in the ``remediations`` folder to automatically resolve many simple "switch on" issues.
* Use the python sdk instead of bash.
* Wrap the flask project with praetorian-flask for security.  Only run on a local network until this is complete.
* Remove manual steps by generating minimal_tester_role.json with correct subscriptions/resource_group paths.
* The container is currently a base of pshchelo/alpine-jupyter-sci-py3 with microsoft/azure-cli Dockerfile layered on top.
* Replace the pshchelo base with a more official (nbgallery or jupyter) docker image and tune the image in the future.
* Add git hooks to automatically remove cell output of azure_cis_scanner.ipynb to avoid checking in sensitive info

Digging Deeper
--------------

A Scanner is a good first tool for securing a cloud environment to ensure best practices and secure configuration settings are employed.
However, this scanner does not assess the health of your IAM policies and roles or network security groups beyond some basic known-bad settings.  Azure is constantly evolving and part of the challenge of a SecOps team is keeping up with best practices in an environment where new tools are released on a monthly basis.

More advanced SecOps teams should consider leveraging automation tools, policy configurations, Azure Quick Templates, EventGrid and many other advanced features.

Need manual penetration testing?  Praetorian has expertise in the Cloud, IOT, NetSec and more.
