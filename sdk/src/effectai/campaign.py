import pyntelope
from pyntelope.types import primitives, Uint32, Uint64, Uint8, Asset, Name, String
from . import types
from pydantic import BaseModel
from typing import Optional
from . import vaccount


class Campaign(BaseModel):
    version: float = 1.1
    title: str
    description: str
    instructions: str
    template: str
    input_schema: Optional[str]
    output_schema: Optional[str]
    image: Optional[str]
    category: Optional[str]
    example_task: Optional[dict]
    estimated_time: Optional[int]


def mkcampaign_action(client, ipfs_hash: str, reward: str, task_time: int):
    client.require_auth()

    v1 = types.Variant.from_dict(
        ["name", pyntelope.types.Name(client.auth.actor)], types_=["address", "name"]
    )

    v2 = types.Struct([pyntelope.types.Uint8(0), pyntelope.types.String(ipfs_hash)])

    v3 = pyntelope.types.Uint32(task_time)
    v4 = types.Struct(
        [pyntelope.types.Asset(reward), pyntelope.types.Name(client.config["token_contract"])]
    )

    # TOOD: v5 is qualifications
    v5 = pyntelope.types.Array.from_dict([], type_=types.Struct)
    v6 = pyntelope.types.Name(client.auth.actor)
    # TODO: v7 is the optional BSC signature
    v7 = pyntelope.types.Uint8(0)

    data = [
        pyntelope.Data(name="owner", value=v1),
        pyntelope.Data(name="content", value=v2),
        pyntelope.Data(name="max_task_time", value=v3),
        pyntelope.Data(name="reward", value=v4),
        pyntelope.Data(name="qualis", value=v5),
        pyntelope.Data(name="payer", value=v6),
        pyntelope.Data(name="sig", value=v7),
    ]
    action = pyntelope.Action(
        account=client.config["tasks_contract"],
        name="mkcampaign",
        data=data,
        authorization=[client.auth],
    )

    return action


def editcampaign_action(client, campaign_id: int, ipfs_hash: str, reward: str):
    client.require_auth()

    v1 = types.Variant.from_dict(
        ["name", pyntelope.types.Name(client.auth.actor)], types_=["address", "name"]
    )

    v2 = types.Struct([pyntelope.types.Uint8(0), pyntelope.types.String(ipfs_hash)])

    # v3 = pyntelope.types.Uint32(task_time)
    v4 = types.Struct(
        [pyntelope.types.Asset(reward), pyntelope.types.Name(client.config["token_contract"])]
    )

    # TOOD: v5 is qualifications
    v5 = pyntelope.types.Array.from_dict([], type_=types.Struct)
    v6 = pyntelope.types.Name(client.auth.actor)
    # TODO: v7 is the optional BSC signature
    v7 = pyntelope.types.Uint8(0)

    data = [
        pyntelope.Data(name="campaign_id", value=pyntelope.types.Uint32(campaign_id)),
        pyntelope.Data(name="owner", value=v1),
        pyntelope.Data(name="content", value=v2),
        pyntelope.Data(name="paused", value=pyntelope.types.Bool(False)),
        # TODO: add max_task_time
        # pyntelope.Data(name="max_task_time", value=v3),
        pyntelope.Data(name="reward", value=v4),
        pyntelope.Data(name="qualis", value=v5),
        pyntelope.Data(name="payer", value=v6),
    ]
    action = pyntelope.Action(
        account=client.config["tasks_contract"],
        name="editcampaign",
        data=data,
        authorization=[client.auth],
    )

    return action


def create(client, campaign_data: dict, reward: str = "0.0000 EFX", task_time: int = 3600):
    camp = Campaign(**campaign_data).dict()
    ipfs_hash = client.ipfs.pin_json(camp)
    action = mkcampaign_action(client, ipfs_hash, reward, task_time)
    resp = client.send_transaction(actions=[action])
    return resp


def edit(client, campaign_id: int, campaign_data: dict, reward: str = "0.0000 EFX"):
    camp = Campaign(**campaign_data).dict()
    ipfs_hash = client.ipfs.pin_json(camp)
    action = editcampaign_action(client, campaign_id, ipfs_hash, reward)
    resp = client.send_transaction(actions=[action])
    return resp


def delete(client, campaign_id: int):
    client.require_auth()

    data = [
        pyntelope.Data(name="campaign_id", value=pyntelope.types.Uint32(campaign_id)),
        pyntelope.Data(
            name="owner",
            value=types.Variant.from_dict(
                ["name", pyntelope.types.Name(client.auth.actor)], types_=["address", "name"]
            ),
        ),
        pyntelope.Data(name="sig", value=pyntelope.types.Uint8(0)),
    ]
    action = pyntelope.Action(
        account=client.config["tasks_contract"],
        name="rmcampaign",
        data=data,
        authorization=[client.auth],
    )
    resp = client.send_transaction([action])
    return resp


def mkbatch_action(client, id_: int, campaign_id: int, ipfs_hash: str, reps: int):
    data = [
        pyntelope.Data(name="id", value=pyntelope.types.Uint32(id_)),
        pyntelope.Data(name="campaign_id", value=pyntelope.types.Uint32(campaign_id)),
        pyntelope.Data(
            name="content",
            value=types.Struct([pyntelope.types.Uint8(0), pyntelope.types.String(ipfs_hash)]),
        ),
        pyntelope.Data(name="repetitions", value=pyntelope.types.Uint32(reps)),
        pyntelope.Data(name="payer", value=pyntelope.types.Name(client.auth.actor)),
        pyntelope.Data(name="sig", value=pyntelope.types.Uint8(0)),
    ]
    action = pyntelope.Action(
        account=client.config["tasks_contract"],
        name="mkbatch",
        data=data,
        authorization=[client.auth],
    )
    return action


def get_batch_pk(batch_id: int, campaign_id: int):
    return Uint64.from_bytes(bytes(Uint32(batch_id)) + bytes(Uint32(campaign_id))).value


def publishbatch_action(client, batch_pk: int, num_tasks: int):

    data = [
        pyntelope.Data(name="batch_id", value=Uint64(batch_pk)),
        pyntelope.Data(name="num_tasks", value=Uint32(num_tasks)),
        pyntelope.Data(name="sig", value=Uint8(0)),
    ]
    action = pyntelope.Action(
        account=client.config["tasks_contract"],
        name="publishbatch",
        data=data,
        authorization=[client.auth],
    )
    return action


# TODO: move this action to a more generic place in the codebase
def make_transfer_action(client, from_acc: str, to_acc: str, quantity: str, memo: str):
    client.require_auth()

    data = [
        pyntelope.Data(name="from", value=Name(from_acc)),
        pyntelope.Data(name="to", value=Name(to_acc)),
        pyntelope.Data(name="quantity", value=Asset(quantity)),
        pyntelope.Data(name="memo", value=String(memo)),
    ]

    action = pyntelope.Action(
        account=client.config["token_contract"],
        name="transfer",
        data=data,
        authorization=[client.auth],
    )

    return action


# Reward is per task
def create_batch(client, campaign_id: int, data: list, reward: str, repetitions: int = 1):
    # TOOD: auto determine reward
    client.require_auth()
    ipfs_hash = client.ipfs.pin_json(data)

    batches = client.get_batches(campaign_id)
    last_batch_id = -1 if not batches else batches[-1]["id"]
    batch_id = last_batch_id + 1
    batch_pk = get_batch_pk(batch_id, campaign_id)

    reward_asset = Asset(reward)
    total_reward_value = (int(reward_asset.get_int_digits()) + 1) * len(data) * repetitions
    total_reward = (
        str(total_reward_value)
        + "."
        + "0" * reward_asset.get_precision()
        + " "
        + reward_asset.get_name()
    )

    create_action = mkbatch_action(client, batch_id, campaign_id, ipfs_hash, repetitions)
    transfer_action = make_transfer_action(
        client, client.auth.actor, client.config["tasks_contract"], total_reward, str(batch_pk)
    )
    publish_action = publishbatch_action(client, batch_pk, len(data))

    resp = client.send_transaction([create_action, transfer_action, publish_action])
    return resp


def delete_batch(client, campaign_id: int, batch_id: int):
    data = [
        pyntelope.Data(name="id", value=pyntelope.types.Uint32(batch_id)),
        pyntelope.Data(name="campaign_id", value=pyntelope.types.Uint32(campaign_id)),
        pyntelope.Data(name="sig", value=pyntelope.types.Uint8(0)),
    ]
    action = pyntelope.Action(
        account=client.config["tasks_contract"],
        name="rmbatch",
        data=data,
        authorization=[client.auth],
    )
    resp = client.send_transaction([action])
    return resp


def get(client, id):
    return client.net.get_table_rows(
        client.config["tasks_contract"],
        "campaign",
        client.config["tasks_contract"],
        lower_bound=id,
        upper_bound=id,
    )[0]
