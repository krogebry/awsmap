import boto3
from lib.awsmap.cache import Cache
from pprint import PrettyPrinter


class Map:
    def __init__(self, dryrun, verbose):
        self.dryrun = dryrun
        self.verbose = verbose

        self.prettyp = PrettyPrinter(indent=4)
        self.cache = Cache()
        self.graph_attr = {
            "fontsize": "80",
            "bgcolor": "#FFB6C1"
        }

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
        key = "{}/{}_{}".format(self.get_account_id(profile_name, region_name), region_name, topic)
        return key

    def _make_cache_key_with_accountid(self, account_id, region_name, topic):
        key = "{}/{}_{}".format(account_id, region_name, topic)
        return key

    def get_account_name(self, profile_name, region_name):
        """Determine Name of the AWS Account."""
        cache_key = self._make_cache_key(profile_name, "account", "name")
        account_name = self.cache.get_cache(cache_key)
        if not account_name:
            client = self._get_client('iam', profile_name=profile_name, region_name=region_name)
            data = client.list_account_aliases()

            account_name = self.cache.set_cache(cache_key, data)

        return account_name['AccountAliases'][0]

    def get_account_id(self, profile_name, region_name):
        """Determine Account ID of the AWS Account."""
        account_id = profile_name.split("-")[0]  # TODO - correct as this is specific to our setup
        cache_key = self._make_cache_key_with_accountid(account_id, "account", "id")
        account_id = self.cache.get_cache(cache_key)
        if not account_id:
            client = self._get_client('sts', profile_name=profile_name, region_name=region_name)
            data = client.get_caller_identity()

            account_id = self.cache.set_cache(cache_key, data)

        return account_id['Account']

    def _tags(self, tags):
        ro = {}
        for tag in tags:
            ro[tag['Key']] = tag['Value']
        return ro
