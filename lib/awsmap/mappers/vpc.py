from lib.awsmap.map import Map

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.network import VPC


class VPCMapper(Map):

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
                        pc_tags = self._tags(peer_connection['Tags'])
                        with Cluster(peer_connection['RequesterVpcInfo']['VpcId']):
                            pc_use_name = "\n".join(pc_tags['Name'].split(" "))

                            pc_vpc = VPC(f"{peer_connection['RequesterVpcInfo']['CidrBlock']}\n{pc_use_name}")
                        vpc << pc_vpc
