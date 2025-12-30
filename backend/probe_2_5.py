import httpx
import asyncio

GEMINI_API_KEY = "AIzaSyCikLiet8ZiU0i0klew5qQ6xQSKqdQCP2M"

async def check_model(name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{name}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": "Ping"}]}]}
    
    print(f"Probing {name}...", end=" ")
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            print("FOUND (200 OK)")
            return True
        else:
            print(f"MISSING ({resp.status_code})")
            return False

async def main():
    # User requests "2.5 flash"
    await check_model("gemini-2.5-flash")
    await check_model("models/gemini-2.5-flash")
    
    # Alternatives just in case
    await check_model("gemini-2.0-flash") # Stable?
    await check_model("gemini-2.0-pro")
    await check_model("gemini-exp-1206") # Dec 6 snapshot?

if __name__ == "__main__":
    asyncio.run(main())
