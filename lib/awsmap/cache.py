import os
import json
import glob
from os import path
from os import environ


class Cache:
    def __init__(self, verbose=False):
        self.cache_dir = "/tmp/cache"
        self.verbose = verbose

    def p(self, msg):
        if self.verbose:
            print(msg)

    def clear(self):
        for f in glob.glob(f"{self.cache_dir}/*"):
            os.remove(f)

    def get_cache(self, cache_key):
        cache_file = f"{self.cache_dir}/{cache_key}"
        if not path.exists(cache_file):
            return False
        else:
            return json.loads(open(cache_file).read())

    def set_cache(self, cache_key, data):
        cache_file = f"{self.cache_dir}/{cache_key}"
        self.p(f"Setting cache: {cache_file}")
        f = open(cache_file, 'w')
        j_data = json.dumps(data, indent=4, sort_keys=True, default=str)
        f.write(j_data)
        return json.loads(j_data)
