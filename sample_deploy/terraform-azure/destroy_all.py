#!/usr/bin/env python

import os
from python_terraform import *

def main():
    t = Terraform()

    modules = ['vm', 'sql_databases', 'logging_and_monitoring', 'storage', 'keyvault',]

    for d in filter(os.path.isdir, os.listdir('.')):
        print(d)
        os.chdir(d)
        return_code, stdout, stderr = t.destroy(".", auto_approve=True)
        print("return_code: {}, stdout: {}, stderr: {}".format(return_code, stdout, stderr))
        os.chdir("../")

#for dir in `ls .`; do pushd $dir > /dev/null  && terraform destroy -auto-approve && popd ;done

if __name__ == "__main__":
    main()
