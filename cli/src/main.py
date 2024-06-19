import json
import csv
import requests
import os
import click
from effectai import Client, campaign


@click.command()
@click.option("--dir", help="Campaign directory.")
def publish(dir):
    """Publish a campaign defined in `dir`."""
    click.echo(f"Loading {dir}!")


@click.command()
@click.option("--dir", help="Campaign directory.")
@click.option("--outfile", help="CSV file name of the output.")
def upload_ipfs(dir, outfile):
    """Upload a directory to ipfs."""
    files = {}
    for f in os.listdir(dir):
        item = open(dir + f, "rb")
        files[f] = item
    click.echo(f"Uploading {len(files)} filed found in {dir}...")
    input("Press Enter to continue...")
    response = requests.post("https://ipfs.effect.ai/api/v0/add?pin=true", files=files)
    hashes = list()
    for line in response.text.split("\n"):
        if line:
            ipfs_obj = json.loads(line)
            hashes.append((ipfs_obj["Name"], ipfs_obj["Hash"]))

    with open(outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for hash in hashes:
            writer.writerow(hash)
    print(f"Write data to {outfile}")


if __name__ == "__main__":
    upload_ipfs()
