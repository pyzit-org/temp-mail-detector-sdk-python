BASE_URL = "https://api-tempmail.pyzit.com/v1"
CHECK_URL = BASE_URL + "/validate/check/"
DETAILED_URL = BASE_URL + "/validate/detailed/"
BULK_URL = BASE_URL + "/validate/bulk/"

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
DETAILED_PAYLOAD = {
    "email": "x@new-domain.io",
    "domain": "new-domain.io",
    "is_disposable": True,
    "status": "disposable",
    "reputation_score": 0.0,
    "risk_level": "high",
    "recommendation": "reject",
    "details": {
        "reputation": {
            "reputation_score": 0.0,
            "is_disposable": True,
            "disposable_confidence": 0.79,
            "risk_level": "high",
            "recommendation": "reject",
        },
        "signals": {
            "positive": [],
            "negative": ["no_mx_records", "new_domain"],
            "neutral": ["limited_history"],
        },
        "dns_intelligence": {
            "has_mx": True,
            "mx_records": [
                {
                    "priority": 5,
                    "exchange": "mail1.example.com",
                    "ips": ["172.65.182.103"],
                },
                {
                    "priority": 10,
                    "exchange": "mail2.example.com",
                    "ips": ["172.65.182.104"],
                },
            ],
            "has_a_record": True,
            "has_spf": True,
            "has_dmarc": False,
            "error": None,
        },
        "stability": {
            "stability_score": 0.2,
            "domain_age_days": 0,
            "is_new_domain": True,
            "risk_factors": ["newly_observed_domain"],
        },
    },
}
BULK_PAYLOAD = {
    "results": {
        "hi@pyzit.com": False,
        "x@mailnator.com": True,
    },
    "processed": 2,
}
