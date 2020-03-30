import boto3

from lib.awsmap.cache import Cache

from diagrams import Cluster, Diagram, Edge

from diagrams.aws.compute import EC2
from diagrams.aws.compute import ElasticKubernetesService as EKS

from diagrams.aws.network import ELB
from diagrams.aws.network import VPC
from diagrams.aws.network import SiteToSiteVpn
from diagrams.aws.network import ClientVpn
from diagrams.aws.network import NATGateway

from diagrams.onprem.network import Internet
from diagrams.onprem.client import Users

from diagrams.aws.management import AutoScaling

from pprint import PrettyPrinter


class Map:
    def __init__(self, dryrun, verbose):
        self.dryrun = dryrun
        self.verbose = verbose

        self.prettyp = PrettyPrinter(indent=4)
        self.cache = Cache()

    def p(self, msg):
        if self.verbose:
            print(msg)

    def pp(self, dict):
        if self.verbose:
            self.prettyp.pprint(dict)

    def _get_client(self, service_name, profile_name="default", region_name="us-east-1"):
        session = boto3.Session(profile_name=profile_name, region_name=region_name)
        return session.client(service_name)

    def _make_cache_key(self, profile_name, region_name, topic):
        key = f"{profile_name}_{region_name}_{topic}"
        return key

    def _tags(self, tags):
        ro = {}
        for tag in tags:
            ro[tag['Key']] = tag['Value']
        return ro

    def get_vpcs(self, profile_name, region_name):
        cache_key = self._make_cache_key(profile_name, region_name, "vpcs")
        vpcs = self.cache.get_cache(cache_key)
        if not vpcs:
            client = self._get_client('ec2', profile_name=profile_name, region_name=region_name)
            data = client.describe_vpcs()
            vpcs = self.cache.set_cache(cache_key, data)

        return vpcs['Vpcs']

    def get_peering_connections(self, vpc_id, profile_name="default", region_name="us-east-1"):
        cache_key = self._make_cache_key(profile_name, region_name, f"vpc_peer_connections_{vpc_id}")
        connections = self.cache.get_cache(cache_key)
        if not connections:
            client = self._get_client('ec2', profile_name=profile_name, region_name=region_name)
            data = client.describe_vpc_peering_connections(
                Filters=[{
                    'Name': 'accepter-vpc-info.vpc-id',
                    'Values': [vpc_id]
                }]
            )
            connections = self.cache.set_cache(cache_key, data)

        return connections["VpcPeeringConnections"]

    def compile(
            self,
            profile_name: str = "default",
            region_name: str = "us-west-2"
    ):
        self.p(f"Compiling: {profile_name} / {region_name}")

        vpcs = self.get_vpcs(profile_name, region_name)
        # self.pp(vpcs)

        with Diagram("Renovo", filename="images/vpc", show=False):
            for vpc in vpcs:
                self.pp(vpc)
                tags = self._tags(vpc['Tags'])

                peering_connections = self.get_peering_connections(
                    vpc["VpcId"],
                    profile_name=profile_name,
                    region_name=region_name
                )
                self.pp(peering_connections)

                with Cluster(tags['Name']):
                    vpc = VPC(vpc['CidrBlock'])

                if len(peering_connections) > 0:
                    for peer_connection in peering_connections:
                        with Cluster(peer_connection['RequesterVpcInfo']['VpcId']):
                            pc_vpc = VPC(peer_connection["RequesterVpcInfo"]['CidrBlock'])
                        vpc << pc_vpc
