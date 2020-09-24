import yaml
import os.path
from lib.awsmap.map import Map

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.network import VPC, InternetGateway, NATGateway, ClientVpn, SiteToSiteVpn

from diagrams.oci.storage import FileStorage
from diagrams.oci.compute import Container

class DockerComposeMapper(Map):

    def compile(self, docker_compose_file):
        self.p(f"Docker: {docker_compose_file}")

        dc_file = open(docker_compose_file)
        dc_yaml = yaml.safe_load(dc_file.read())

        self.pp(dc_yaml)

        node_attrs = {
            # "width": "1.3"
            # "fixedsize": "false"
            # "imagescale": "false"
        }

        service_containers = {}

        with Diagram(os.path.basename(docker_compose_file), filename=f"images/dc", show=False, node_attr=node_attrs):

            localhost = Container("localhost")

            for service_name, service_config in dc_yaml['services'].items():
                self.p(f"Service: {service_name}")
                with Cluster(service_name):
                    container = Container(service_name)
                    service_containers[service_name] = container
                    if "volumes" in service_config.keys():
                        for volume in service_config['volumes']:
                            container << FileStorage("\n".join(volume.split(":")))

                    if "ports" in service_config.keys():
                        for port in service_config['ports']:
                            container << Edge(label=port) << localhost

            for service_name, service_config in dc_yaml['services'].items():
                # Dependency edges
                if "depends_on" in service_config.keys():
                    for dep in service_config['depends_on']:
                        # service_containers[service_name] << Edge(label=dep, color="red", style="dashed") << localhost
                        service_containers[dep] << Edge(color="red", style="dashed") << service_containers[service_name]



