# windows.ps1

# TODO make this powershell

1. Install python3 https://www.python.org/downloads/ (python 3.6 recommended by 3.7 should work)
2. pip install azure-cis-scanner
3. install azure cli
4. Set path to value it suggests in the install output
$env:path="$env:path;c:\users\<username>\appdata\local\programs\python\<python37-32>\Scripts"
5. log out of powershell (to get things to be applied) and log back in
6. azscan