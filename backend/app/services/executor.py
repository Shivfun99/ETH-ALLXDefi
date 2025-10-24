"""
executor.py

Optional: functions that prepare/send transactions to reduce leverage.
VERY IMPORTANT: sending on-chain transactions requires signing keys and is sensitive.
This module will only attempt to send txs if PRIVATE_KEY and ETH_RPC are set.
Use with care and require explicit user opt-in.
"""

from web3 import Web3, HTTPProvider
from app.config import settings
from typing import Optional

def get_web3() -> Optional[Web3]:
    if not settings.ETH_RPC:
        return None
    w3 = Web3(HTTPProvider(settings.ETH_RPC))
    return w3

def build_reduce_leverage_tx(user_addr: str, position_id: str, reduce_to: float) -> dict:
    """
    Pseudocode tx builder. In production, you'd call a protocol-specific helper contract.
    Returns a dictionary representing the tx (to, data, value, gas, etc.)
    """
    # Example: this is a placeholder - replace with real contract call encoding
    tx = {
        "to": "0xProtocolHelperContractAddress",  # replace
        "data": "0x",  # ABI-encoded data for helper contract
        "value": 0
    }
    return tx

def send_signed_tx(tx: dict) -> str:
    w3 = get_web3()
    if w3 is None:
        raise RuntimeError("ETH_RPC not configured — cannot send tx")

    if not settings.PRIVATE_KEY:
        raise RuntimeError("PRIVATE_KEY not set — refusing to sign/send tx")

    acct = w3.eth.account.from_key(settings.PRIVATE_KEY)
    # Build base tx with gas, nonce etc - you may want to estimate gas in production
    base_tx = {
        "from": acct.address,
        "to": tx.get("to"),
        "value": tx.get("value", 0),
        "data": tx.get("data", b""),
        "gas": tx.get("gas", 300000),
        "gasPrice": w3.to_wei("30", "gwei"),
        "nonce": w3.eth.get_transaction_count(acct.address)
    }
    signed = acct.sign_transaction(base_tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()
