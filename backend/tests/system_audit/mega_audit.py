import httpx
import asyncio
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
COLL = "bits"
SLUG = "mega-audit-v2"

class MegaAudit:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.results = []

    async def run(self):
        print(f"--- MASTER AUDIT START: {datetime.now()} ---")
        
        # 1. System (1)
        await self.test("Vitals Check", "GET", f"{BASE_URL}/system/vitals")

        # 2. Projects Lifecycle (5)
        await self.test("List Projects", "GET", f"{BASE_URL}/projects/")
        await self.test("Create Project", "POST", f"{BASE_URL}/projects/", json={"name": "Mega Audit", "collection": COLL, "slug": SLUG})
        await self.test("Duplicate Project (400)", "POST", f"{BASE_URL}/projects/", json={"name": "X", "collection": COLL, "slug": SLUG}, expected=400)
        await self.test("Invalid Collection (400)", "POST", f"{BASE_URL}/projects/", json={"name": "X", "collection": "bad", "slug": "x"}, expected=400)
        await self.test("Create Manual Slug", "POST", f"{BASE_URL}/projects/", json={"name": "Manual", "collection": COLL, "slug": "manual-slug"})

        # 3. Content & Precedence (7)
        await self.test("Get Content", "GET", f"{BASE_URL}/{COLL}/{SLUG}/content")
        await self.test("Get Non-existent (404)", "GET", f"{BASE_URL}/{COLL}/ghost/content", expected=404)
        
        md_content = """---
title: Audit
description: x
draft: true
---
# El Desafío
x
# La Solución
x
# Proceso de Armado
x
# Retos y Aprendizajes
x
# Veredicto
x"""
        await self.test("Persist Valid MD", "POST", f"{BASE_URL}/{COLL}/{SLUG}/persist", json={"content": md_content})
        await self.test("Persist Invalid Frontmatter (400)", "POST", f"{BASE_URL}/{COLL}/{SLUG}/persist", json={"content": "bad"}, expected=400)
        await self.test("Revert (No Portfolio Base - 400/404)", "POST", f"{BASE_URL}/{COLL}/{SLUG}/revert", expected=[400, 404])
        await self.test("Promote Project", "POST", f"{BASE_URL}/{COLL}/{SLUG}/promote", expected=[200, 400])
        await self.test("Forget Project (Cleanup)", "POST", f"{BASE_URL}/{COLL}/{SLUG}/forget")

        # 4. Chat & IA (4)
        await self.client.post(f"{BASE_URL}/projects/", json={"name": "Chat Test", "collection": COLL, "slug": "chat-test"})
        await self.test("Chat Init", "POST", f"{BASE_URL}/{COLL}/chat-test/init")
        await self.test("Send Message", "POST", f"{BASE_URL}/{COLL}/chat-test/message", json={"content": "Hello"})
        await self.test("Generate Draft", "POST", f"{BASE_URL}/{COLL}/chat-test/draft")
        await self.test("Chat History", "GET", f"{BASE_URL}/{COLL}/chat-test/chat/history")

        # 5. Localization (3)
        await self.test("Get Translation", "GET", f"{BASE_URL}/{COLL}/chat-test/translate")
        await self.test("Translation Draft", "POST", f"{BASE_URL}/{COLL}/chat-test/translate/draft", json={"from_scratch": True})
        await self.test("Persist Translation", "POST", f"{BASE_URL}/{COLL}/chat-test/translate/persist", json={"content": md_content})

        # 6. Studio Management (5)
        await self.test("Suggest Shots", "POST", f"{BASE_URL}/{COLL}/chat-test/studio/suggest")
        await self.test("List Shots", "GET", f"{BASE_URL}/{COLL}/chat-test/studio/shots")
        await self.test("Create Manual Shot", "POST", f"{BASE_URL}/{COLL}/chat-test/studio/shots", json={"title": "Manual Shot", "description": "x", "focus": "x", "atmosphere": "rojo"})
        await self.test("Get Shot Detail", "GET", f"{BASE_URL}/{COLL}/chat-test/studio/shots/manual-shot")
        await self.test("Patch Shot", "PATCH", f"{BASE_URL}/{COLL}/chat-test/studio/shots/manual-shot", json={"focus": "updated"})

        # 7. Studio Assets & Pipeline (5)
        await self.test("Get Missing Image (404)", "GET", f"{BASE_URL}/{COLL}/chat-test/studio/shots/manual-shot/image/none", expected=404)
        await self.test("Status Polling", "GET", f"{BASE_URL}/{COLL}/chat-test/studio/shots/manual-shot/status")
        await self.test("Correct Missing Variant (400)", "POST", f"{BASE_URL}/{COLL}/chat-test/studio/shots/manual-shot/correct", json={"instruction": "x", "comfly_id": "none"}, expected=400)
        await self.test("Approve Missing Variant (400)", "POST", f"{BASE_URL}/{COLL}/chat-test/studio/shots/manual-shot/approve", json={"comfly_id": "none"}, expected=400)
        await self.test("Delete Variant (404)", "DELETE", f"{BASE_URL}/{COLL}/chat-test/studio/shots/manual-shot/image/none", expected=404)

        # Final Cleanups
        await self.client.post(f"{BASE_URL}/{COLL}/chat-test/forget")
        await self.client.post(f"{BASE_URL}/{COLL}/manual-slug/forget")

        print("\n--- AUDIT SUMMARY (30 POINTS) ---")
        for r in self.results:
            status = "✅ PASS" if r["success"] else "❌ FAIL"
            print(f"{status} {r['name']} ({r['code']})")
        
        await self.client.aclose()

    async def test(self, name, method, url, json=None, expected=None):
        try:
            if method == "GET": r = await self.client.get(url)
            elif method == "POST": r = await self.client.post(url, json=json)
            elif method == "PATCH": r = await self.client.patch(url, json=json)
            elif method == "DELETE": r = await self.client.delete(url)
            
            code = r.status_code
            success = code < 300 if expected is None else (code in expected if isinstance(expected, list) else code == expected)
            self.results.append({"name": name, "code": code, "success": success})
        except Exception as e:
            self.results.append({"name": name, "code": "ERR", "success": False, "err": str(e)})

if __name__ == "__main__":
    asyncio.run(MegaAudit().run())
