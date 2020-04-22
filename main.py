#!/usr/bin/python
import logging
import json
import os
import datetime
from azure.common.client_factory import get_client_from_json_dict
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient


_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
_LOGGER.addHandler(ch)


def get_management_client(azure_auth):
    """Get Container Client."""
    client = None
    if azure_auth is not None:
        _LOGGER.info("Authenticating Azure using credentials")
        auth_config_dict = json.loads(azure_auth)
        client = get_client_from_json_dict(MonitorManagementClient, auth_config_dict)
    else:
        _LOGGER.error(
            "\nFailed to authenticate to Azure. Have you set the"
            " AZURE_AUTH environment variable?\n"
        )
    return client


def main():
    azure_auth = os.environ.get("AZURE_AUTH")
    resource_id = os.environ.get("RESOURCE_ID")

    client = get_management_client(azure_auth)

    today  = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)

    metrics_data = client.metrics.list(
        resource_id,
        timespan="{}/{}".format(yesterday, today),
        interval='PT1H',
        metric='Percentage CPU',
        aggregation='Total'
    )

    for item in metrics_data.value:
        # azure.mgmt.monitor.models.Metric
        _LOGGER.info("{} ({})".format(item.name.localized_value, item.unit.name))
        for timeserie in item.timeseries:
            for data in timeserie.data:
                # azure.mgmt.monitor.models.MetricData
                _LOGGER.info("{}: {}".format(data.time_stamp, data.total))


if __name__ == "__main__":
    _LOGGER.info("starting")
    main()
