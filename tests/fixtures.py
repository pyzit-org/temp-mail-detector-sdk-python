BASE_URL = "https://api.pyzit.com"
CHECK_URL = BASE_URL + "/v1/tmd/check/"
DETAILED_URL = BASE_URL + "/v1/tmd/detailed/"
BULK_URL = BASE_URL + "/v1/tmd/bulk/"

CLEAN_CHECK_PAYLOAD = {
    "email": "hi@pyzit.com",
    "is_disposable": False,
    "status": "clean",
}
DISPOSABLE_CHECK_PAYLOAD = {
    "email": "user@mailnator.com",
    "is_disposable": True,
    "status": "disposable",
}
PRIVACY_RELAY_CHECK_PAYLOAD = {
    "email": "user@privaterelay.appleid.com",
    "is_disposable": False,
    "is_privacy_relay": True,
    "status": "privacy_relay",
    "relay_provider": "apple",
    "provider_name": "Apple Private Relay",
}
DETAILED_PAYLOAD = {
    "email": "user@guerrillamail.com",
    "domain": "guerrillamail.com",
    "is_disposable": False,
    "is_trusted": True,
    "classification": "trusted",
    "reputation_score": 100,
    "risk_level": "low",
    "is_valid_format": True,
    "rule_applied": "custom_whitelist",
    "details": {
        "has_mx": True,
        "mx_records": ["custom-whitelist.internal"],
        "has_a": True,
        "a_records": [],
        "has_spf": True,
        "spf_record": "v=spf1 include:custom-whitelist ~all",
        "has_dmarc": True,
        "dmarc_record": "v=DMARC1; p=none",
    },
    "status": "clean",
}
BULK_PAYLOAD = {
    "total": 2,
    "status": "mixed",
    "disposable_count": 1,
    "privacy_relay_count": 0,
    "flagged_domains": ["mailnator.com"],
    "results": [
        {
            "email": "hi@pyzit.com",
            "is_disposable": False,
            "is_privacy_relay": False,
            "status": "clean",
        },
        {
            "email": "x@mailnator.com",
            "is_disposable": True,
            "is_privacy_relay": False,
            "status": "disposable",
        },
    ],
}
BULK_WITH_RELAY_PAYLOAD = {
    "total": 3,
    "status": "mixed",
    "disposable_count": 1,
    "privacy_relay_count": 1,
    "flagged_domains": ["mailnator.com"],
    "results": [
        {
            "email": "hi@pyzit.com",
            "is_disposable": False,
            "is_privacy_relay": False,
            "status": "clean",
        },
        {
            "email": "x@mailnator.com",
            "is_disposable": True,
            "is_privacy_relay": False,
            "status": "disposable",
        },
        {
            "email": "user@privaterelay.appleid.com",
            "is_disposable": False,
            "is_privacy_relay": True,
            "status": "privacy_relay",
            "relay_provider": "apple",
            "provider_name": "Apple Private Relay",
        },
    ],
}
