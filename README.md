
Example on using Docker to fetch metrics form Azure VM

# Build and Run


Build the image
```bash
docker build --pull --rm -f "dockerfile.dev" -t azurepythonexample:latest "."
```

Run the image
```bash
docker run --rm -it --env-file local.env  azurepythonexample:latest
```

# References
- Azure for Python Developers https://docs.microsoft.com/en-us/azure/python/?view=azure-python
- List all subscriptions https://docs.microsoft.com/en-us/python/api/azure-mgmt-subscription/azure.mgmt.subscription.operations.subscriptionsoperations?view=azure-python#list-custom-headers-none--raw-false----operation-config-
- Example Fetch Metrics https://stackoverflow.com/questions/54327418/get-cpu-utilization-of-virtual-machines-in-azure-using-python-sdk