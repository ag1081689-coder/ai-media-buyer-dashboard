import os

USERS = {
    "admin": {
        "password": os.getenv("ADMIN_PASSWORD", ""),
        "allowed_accounts": ["*"],
        "role": "admin"
    },
    "memmar degla": {
        "password": os.getenv("MEMMAR_DEGLA_PASSWORD", ""),
        "allowed_accounts": ["act_3654875044793620"],
        "role": "client_viewer"
    }
}

ACCOUNT_MODES = {
    "act_3654875044793620": "real_estate_leads"
}

DEFAULT_ACCOUNT_MODE = "sales"


def get_account_mode(account_id):
    return ACCOUNT_MODES.get(str(account_id), DEFAULT_ACCOUNT_MODE)


def filter_accounts_for_user(ad_accounts, allowed_accounts):
    if "*" in allowed_accounts:
        return ad_accounts

    return [
        account for account in ad_accounts
        if str(account.get("id")) in allowed_accounts
    ]
