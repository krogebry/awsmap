"""Build diagram of the Subnets and related attach routing."""
from lib.awsmap.map import Map
from diagrams import Cluster, Diagram
from diagrams.aws.network import VPC, InternetGateway, NATGateway, ClientVpn, TransitGateway


class SubnetMapper(Map):
    """Mapped class of a subnet."""

    def get_internet_gateways(self, vpc_id, profile_name, region_name):
        """Fetch Internet Gateway details."""
        cache_key = self._make_cache_key(profile_name, region_name, "{}_igws".format(vpc_id))
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

    def get_nat_gateways(self, vpc_id, profile_name, region_name):
        """Fetch NAT Gateway details."""
        cache_key = self._make_cache_key(profile_name, region_name, "{}_nat_gws".format(vpc_id))
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

    def get_route_tables(self, vpc_id, profile_name, region_name):
        """Fetch Route Tables."""
        cache_key = self._make_cache_key(profile_name, region_name, "{}_route_tables".format(vpc_id))
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

    def get_subnets(self, vpc_id, profile_name, region_name):
        """Fetch subnet details."""
        cache_key = self._make_cache_key(profile_name, region_name, "{}_subnets".format(vpc_id))
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

    def get_vpn_gateways(self, vpc_id, profile_name, region_name):
        """Fetch VPN Gateway details."""
        cache_key = self._make_cache_key(profile_name, region_name, "{}_vpn_gateways".format(vpc_id))
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

    def get_transit_gateways(self, vpc_id, profile_name, region_name):
        """Fetch details on the attached Transit Gateways."""
        cache_key = self._make_cache_key(profile_name, region_name, "{}_transit_gateways".format(vpc_id))
        transit_gateways = self.cache.get_cache(cache_key)
        if not transit_gateways:
            client = self._get_client('ec2', profile_name=profile_name, region_name=region_name)
            data = client.describe_transit_gateway_vpc_attachments(
                Filters=[{
                    'Name': 'vpc-id',
                    'Values': [vpc_id]
                }]
            )
            transit_gateways = self.cache.set_cache(cache_key, data)

        return transit_gateways['TransitGatewayVpcAttachments']

    def compile(self, vpc_id, profile_name, region_name):
        """Build Diagram of the subnets."""
        self.p("Compiling: {} / {} / {}".format(vpc_id, profile_name, region_name))

        vpn_gws = self.get_vpn_gateways(vpc_id, profile_name=profile_name, region_name=region_name)
        subnets = self.get_subnets(vpc_id, profile_name=profile_name, region_name=region_name)
        nat_gws = self.get_nat_gateways(vpc_id, profile_name=profile_name, region_name=region_name)
        inet_gws = self.get_internet_gateways(vpc_id, profile_name=profile_name, region_name=region_name)
        transit_gws = self.get_transit_gateways(vpc_id, profile_name=profile_name, region_name=region_name)

        route_tables = self.get_route_tables(vpc_id, profile_name=profile_name, region_name=region_name)
        # self.pp(route_tables)

        with Diagram(vpc_id,
                     filename="images/{}/subnets_{}".format(self.get_account_id(profile_name, region_name), vpc_id),
                     show=False,
                     graph_attr=self.graph_attr):
            internet_gateways = {}
            for inet_gw in inet_gws:
                internet_gateways[inet_gw['InternetGatewayId']] = InternetGateway(inet_gw['InternetGatewayId'])

            nat_gateways = {}
            for nat_gw in nat_gws:
                nat_gateways[nat_gw['NatGatewayId']] = NATGateway(nat_gw['NatGatewayId'])

            vpn_gateways = {}
            for vpn_gw in vpn_gws:
                vpn_gateways[vpn_gw['VpnGatewayId']] = ClientVpn(vpn_gw['VpnGatewayId'])

            transit_gateways = {}
            for transit_gw in transit_gws:
                transit_gateways[transit_gw['TransitGatewayId']] = TransitGateway(transit_gw['TransitGatewayId'])

            for subnet in subnets:
                # self.pp(subnet)
                subnet_tags = self._tags(subnet['Tags'])

                with Cluster(subnet_tags['Name']):
                    diag_subnet = VPC("{}\n{}".format(subnet['CidrBlock'], subnet['AvailabilityZone']))

                # Is this subnet associated with a RT?
                for rtable in route_tables:
                    self.pp(rtable)
                    for rt_association in rtable['Associations']:
                        # self.pp(rt_association)
                        if 'SubnetId' in rt_association.keys() and rt_association['SubnetId'] == subnet['SubnetId']:
                            self.p("Found RT association")
                            for route in rtable['Routes']:
                                if 'NatGatewayId' in route and route['NatGatewayId'] in nat_gateways.keys():
                                    self.p("Found NAT Gateway route: {}".format(route['NatGatewayId']))
                                    diag_subnet >> nat_gateways[route['NatGatewayId']]

                                if 'GatewayId' in route and route['GatewayId'] in vpn_gateways.keys():
                                    self.p("Found VPN Gateway route: {}".format(route['GatewayId']))
                                    diag_subnet >> vpn_gateways[route['GatewayId']]

                                if 'GatewayId' in route and route['GatewayId'] in internet_gateways.keys():
                                    self.p("Found Internet Gateway route: {}".format(route['GatewayId']))
                                    diag_subnet >> internet_gateways[route['GatewayId']]

                                if 'TransitGatewayId' in route and route['TransitGatewayId'] in transit_gateways.keys():
                                    self.p("Found Transit Gateway route: {}".format(route['TransitGatewayId']))
                                    diag_subnet >> transit_gateways[route['TransitGatewayId']]
