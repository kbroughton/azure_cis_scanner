
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
python3 setup.py install

azscan --help
azscan
