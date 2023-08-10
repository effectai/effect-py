import pyntelope
from pyntelope.types import primitives
from . import types

def create(client, ipfs_hash: str, reward: str, task_time: int = 3600):
    client.require_auth()

    v1 = types.Variant.from_dict(
        ['name', pyntelope.types.Name(client.auth.actor)],
        types_=['address', 'name']
    )

    v2 = types.Struct([pyntelope.types.Uint8(0),
                       pyntelope.types.String(ipfs_hash)])

    v3 = pyntelope.types.Uint32(task_time)
    v4 = types.Struct(
        [pyntelope.types.Asset(reward),
         pyntelope.types.Name(client.config['token_contract'])]
    )

    v5 = pyntelope.types.Array.from_dict([], type_=types.Struct)
    v6 = pyntelope.types.Name(client.auth.actor)
    v7 = pyntelope.types.Uint8(0)

    data = [
        pyntelope.Data(name='owner', value=v1),
        pyntelope.Data(name='content', value=v2),
        pyntelope.Data(name='max_task_time', value=v3),
        pyntelope.Data(name='reward', value=v4),
        pyntelope.Data(name='qualis', value=v5),
        pyntelope.Data(name='payer', value=v6),
        pyntelope.Data(name='sig', value=v7),
    ]
    action = pyntelope.Action(
        account=client.config['tasks_contract'],
        name='mkcampaign',
        data=data,
        authorization=[client.auth],
    )
    resp = client.send_transaction(actions=[action])
    return resp

def delete(client, campaign_id: int):
    client.require_auth()

    data = [
        pyntelope.Data(name='campaign_id',value=pyntelope.types.Uint32(campaign_id)),
        pyntelope.Data(
            name='owner',
            value=types.Variant.from_dict(
                ['name', pyntelope.types.Name(client.auth.actor)],
                types_=['address', 'name']
            )
        ),
        pyntelope.Data(name='campaign_id', value=pyntelope.types.Uint8(0))
    ]
    action = pyntelope.Action(
        account=client.config['tasks_contract'],
        name='rmcampaign',
        data=data,
        authorization=[client.auth],
    )
    resp = client.send_transaction([action])
    return resp
