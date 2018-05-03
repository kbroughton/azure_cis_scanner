# azure_cis_scanner
Security Compliance Scanning tool for CIS Azure Benchmark 1.0


Raw data will have the format as returned by the Azure Api in json format.
Raw data will be per major CIS section in files based on the name.

```
Identity and Access Management
Security Center
Storage 
Virtual Machines
...
```

Filtered data will be in files named by the finding and have the following format

{
	"finding_name": "threat detection should be turned on",
	"columns": ['region', 'server', database' ],
	"stats": {"items_checked": 10, "items_flagged": 4},
	"data": [
	  ('us-west-1', 'server01', 'db011')
	  ('us-west-2', 'server02', 'db021')
	  ('us-west-2', 'server02', 'db023')
	  ('us-west-2', 'server02', 'db024')
	  ]
}