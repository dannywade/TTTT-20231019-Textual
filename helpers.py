"""Module for helper functions"""
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)
from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect


def device_connection(host_id: str, credentials: dict) -> ConnectHandler:
    """
    Automatically handles device connections using Netmiko.

    Args:
        host_id (str): Commonly the hostname of a network device
        credentials (dict): A dictionary with 'username' and 'password' as keys

    Returns:
        ConnectHandler object
    """
    remote_device = {
        "device_type": "autodetect",
        "host": host_id,
        "username": credentials.get("username"),
        "password": credentials.get("password"),
    }

    try:
        guesser = SSHDetect(**remote_device)
        best_match = guesser.autodetect()
        remote_device["device_type"] = best_match
        connection = ConnectHandler(**remote_device)
    except (NetmikoTimeoutException, NetmikoAuthenticationException, ValueError) as e:
        print(f"Could not connect to device due to the following error: {e}")
        connection = None

    return connection
