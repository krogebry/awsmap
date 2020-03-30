#!/usr/bin/env python
import os
import sys
import yaml
import click
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.awsmap.map import Map
from lib.awsmap.cache import Cache


@click.group(invoke_without_command=True)
def cli(ctx, debug):
    """CLI things"""


@cli.command()
@click.option('-d', '--dryrun', default=False, type=bool, is_flag=True)
@click.option('-v', '--verbose', default=False, type=bool, is_flag=True)
@click.option('-r', '--region_name', default=False)
def map(dryrun, verbose, region_name):
    """Mapp stuff out"""
    mapper = Map(dryrun, verbose)
    mapper.compile(region_name=region_name)


@cli.command()
def clear_cache():
    c = cache.Cache()
    c.clear()
    print("Cache has been cleared.")


cli = click.CommandCollection(sources=[cli])

if __name__ == '__main__':
    cli()
