# Python Azure VM Utilization

Example on using Docker to fetch metrics from Azure VM

# Development Setup

Make a copy of local.env.example and rename to local.env. Edit the file with the necessary credentials for the service principal.

# Using Docker

Build the image
```bash
docker build --pull --rm -f "dockerfile.dev" -t azurepythonexample:latest "."
```

Run the image
```bash
docker run --rm -it azurepythonexample:latest

# run with an environment file
docker run --rm -it --env-file local.env azurepythonexample:latest
```

Run the script

```python
#> python main.py
```

# Notes

Should call `client.metric_definitions.list` to get the exact metric details for each metric. See https://docs.microsoft.com/en-us/rest/api/monitor/metricdefinitions/list

Interesting Metrics for VMs

- Percentage CPU. The percentage of allocated compute units that are currently in use by the Virtual Machine(s)
- Disk Read Bytes
- Disk Write Bytes
- Network In Total. The number of bytes received on all network interfaces by the Virtual Machine(s) (Incoming Traffic)
- Network Out Total

Most metrics allow time grain to be any of the following

```python
class TimeGrain(str, Enum):

    pt1_m = "PT1M"
    pt5_m = "PT5M"
    pt15_m = "PT15M"
    pt30_m = "PT30M"
    pt1_h = "PT1H"
    pt6_h = "PT6H"
    pt12_h = "PT12H"
    pt1_d = "PT1D"
```

Most metrics allow the following Aggregation types

```python
class AggregationType(str, Enum):

    none = "None"
    average = "Average"
    count = "Count"
    minimum = "Minimum"
    maximum = "Maximum"
    total = "Total"
```

# References
- Azure for Python Developers https://docs.microsoft.com/en-us/azure/python/?view=azure-python
- List all subscriptions https://docs.microsoft.com/en-us/python/api/azure-mgmt-subscription/azure.mgmt.subscription.operations.subscriptionsoperations?view=azure-python#list-custom-headers-none--raw-false----operation-config-
- Example Fetch Metrics https://stackoverflow.com/questions/54327418/get-cpu-utilization-of-virtual-machines-in-azure-using-python-sdk
- MetricsOperation Class https://docs.microsoft.com/en-us/python/api/azure-mgmt-monitor/azure.mgmt.monitor.v2018_01_01.operations.metricsoperations?view=azure-python
- Definitions of Metrics https://docs.microsoft.com/en-us/rest/api/monitor/metricdefinitions/list#definitions
- Authenicate with Json https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate?tabs=bash#authenticate-with-a-json-file