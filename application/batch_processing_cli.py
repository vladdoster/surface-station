#!/usr/bin/env python2

# Author: Vlad Doster (mvdoster (at) gmail.com)
# Small cli tool to run different ways to batch process datasets

import click


@click.group()
@click.option(
    "-d",
    "--directory-to-process",
    required=True,
    show_default=True,
    help="Pass a captured_datasets directory",
)
@click.pass_context
def cli(ctx, directory_to_process):
    ctx.obj["DIRECTORY_TO_PROCESS"] = directory_to_process


@cli.command()
@click.pass_context
def google_cloud_ml(ctx):
    """Batch process images via Google Cloud ML from a captured dataset"""
    click.echo(
        "Batch processing *.jpg images in {}".format(ctx.obj["DIRECTORY_TO_PROCESS"])
    )
    # For each file, send off to the google cloud and then save to a directory inside 1


if __name__ == "__main__":
    cli(obj={})
