#!/usr/bin/env python
import os
import sys
import yaml
import click
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.awsmap.mappers.vpc import VPCMapper
from lib.awsmap.mappers.subnet import SubnetMapper
from lib.awsmap.cache import Cache


@click.group(invoke_without_command=True)
def cli(ctx, debug):
    """CLI things"""


@cli.command()
@click.option('-d', '--dryrun', default=False, type=bool, is_flag=True)
@click.option('-v', '--verbose', default=False, type=bool, is_flag=True)
@click.option('-r', '--profile_name', default="default")
@click.option('-r', '--region_name', default="us-east-1")
def vpcs(dryrun, verbose, profile_name, region_name):
    """Map VPC and peer connections."""
    mapper = VPCMapper(dryrun, verbose)
    mapper.compile(profile_name=profile_name, region_name=region_name)


@cli.command()
@click.option('-d', '--dryrun', default=False, type=bool, is_flag=True)
@click.option('-v', '--verbose', default=False, type=bool, is_flag=True)
@click.option('-r', '--profile_name', default="default")
@click.option('-r', '--region_name', default="us-east-1")
def subnets(dryrun, verbose, profile_name, region_name):
    """Map VPC and peer connections."""
    # vpc_id = "vpc-5e8edb39"
    vpc_id = "vpc-029e3142c2d62e29b"
    mapper = SubnetMapper(dryrun, verbose)
    mapper.compile(vpc_id, profile_name=profile_name, region_name=region_name)


@cli.command()
def clear_cache():
    c = cache.Cache()
    c.clear()
    print("Cache has been cleared.")


cli = click.CommandCollection(sources=[cli])

if __name__ == '__main__':
    cli()
