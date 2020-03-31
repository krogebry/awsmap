import boto3
from lib.awsmap.cache import Cache
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
