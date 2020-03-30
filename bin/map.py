#!/usr/bin/env python
import os
import sys
import yaml
import click
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.awsmap.map import Map


@click.group(invoke_without_command=True)
def cli(ctx, debug):
    """CLI things"""


@cli.command()
@click.option('-d', '--dryrun', default=False, type=bool, is_flag=True)
@click.option('-v', '--verbose', default=False, type=bool, is_flag=True)
def map(dryrun, verbose):
    """Mapp stuff out"""


@cli.command()
def clear_cache():
    c = cache.Cache()
    c.clear()
    print("Cache has been cleared.")


cli = click.CommandCollection(sources=[cli])

if __name__ == '__main__':
    cli()
