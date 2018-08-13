
curl -L https://aka.ms/InstallAzureCli | bash
apk update && apk add mktemp
mktemp
curl -L https://aka.ms/InstallAzureCli -O azcli.sh
mktemp -t azure_cli_install_tmp_XXXX
mktemp -t azure
chmod a+x azcli.sh
./azcli.sh
apk add openssl-dev
az login
pip3 install -r requirements.txt
python3 setup.py
mv azure_cis_scannerWe use the azure foundation benchmark from CIS release feb 20 of this year.
https://www.cisecurity.org/cis-microsoft-azure-foundations-benchmark-v1-0-0-now-available/
mv azure_cis_scanner/azscanner.bat bin/
mv azscanner bin/
