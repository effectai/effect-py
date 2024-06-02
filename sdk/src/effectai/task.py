import pyntelope
from pyntelope.types import primitives, Uint32, Uint64, Uint8, String
from . import types
from pydantic import BaseModel
from typing import Optional
from . import vaccount


def reserve(client, campaign_id: int):
    data = [
        pyntelope.Data(name="campaign_id", value=Uint32(campaign_id)),
        pyntelope.Data(name="account_id", value=Uint32(client.config["auth_vaccount_id"])),
        pyntelope.Data(name="quali_assets", value=Uint8(0)),
        pyntelope.Data(name="payer", value=pyntelope.types.Name(client.auth.actor)),
        pyntelope.Data(name="sig", value=pyntelope.types.Uint8(0)),
    ]
    action = pyntelope.Action(
        account=client.config["tasks_contract"],
        name="reservetask",
        data=data,
        authorization=[client.auth],
    )
    resp = client.send_transaction([action])
    return resp


def get_reservation(client, campaign_id: int):
    b = bytes(Uint32(campaign_id))
    b += bytes(Uint32(client.config["auth_vaccount_id"]))

    idx = Uint64.from_bytes(b).value

    rows = client.net.get_table_rows(
        client.config["tasks_contract"],
        "reservation",
        client.config["tasks_contract"],
        index_position=2,
        key_type="i64",
        lower_bound=idx,
        upper_bound=idx,
    )
    if not rows:
        raise ValueError("No reservation found")
    return rows[0]


def submit(client, campaign_id: int, data: str):
    reservation = get_reservation(client, campaign_id)
    data = [
        pyntelope.Data(name="campaign_id", value=Uint32(campaign_id)),
        pyntelope.Data(name="task_idx", value=Uint32(reservation["task_idx"])),
        pyntelope.Data(name="data", value=String("hello")),
        pyntelope.Data(name="account_id", value=Uint32(client.config["auth_vaccount_id"])),
        pyntelope.Data(name="payer", value=pyntelope.types.Name(client.auth.actor)),
        pyntelope.Data(name="sig", value=pyntelope.types.Uint8(0)),
    ]
    action = pyntelope.Action(
        account=client.config["tasks_contract"],
        name="submittask",
        data=data,
        authorization=[client.auth],
    )
    resp = client.send_transaction([action])
    return resp
