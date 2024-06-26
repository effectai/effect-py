"""Effect AI CLI."""
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


def parse_campaign(filename, campaign_str):
    """Extract and parse frontmatter and insturctions from campaign."""
    (_, frontmatter, instructions) = re.split("---+", campaign_str)
    camp = yaml.safe_load(frontmatter)
    camp["instructions"] = instructions
    if not camp["template"].startswith("<html>"):
        template_path = os.path.dirname(filename) + "/" + camp["template"]
        with open(template_path, "r") as f:
            camp["template"] = f.read()
    return camp


@click.group()
def cli():
    """Start CLI entry point."""
    pass


@cli.command()
@click.option("--file", help="Directory the campaign is in.")
def publish(file):
    """Publish a campaign on Effect Network."""
    e = Client("jungle4")

    e.login(
        "efxefxefxefx",  # your account name
        "active",  # account permission
        os.environ["EOS_KEY"],
    )

    with io.open(file, "r") as f:
        campaign_str = f.read()
    camp = parse_campaign(file, campaign_str)

    res = campaign.create(e, camp)

    print(res)


@cli.command()
@click.option("--file", help="CSV file for batch data.")
@click.option("--campaign-id", help="Campaign ID.")
def add_batch(file, campaign_id):
    e = Client("jungle4")

    e.login(
        "efxefxefxefx",  # your account name
        "active",  # account permission
        os.environ["EOS_KEY"],
    )

    with open(file, "r") as f:
        reader = csv.reader(f)
        labels = next(reader, None)
        data = [dict(zip(labels, line)) for line in reader]

    click.echo(f"Creating batch with {len(data)} tasks")
    input("Press Enter to continue...")

    resp = campaign.create_batch(e, campaign_id, data, "0.0000 EFX")
    print(resp)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


ipfs_url = "https://ipfs.effect.ai/api/v0/add?pin=true"


@cli.command()
@click.option("--dir", help="Campaign directory.")
@click.option("--outfile", help="CSV file name of the output.")
def upload_ipfs(dir, outfile):
    """Upload a directory to ipfs."""
    files_per_batch = 50
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
    click.echo(f"Uploading {num_files} files found in {dir} " + f"in {num_batches} batches...")
    input("Press Enter to continue...")

    all_responses = ""
    for i, batch in enumerate(batches):
        click.echo(f"> Uploading batch {i}")
        resp = requests.post(ipfs_url, files=batch)
        all_responses += resp.text

    hashes = list()
    for line in all_responses.split("\n"):
        if line:
            ipfs_obj = json.loads(line)
            click.echo(f"Uploading {ipfs_obj['Hash']}")
            hashes.append((ipfs_obj["Name"], ipfs_obj["Hash"]))

    with open(outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(("filename", "cid"))
        for hash in hashes:
            writer.writerow(hash)
    print(f"Write data to {outfile}")


if __name__ == "__main__":
    cli()
