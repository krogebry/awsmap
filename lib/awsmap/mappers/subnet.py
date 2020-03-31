from lib.awsmap.map import Map

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.network import VPC, InternetGateway, NATGateway, ClientVpn, SiteToSiteVpn


class SubnetMapper(Map):

    def get_internet_gateways(self, vpc_id,
                    profile_name: str = "default",
                    region_name: str = "us-west-2"):

        cache_key = self._make_cache_key(profile_name, region_name, f"{vpc_id}_igws")
        inet_gws = self.cache.get_cache(cache_key)
        if not inet_gws:
            client = self._get_client('ec2', profile_name=profile_name, region_name=region_name)
            data = client.describe_internet_gateways(
                Filters=[{
                    'Name': 'attachment.vpc-id',
                    'Values': [vpc_id]
                }]
            )
            inet_gws = self.cache.set_cache(cache_key, data)

        return inet_gws['InternetGateways']

    def get_nat_gateways(self, vpc_id,
                    profile_name: str = "default",
                    region_name: str = "us-west-2"):

        cache_key = self._make_cache_key(profile_name, region_name, f"{vpc_id}_nat_gws")
        nat_gws = self.cache.get_cache(cache_key)
        if not nat_gws:
            client = self._get_client('ec2', profile_name=profile_name, region_name=region_name)
            data = client.describe_nat_gateways(
                Filters=[{
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }]
            )
            nat_gws = self.cache.set_cache(cache_key, data)

        return nat_gws['NatGateways']

    def get_route_tables(self, vpc_id,
                    profile_name: str = "default",
                    region_name: str = "us-west-2"):

        cache_key = self._make_cache_key(profile_name, region_name, f"{vpc_id}_route_tables")
        route_tables = self.cache.get_cache(cache_key)
        if not route_tables:
            client = self._get_client('ec2', profile_name=profile_name, region_name=region_name)
            data = client.describe_route_tables(
                Filters=[{
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }]
            )
            route_tables = self.cache.set_cache(cache_key, data)

        return route_tables['RouteTables']

    def get_subnets(self, vpc_id,
                    profile_name: str = "default",
                    region_name: str = "us-west-2"):

        cache_key = self._make_cache_key(profile_name, region_name, f"{vpc_id}_subnets")
        subnets = self.cache.get_cache(cache_key)
        if not subnets:
            client = self._get_client('ec2', profile_name=profile_name, region_name=region_name)
            data = client.describe_subnets(
                Filters=[{
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }]
            )
            subnets = self.cache.set_cache(cache_key, data)

        return subnets['Subnets']

    def get_vpn_gateways(self, vpc_id,
                    profile_name: str = "default",
                    region_name: str = "us-west-2"):

        cache_key = self._make_cache_key(profile_name, region_name, f"{vpc_id}_vpn_gateways")
        vpn_gateways = self.cache.get_cache(cache_key)
        if not vpn_gateways:
            client = self._get_client('ec2', profile_name=profile_name, region_name=region_name)
            data = client.describe_vpn_gateways(
                Filters=[{
                    'Name': 'attachment.vpc-id',
                    'Values': [vpc_id]
                }]
            )
            vpn_gateways = self.cache.set_cache(cache_key, data)

        return vpn_gateways['VpnGateways']

    def compile(
            self,
            vpc_id,
            profile_name: str = "default",
            region_name: str = "us-west-2"
    ):
        self.p(f"Compiling: {vpc_id} / {profile_name} / {region_name}")

        vpn_gws = self.get_vpn_gateways(vpc_id, profile_name=profile_name, region_name=region_name)
        subnets = self.get_subnets(vpc_id, profile_name=profile_name, region_name=region_name)
        nat_gws = self.get_nat_gateways(vpc_id, profile_name=profile_name, region_name=region_name)
        inet_gws = self.get_internet_gateways(vpc_id, profile_name=profile_name, region_name=region_name)

        route_tables = self.get_route_tables(vpc_id, profile_name=profile_name, region_name=region_name)
        # self.pp(route_tables)

        with Diagram(vpc_id, filename=f"images/subnets_{vpc_id}", show=False):
            internet_gateways = {}
            for inet_gw in inet_gws:
                internet_gateways[inet_gw['InternetGatewayId']] = InternetGateway(inet_gw['InternetGatewayId'])

            nat_gateways = {}
            for nat_gw in nat_gws:
                nat_gateways[nat_gw['NatGatewayId']] = NATGateway(nat_gw['NatGatewayId'])

            vpn_gateways = {}
            for vpn_gw in vpn_gws:
                vpn_gateways[vpn_gw['VpnGatewayId']] = ClientVpn(vpn_gw['VpnGatewayId'])

            for subnet in subnets:
                # self.pp(subnet)
                subnet_tags = self._tags(subnet['Tags'])

                with Cluster(subnet_tags['Name']):
                    diag_subnet = VPC(f"{subnet['CidrBlock']}\n{subnet['AvailabilityZone']}")

                # Is this subnet associated with a RT?
                for rt in route_tables:
                    self.pp(rt)
                    for rt_association in rt['Associations']:
                        # self.pp(rt_association)
                        if 'SubnetId' in rt_association.keys() and rt_association['SubnetId'] == subnet['SubnetId']:
                            self.p(f"Found RT association")
                            for route in rt['Routes']:
                                if 'NatGatewayId' in route and route['NatGatewayId'] in nat_gateways.keys():
                                    self.p(f"Found NAT Gateway route: {route['NatGatewayId']}")
                                    diag_subnet >> nat_gateways[route['NatGatewayId']]

                                if 'GatewayId' in route and route['GatewayId'] in vpn_gateways.keys():
                                    self.p(f"Found VPN Gateway route: {route['GatewayId']}")
                                    diag_subnet >> vpn_gateways[route['GatewayId']]

                                if 'GatewayId' in route and route['GatewayId'] in internet_gateways.keys():
                                    self.p(f"Found Internet Gateway route: {route['GatewayId']}")
                                    diag_subnet >> internet_gateways[route['GatewayId']]


