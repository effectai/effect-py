import pydantic
import pyntelope

from effectai import config
from effectai import types
from effectai import vaccount
from effectai.ipfs import IPFS
from pyntelope.types import Uint32, Uint64

class Client:
    def __init__(self, net: str = "jungle4"):
        auth = None
        __key = None

        self.network_name = net
        if net == "jungle4" or net == "jungle":
            self.network_name = "jungle4"
            self.net = pyntelope.Jungle4Testnet()
        elif net == "mainnet":
            self.net = pyntelope.EosMainnet()
        else:
            raise ValueError("The network should be 'jungle4' or 'mainnet'.")
        self.config = config.presets[self.network_name]
        self.ipfs = IPFS(self.config["ipfs_url"])

    def require_auth(self):
        if self.auth == None:
            raise ValueError("Login required.")

    def login(self, actor, permission, key):
        self.auth = pyntelope.Authorization(actor=actor, permission=permission)
        self.__key = key
        self.config["tasks_vaccount_id"] = vaccount.get(self, self.config["tasks_contract"])
        self.config["auth_vaccount_id"] = vaccount.get(self, actor)

    def get_settings(self):
        return self.net.get_table_rows(
            self.config["tasks_contract"],
            "settings",
            self.config["tasks_contract"],
        )

    def get_campaigns(self):
        return self.net.get_table_rows(
            self.config["tasks_contract"],
            "campaign",
            self.config["tasks_contract"],
        )

    def get_batches(self, campaign_id: int):
        lower = bytes(Uint32(0)) + bytes(Uint32(campaign_id))
        upper = bytes(Uint32(4294967295)) + bytes(Uint32(campaign_id))

        return self.net.get_table_rows(
            self.config["tasks_contract"],
            "batch",
            self.config["tasks_contract"],
            lower_bound=Uint64.from_bytes(lower).value,
            upper_bound=Uint64.from_bytes(upper).value,
        )

    def send_transaction(self, actions):
        raw_tx = pyntelope.Transaction(actions=actions)
        linked_tx = raw_tx.link(net=self.net)
        signed_tx = linked_tx.sign(key=self.__key)
        return signed_tx.send()
