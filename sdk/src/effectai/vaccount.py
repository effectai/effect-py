import pyntelope.types
from pyntelope.types import Uint8, Uint32, Uint64, Name, Asset, String
from . import types


def make_token_index(client, account: str):
    b = bytes(Name(client.config["token_contract"]))
    b += bytes([1])
    b += bytes(Name(account))
    b += bytes([0] * (32 - len(b)))
    return b


def get(client, account: str = None):
    if not account:
        client.require_auth()
        account = client.auth.actor

    idx = make_token_index(client, account).hex()

    rows = client.net.get_table_rows(
        client.config["vaccount_contract"],
        "account",
        client.config["vaccount_contract"],
        index_position=2,
        key_type="sha256",
        lower_bound=idx,
        upper_bound=idx,
    )

    # TODO: return the ID of the token client's contract and symbol in
    # case of multiple rows
    return rows[0]["id"]


def open(client):
    client.require_auth()

    data = [
        pyntelope.Data(
            name="acc",
            value=types.Variant.from_dict(
                ["name", pyntelope.types.Name(client.auth.actor)], types_=["address", "name"]
            ),
        ),
        pyntelope.Data(
            name="symbol",
            value=types.Struct(
                [
                    pyntelope.types.Symbol(client.config["token_symbol"]),
                    pyntelope.types.Name(client.config["token_contract"]),
                ]
            ),
        ),
        pyntelope.Data(name="payer", value=pyntelope.types.Name(client.auth.actor)),
    ]

    action = pyntelope.Action(
        account=client.config["vaccount_contract"],
        name="open",
        data=data,
        authorization=[client.auth],
    )

    resp = client.send_transaction([action])
    return resp


def vtransfer_action(client, from_id: int, to_id: int, quantity: str, memo: str):
    client.require_auth()

    data = [
        pyntelope.Data(name="from_id", value=Uint64(from_id)),
        pyntelope.Data(name="to_id", value=Uint64(to_id)),
        pyntelope.Data(
            name="quantity",
            value=types.Struct([Asset(quantity), Name(client.config["token_contract"])]),
        ),
        pyntelope.Data(name="memo", value=String(memo)),
        pyntelope.Data(name="sig", value=Uint8(0)),
        pyntelope.Data(name="fee", value=Uint8(0)),
    ]

    action = pyntelope.Action(
        account=client.config["vaccount_contract"],
        name="vtransfer",
        data=data,
        authorization=[client.auth],
    )

    return action
