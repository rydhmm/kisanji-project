"""Test Mandi API"""
import httpx
import asyncio
import json

async def test_mandi():
    async with httpx.AsyncClient() as client:
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        
        # Test without state filter first
        params = {
            "api-key": "579b464db66ec23bdd0000012bc7e5f654d243de5d2f826a8f6bd9a3",
            "format": "json",
            "limit": 10
        }
        
        try:
            response = await client.get(url, params=params, timeout=15.0)
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Total records available: {data.get('total', 0)}")
            print(f"Records in this query: {data.get('count', 0)}")
            records = data.get("records", [])
            if records:
                print(f"\nSample records:")
                for i, rec in enumerate(records[:3]):
                    print(f"\n{i+1}. {rec.get('commodity')} in {rec.get('market')}, {rec.get('state')}")
                    print(f"   Price: ₹{rec.get('modal_price')}/quintal")
                    print(f"   Date: {rec.get('arrival_date')}")
            
            # Get unique states
            states = set(rec.get('state') for rec in records)
            print(f"\nStates in data: {states}")
            
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_mandi())
