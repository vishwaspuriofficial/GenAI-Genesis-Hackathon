import time
from datetime import datetime
import asyncio
from meeting import run_meeting
import aiohttp

async def scheduler_service():
    """Infinitely running scheduler service."""
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")  # Current time in yyyy-mm-dd hh:mm format
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/meeting/earliest") as response:
                if response.status == 200:
                    response_data = await response.json()
                    earliest_meeting = response_data['appointment']
                else:
                    earliest_meeting = None
        if earliest_meeting is None:
            print("No meetings scheduled. Waiting...")
            await asyncio.sleep(60)  # Wait for 1 minute before checking again
            continue
            
        meeting_time, meeting_id = earliest_meeting['datetime'], earliest_meeting['appointment_id']  
        if current_time == meeting_time:
            print(f"Starting meeting: {meeting_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:8000/api/meeting-short-info/{meeting_id}") as response:
                    if response.status == 200:
                        response_data = await response.json()
                        meeting_info = response_data
                    else:
                        meeting = None
            await run_meeting(meeting_info) 
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:8000/api/meetings/cleanup") as response:
                    if response.status == 200:
                        print("Cleanup request successful.")
                    else:
                        print(f"Cleanup request failed with status code: {response.status}")
        else:
            print(f"Waiting for the next meeting at {meeting_time}...")

        
        await asyncio.sleep(30)

if __name__ == "__main__":
    print("Scheduler service started.")
    asyncio.run(scheduler_service())