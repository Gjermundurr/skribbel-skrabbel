from extras.scripts import Script, ObjectVar, IPNetworkVar, IPAddressVar, IntegerVar
from ipam.models import Prefix, Role
from dcim.models import Interface, Device
from os import getenv
from requests import post

# replace with hashicorp plugin? 
GITLAB_URL = getenv("GITLAB_URL")
GITLAB_TOKEN = getenv("GITLAB_TOKEN")

PROJECT_ID = 1234
PROJECT_REF = "main"
ENDPOINT = f"/api/v4/projects/{PROJECT_ID}/ref/{PROJECT_REF}/trigger/pipeline"


class DeployVxlanWebhook(Script):
    class Meta:
        name = "Deploy VXLAN configuration via Webhook"
        description = "Input vxlan deployment details and invoke deployment via webhook"
        scheduling_enabled = False
        commit_default = False


    vlan_role = ObjectVar(
        model=Role,
        label="Role",
        required=True,
        description="Select network role"
    )
    vlan = IntegerVar(
        label="VLAN",
        required=False,
        description="Specify VLAN ID (leave blank to auto-select)"
    )
    prefix = IPNetworkVar(
        label="Prefix",
        required=False,
        description="Specify prefix, Ex: 192.168.1.0/24 (leave blank to auto-select)"
    )
    gateway = IPAddressVar(
        label="Gateway",
        required=False,
        description="Specify gateway, Ex: 192.168.1.1 (leave blank to auto-select)"
    )
    leaf_interface = ObjectVar(
        model=Interface,
        label="Leaf Interface",
        required=False,
        description="Select the leaf interface"
    )
    leaf_switch = ObjectVar(
        model=Device,
        label="Leaf Switch",
        required=False,
        description="Select the leaf switch role"
    )

    def run(self, data, commit):

        if not all([GITLAB_URL, GITLAB_TOKEN]):
            raise ValueError("GITLAB_URL and GITLAB_TOKEN environment variables must be set")

        # post data to webhook url to invoke gitlab pipeline
        response = post(
            url=f"{GITLAB_URL}{ENDPOINT}",
            headers={
                "Authorization": f"Bearer {GITLAB_TOKEN}"
            },
            json={
                "vlan_role": str(data["vlan_role"]),
                "vlan": str(data["vlan"]),
                "prefix": str(data["prefix"]),
                "gateway": str(data["gateway"])
            }
        )
        if response.status_code == 200:
            self.log_success("webhook successfully posted")
        else:
            self.log_failure(f"Webhook response error: {response.status_code}, Response: {response.text}")
