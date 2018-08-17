jupyter notebook --port=8888 --ip=0.0.0.0 --allow-root &

pushd /praetorian-tools/azure_cis_scanner
python3 setup.py install
popd >> /dev/null

run_jnb -a '{"subscription_id": "510f92e0-xxxx-yyyy-zzzz-095d37e6a299", "base_dir": "/engagements/${PROJECT}"}' -v /praetorian_tools/azure_cis_scanner/scanner/azure_cis_scanner.ipynb -t 500

flask app.py
