import math
import re
import json
import csv
import requests
import os
import click
import yaml
import io
from effectai import Client, campaign


def parse_campaign(campaign_str):
    """Extract and parse frontmatter and insturctions from campaign."""
    (_, frontmatter, instructions) = re.split("---+", campaign_str)
    campaign = yaml.safe_load(frontmatter)
    campaign['instructions'] = instructions
    return campaign


@click.group()
def cli():
    pass


@cli.command()
@click.option("--file", help="Directory the campaign is in.")
def publish(file):
    """Publish a campaign on Effect Network"""
    with io.open(file, "r") as f:
        campaign_str = f.read()
    campaign = parse_campaign(campaign_str)
    print(campaign)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


@cli.command()
@click.option("--dir", help="Campaign directory.")
@click.option("--outfile", help="CSV file name of the output.")
def upload_ipfs(dir, outfile):
    """Upload a directory to ipfs."""
    files_per_batch = 2
    num_files = 0
    batches = list()
    for batch in chunks(os.listdir(dir), files_per_batch):
        batch_files = {}
        for f in batch:
            item = open(dir + f, "rb")
            batch_files[f] = item
        batches.append(batch_files)
        num_files += len(batch)
            
    num_batches = math.ceil(num_files / files_per_batch)
    click.echo(f"Uploading {num_files} files found in {dir} in {num_batches} batches...")
    input("Press Enter to continue...")
    
    all_responses = ''
    for batch in batches:
        resp = requests.post("https://ipfs.effect.ai/api/v0/add?pin=true", files=batch)
        all_responses += resp.text

    hashes = list()
    for line in all_responses.split("\n"):
        if line:
            ipfs_obj = json.loads(line)
            click.echo(f"Uploading {ipfs_obj['Hash']}")
            hashes.append((ipfs_obj["Name"], ipfs_obj["Hash"]))

    with open(outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for hash in hashes:
            writer.writerow(hash)
    print(f"Write data to {outfile}")


if __name__ == "__main__":
    cli()
