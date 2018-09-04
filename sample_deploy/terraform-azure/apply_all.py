#!/usr/bin/env python

import os
from python_terraform import *

def main():
    t = Terraform()

    modules = ['keyvault', 'storage', 'vm', 'sql_database', 'logging_and_monitoring']
    for d in modules:
        print(d)
        os.chdir(d)
        return_code, stdout, stderr = t.apply(".", auto_approve=True)
        print("return_code: {}, stdout: {}, stderr: {}".format(return_code, stdout, stderr))
        os.chdir("../")

if __name__ == "__main__":
    main()

