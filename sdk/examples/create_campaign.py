import os
from effectai import Client
from effectai import campaign

e = Client("jungle4")

e.login(
    "efxefxefxefx",  # your account name
    "active",  # account permission
    os.environ["EOS_KEY"],
)


r = campaign.create(
    e,
    {
        "title": "Answer questions in a conversational style",
        "description": "You are contributing to a dataset for conversational style chatbots.",
        "instructions": "Write your answers in a casual style like you would on Whatsapp.",
        "template": "<h1>Placeholder</h1>",
    },
    "1.0064 EFX",
)
print(r)
print(e.get_campaigns())
