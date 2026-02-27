import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
COLL = "atoms"
SLUG = "simulated-robot"

async def run_workflow():
    async with httpx.AsyncClient(timeout=120.0) as client:
        print(f"--- STARTING WORKFLOW SIMULATION: {datetime.now()} ---")
        
        # 1. CREATE
        print("\n[1] Creating Project...")
        r = await client.post(f"{BASE_URL}/projects/", json={"name": "Simulated Robot", "collection": COLL, "slug": SLUG})
        print(f"Response: {r.status_code}")

        # 2. CHAT INIT
        print("\n[2] Initializing IA Interview...")
        r = await client.post(f"{BASE_URL}/{COLL}/{SLUG}/init")
        if r.status_code == 200:
            print(f"IA: {r.json().get('content')[:100]}...")
        else:
            print(f"Status: {r.status_code}")

        # 3. MESSAGE
        print("\n[3] Sending Technical Context...")
        r = await client.post(f"{BASE_URL}/{COLL}/{SLUG}/message", json={"content": "Es un robot basado en ESP32 con motores NEMA17 y control cinemático inverso."})
        print(f"IA: {r.json().get('content')[:100]}...")

        # 4. DRAFT
        print("\n[4] Generating Markdown Draft...")
        r = await client.post(f"{BASE_URL}/{COLL}/{SLUG}/draft")
        draft = r.json().get("content")
        print(f"Draft Length: {len(draft) if draft else 0} chars")

        # 5. PERSIST
        print("\n[5] Persisting Working Copy...")
        r = await client.post(f"{BASE_URL}/{COLL}/{SLUG}/persist", json={"content": draft})
        print(f"Status: {r.status_code}")

        # 6. STUDIO SUGGEST
        print("\n[6] Suggesting Photographic Shots...")
        r = await client.post(f"{BASE_URL}/{COLL}/{SLUG}/studio/suggest")
        print(f"Suggested {len(r.json())} shots.")

        # 7. TRANSLATE
        print("\n[7] Generating English Translation...")
        r = await client.post(f"{BASE_URL}/{COLL}/{SLUG}/translate/draft", json={"from_scratch": True})
        en_draft = r.json().get("content")
        print(f"EN Draft Length: {len(en_draft) if en_draft else 0} chars")

        # 8. PERSIST EN
        print("\n[8] Persisting English Version...")
        r = await client.post(f"{BASE_URL}/{COLL}/{SLUG}/translate/persist", json={"content": en_draft})
        print(f"Status: {r.status_code}")

        # 9. PROMOTE
        print("\n[9] Promoting to Portfolio (Final Step)...")
        r = await client.post(f"{BASE_URL}/{COLL}/{SLUG}/promote")
        print(f"Promote Response: {r.status_code}")

        print(f"\n--- WORKFLOW SIMULATION COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    asyncio.run(run_workflow())
