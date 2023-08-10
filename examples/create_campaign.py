from effect_sdk.effect import Client
from effect_sdk import campaign

e = Client("jungle4")

e.login(
    'efxefxefxefx', # your account name
    'active', # account permission
    '<your private key>'
)

print(campaign.create(e, 'ipfshashhere', '1.0032 EFX'))
print(e.get_campaigns())
