import os
import json
import glob
from os import path, mkdir
from shutil import rmtree


class Cache:
    def __init__(self, verbose=False):
        self.cache_dir = "/tmp/awsmap-cache"
        self.verbose = verbose
        if not path.exists(self.cache_dir):
            mkdir(self.cache_dir)

    def p(self, msg):
        if self.verbose:
            print(msg)

    def clear(self):
        rmtree(self.cache_dir)
        # for f in glob.glob("{}/**".format(self.cache_dir)):
        #     os.remove(f)

    def get_cache(self, cache_key):
        cache_file = "{}/{}".format(self.cache_dir, cache_key)
        if '/' in cache_key:
            account_dir = "{}/{}".format(self.cache_dir, cache_key.split("/")[0])
            if not path.exists(account_dir):
                mkdir(account_dir)

        if not path.exists(cache_file):
            print(cache_file)
            return False
        else:
            return json.loads(open(cache_file).read())

    def set_cache(self, cache_key, data):
        cache_file = "{}/{}".format(self.cache_dir, cache_key)
        self.p("Setting cache: {}".format(cache_file))
        f = open(cache_file, 'w')
        j_data = json.dumps(data, indent=4, sort_keys=True, default=str)
        f.write(j_data)
        return json.loads(j_data)
