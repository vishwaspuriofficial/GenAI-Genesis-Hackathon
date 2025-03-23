import time
from datetime import datetime
from test import meetings, getMeetingDetails
import asyncio
from agent import run_meeting

def get_earliest_meeting():
    """Fetch the earliest meeting info from the meetings dictionary."""
    if not meetings:
        return None, None
    sorted_meetings = sorted(meetings.items(), key=lambda x: x[0])  # Sort by time
    return sorted_meetings[0]  # Return the earliest meeting (time, info)

async def scheduler_service():
    """Infinitely running scheduler service."""
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")  # Current time in yyyy-mm-dd hh:mm format
        meeting_time, meeting_id = get_earliest_meeting()

        if meeting_time is None:
            print("No meetings scheduled. Waiting...")
            await asyncio.sleep(60)  # Wait for 1 minute before checking again
            continue

        if current_time == meeting_time:
            print(f"Starting meeting: {meeting_id}")
            meeting_link, team_name = getMeetingDetails(meeting_id)
            meeting_info = {"meetingLink": meeting_link, "teamName": team_name}
            await run_meeting(meeting_info)  # Call the run_meeting function asynchronously
            del meetings[meeting_time]  # Remove the meeting after it's triggered
        else:
            print(f"Waiting for the next meeting at {meeting_time}...")

        await asyncio.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    print("Scheduler service started.")
    asyncio.run(scheduler_service())