# awsmap
Mapping AWS stuff

# Requirements

* dot
  * brew install graphviz
* python3.6
  * pip install -U -f ./[requirements.txt](./requirements.txt)

# Usage

```
Usage: map.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  clear-cache     Clear cached data files.
  docker-compose  Map out a docker-compose yaml file.
  network         Map VPC and SubNets with peer connections.
  subnets         Map Subnets and peer connections.
  vpcs            Map VPC and peer connections.
```