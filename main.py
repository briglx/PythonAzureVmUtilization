#!/usr/bin/python
import logging
import json
import os
import csv
from datetime import datetime, timedelta
from azure.common.client_factory import get_client_from_json_dict
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient
import numpy as np


_LOGGER = logging.getLogger(__name__)


class AuthException(ValueError):
    """Auth process failed for some reason."""

    def __str__(self):
        return "Failed to authenticate to Azure. Have you set the AZURE_AUTH environment variable?"


def configure_logger():
    """Configure logger"""
    _LOGGER.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)


def get_management_client(azure_auth, client_class):
    """Returns SDK Client for the given client_class."""
    client = None
    if azure_auth is not None:
        _LOGGER.info("Getting SDK Client for %s", client_class)
        auth_config_dict = json.loads(azure_auth)
        client = get_client_from_json_dict(client_class, auth_config_dict)
    else:
        raise AuthException()
    return client


def get_metric_definitions(client, resource_id):
    """Get details about the metrics"""
    metric_definitions = client.metric_definitions.list(
        resource_id, metricnamespace="Microsoft.Compute/virtualMachines", raw=True
    )
    for metric_definition in metric_definitions:
        _LOGGER.info(metric_definition.name)
        for supported_aggregation_type in metric_definition.supported_aggregation_types:
            _LOGGER.info(supported_aggregation_type)
        for metric_availability in metric_definition.metric_availabilities:
            _LOGGER.info(metric_availability)


def get_mean(array):
    """Get mean from passed array"""
    np_array = np.asarray(array)
    if np_array.any():
        return np_array.mean()
    return None


def get_max(array):
    """Get mean from passed array"""
    np_array = np.asarray(array)
    if np_array.any():
        return np_array.max()
    return None


def get_min(array):
    """Get mean from passed array"""
    np_array = np.asarray(array)
    if np_array.any():
        return np_array.min()
    return None


def get_vm_metrics(monitor_client, resource_id):
    """Get metrics for the given vm. Returns row of cpu, disk, network activity"""

    today = datetime.utcnow().date()
    last_week = today - timedelta(days=7)

    metrics_data = monitor_client.metrics.list(
        resource_id,
        timespan="{}/{}".format(last_week, today),
        interval="PT12H",
        metricnames="Percentage CPU,Disk Read Bytes,Disk Write Bytes,Network In Total,Network Out Total",
        aggregation="Minimum,Average,Maximum",
    )

    row = {}
    ave_cpu = []
    min_cpu = []
    max_cpu = []
    ave_disk_read = []
    ave_disk_write = []
    ave_network_in = []
    ave_network_out = []

    for item in metrics_data.value:
        if item.name.value == "Percentage CPU":
            for timeserie in item.timeseries:
                for data in timeserie.data:
                    if data.average:
                        ave_cpu.append(data.average)
                    if data.minimum:
                        min_cpu.append(data.minimum)
                    if data.maximum:
                        max_cpu.append(data.maximum)

        if item.name.value == "Disk Read Bytes":
            for timeserie in item.timeseries:
                for data in timeserie.data:
                    if data.average:
                        ave_disk_read.append(data.average)

        if item.name.value == "Disk Write Bytes":
            for timeserie in item.timeseries:
                for data in timeserie.data:
                    if data.average:
                        ave_disk_write.append(data.average)

        if item.name.value == "Network In Total":
            for timeserie in item.timeseries:
                for data in timeserie.data:
                    if data.average:
                        ave_network_in.append(data.average)

        if item.name.value == "Network Out Total":
            for timeserie in item.timeseries:
                for data in timeserie.data:
                    if data.average:
                        ave_network_out.append(data.average)

    row = (
        get_mean(ave_cpu),
        get_min(min_cpu),
        get_max(max_cpu),
        get_mean(ave_disk_read),
        get_mean(ave_disk_write),
        get_mean(ave_network_in),
        get_mean(ave_network_out),
    )

    return row


def save_to_file(header, items):
    """Save items to csv file"""

    dte = datetime.utcnow()
    local_filename = "vm-utilization-%s.csv" % (dte.isoformat())
    local_filename = local_filename.replace(":", "-")
    with open(local_filename, "w", newline="") as utilization_report:
        writer = csv.writer(utilization_report, delimiter=",")

        writer.writerows([header])

        for row in items:

            writer.writerows([row])


def main():
    """Main function to get metrics"""
    azure_auth = os.environ.get("AZURE_AUTH")

    # Get Clients
    subscription_client = get_management_client(azure_auth, SubscriptionClient)
    compute_client = get_management_client(azure_auth, ComputeManagementClient)
    monitor_client = get_management_client(azure_auth, MonitorManagementClient)

    rows = []

    # Iterate each subscription
    for subscription in subscription_client.subscriptions.list():
        _LOGGER.info("%s %s", subscription.display_name, subscription.subscription_id)

        for virtual_machine in compute_client.virtual_machines.list_all():
            _LOGGER.info("%s %s", virtual_machine.name, virtual_machine.id)
            row = get_vm_metrics(monitor_client, virtual_machine.id)
            rows.append((subscription.display_name, virtual_machine.id, *row))

    header = list(
        [
            "subscription_name",
            "resource_id",
            "cpu_mean",
            "cpu_min",
            "cpu_max",
            "disk_read_mean",
            "disk_write_mean",
            "network_in_mean",
            "network_out_mean",
        ]
    )
    save_to_file(header, rows)


if __name__ == "__main__":
    configure_logger()
    _LOGGER.info("starting")
    main()
