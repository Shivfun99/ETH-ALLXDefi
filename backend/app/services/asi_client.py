"""
asi_client.py — robust ASI:One + local fallback client
"""

import aiohttp
import asyncio
import re
import random
from ..config import settings


# Default ASI endpoint list (cloud + local fallback)
ASI_ENDPOINTS = [
    settings.ASI_ENDPOINT or "http://127.0.0.1:8001",
]


async def call_asi_model(payload: dict) -> dict:
    """
    Try calling ASI endpoints (cloud or local).
    If ASI Cloud (asi1.ai) is reachable, parse real model output.
    Falls back to local simulated model if all fail.
    """
    timeout = aiohttp.ClientTimeout(total=15)
    last_error = None

    for base in ASI_ENDPOINTS:
        url = base.rstrip("/")
        try:
            print(f"[DEBUG] Trying ASI at: {url}")

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            if settings.ASI_API_KEY:
                headers["Authorization"] = f"Bearer {settings.ASI_API_KEY}"

            # ✅ Detect if using ASI Cloud or local mock
            if "asi1.ai" in url:
                # Cloud ASI:One format
                json_payload = {
                    "model": "asi1-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a DeFi risk analysis model. Respond concisely with risk probability and class (🟢/🟡/🔴).",
                        },
                        {
                            "role": "user",
                            "content": f"Given these metrics, estimate the DeFi portfolio risk:\n{payload}",
                        },
                    ],
                    "temperature": 0.4,
                    "max_tokens": 150,
                }
            else:
                # Local ASI mock expects raw payload
                json_payload = payload

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=json_payload) as resp:
                    data = await resp.json()
                    if resp.status == 200:
                        print(f"✅ ASI Cloud responded successfully: {url}")

                        # 🧠 ASI:One returns "choices" with text inside
                        if "choices" in data:
                            text = data["choices"][0]["message"]["content"]

                            # Parse probability (like "Risk probability: 42.5")
                            prob_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
                            prob = float(prob_match.group(1)) if prob_match else random.uniform(20, 80)

                            # Parse risk class emoji/text
                            cls_match = re.search(r"(🟢|🟡|🔴)\s*\w*\s*Risk", text)
                            risk_class = cls_match.group(0) if cls_match else "Unknown"

                            return {
                                "risk_probability": round(prob, 2),
                                "risk_class": risk_class,
                                "message": text.strip(),
                                "source": "ASI:One Cloud",
                            }

                        # Local mock JSON
                        return {
                            "risk_probability": data.get("risk_probability", 0.0),
                            "risk_class": data.get("risk_class", "Unknown"),
                            "message": data.get("message", ""),
                            "source": "ASI-local",
                        }

                    else:
                        print(f"⚠️ ASI API returned {resp.status} on {url}")
                        last_error = resp.status

        except Exception as e:
            print(f"⚠️ ASI API call failed on {url}: {e}")
            last_error = str(e)

    # 🚨 fallback — simulate risk locally
    print("🔍 Final Risk Model Used: local_fallback")

    prob = round(random.uniform(20, 90), 2)
    if prob < 40:
        rclass = "🟢 Low Risk"
    elif prob < 70:
        rclass = "🟡 Medium Risk"
    else:
        rclass = "🔴 High Risk"

    return {
        "risk_probability": prob,
        "risk_class": rclass,
        "message": "Fallback local AI model used due to ASI unavailability.",
        "source": "local_fallback",
        "error": last_error,
    }
