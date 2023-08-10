import pyntelope.types
from . import types

def make_token_index(client):
    b = bytes(pyntelope.types.Name(client.config['token_contract']))
    b += bytes([1])
    b += bytes(pyntelope.types.Name(client.auth.actor))
    b += bytes([0]*(32 - len(b)))
    return b

def get(client):
    client.require_auth()
    idx = make_token_index(client).hex()

    rows = client.net.get_table_rows(
        client.config['vaccount_contract'],
        'account',
        client.config['vaccount_contract'],
        index_position = 2,
        key_type = 'sha256',
        lower_bound = idx,
        upper_bound = idx,
    )

    # TODO: return the ID of the token client's contract and symbol in
    # case of multiple rows
    return rows[0]['id']

def open(client):
    client.require_auth()

    data = [
        pyntelope.Data(
            name='acc',
            value=types.Variant.from_dict(
                ['name', pyntelope.types.Name(client.auth.actor)],
                types_=['address', 'name']
            )
        ),
        pyntelope.Data(
            name='symbol',
            value=types.Struct(
                [pyntelope.types.Symbol(client.config['token_symbol']),
                 pyntelope.types.Name(client.config['token_contract'])]
            )
        ),
        pyntelope.Data(
            name='payer',
            value=pyntelope.types.Name(client.auth.actor)
        )
    ]

    action = pyntelope.Action(
        account=client.config['vaccount_contract'],
        name='open',
        data=data,
        authorization=[client.auth],
    )

    resp = client.send_transaction([action])
    return resp
