#!/usr/bin/env python
"""
Appointment Management Utility

This script provides direct access to view, add, and delete appointments
in the appointments.json file.
"""

import argparse
import json
import sys
import os
from datetime import datetime
from collections import OrderedDict

# Path to the appointments JSON file
APPOINTMENTS_FILE = "appointments.json"

def load_appointments():
    """Load appointments from the JSON file"""
    if not os.path.exists(APPOINTMENTS_FILE):
        print(f"Appointments file not found: {APPOINTMENTS_FILE}")
        return OrderedDict()
        
    try:
        with open(APPOINTMENTS_FILE, 'r') as f:
            data = json.load(f)
            # Convert to OrderedDict and sort
            appointments = OrderedDict(sorted(data.items()))
            return appointments
    except Exception as e:
        print(f"Error loading appointments: {str(e)}")
        return OrderedDict()

def save_appointments(appointments):
    """Save appointments to the JSON file"""
    try:
        with open(APPOINTMENTS_FILE, 'w') as f:
            json.dump(dict(appointments), f, indent=4)
        print(f"Successfully saved {len(appointments)} appointments to {APPOINTMENTS_FILE}")
    except Exception as e:
        print(f"Error saving appointments: {str(e)}")

def display_appointments(appointments):
    """Display all appointments in a readable format"""
    if not appointments:
        print("No appointments found.")
        return
        
    print(f"\nFound {len(appointments)} appointments:")
    print("-" * 50)
    print(f"{'DATETIME':<20} | {'APPOINTMENT ID'}")
    print("-" * 50)
    
    for date_time, appointment_id in appointments.items():
        print(f"{date_time:<20} | {appointment_id}")
    
    print("-" * 50)

def add_appointment(appointments, date, time, appointment_id):
    """Add a new appointment"""
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        return False
        
    # Validate time format
    try:
        datetime.strptime(time, "%H:%M")
    except ValueError:
        print("Error: Time must be in HH:MM format")
        return False
    
    # Create key
    key = f"{date} {time}"
    
    # Add to dictionary
    appointments[key] = appointment_id
    
    # Sort
    sorted_appointments = OrderedDict(sorted(appointments.items()))
    
    # Save
    save_appointments(sorted_appointments)
    print(f"Added appointment {appointment_id} at {key}")
    return True

def delete_appointment(appointments, date_time=None, appointment_id=None):
    """Delete an appointment by datetime or ID"""
    if not appointments:
        print("No appointments to delete.")
        return False
        
    if date_time and date_time in appointments:
        removed_id = appointments.pop(date_time)
        save_appointments(appointments)
        print(f"Deleted appointment at {date_time} with ID {removed_id}")
        return True
        
    if appointment_id:
        for dt, aid in list(appointments.items()):
            if aid == appointment_id:
                del appointments[dt]
                save_appointments(appointments)
                print(f"Deleted appointment with ID {appointment_id} at {dt}")
                return True
    
    print("Appointment not found.")
    return False

def cleanup_past(appointments):
    """Remove all past appointments"""
    now = datetime.now()
    current_date_time = now.strftime("%Y-%m-%d %H:%M")
    
    # Find keys to remove
    to_remove = []
    for date_time in appointments:
        try:
            dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            if dt < now:
                to_remove.append(date_time)
        except ValueError:
            # Invalid format, should be removed
            to_remove.append(date_time)
    
    # Remove the keys
    for key in to_remove:
        del appointments[key]
    
    if to_remove:
        save_appointments(appointments)
        print(f"Removed {len(to_remove)} past appointments")
    else:
        print("No past appointments to remove")
    
    return len(to_remove)

def get_earliest_meeting():
    """
    Get the earliest upcoming meeting
    
    Returns:
        dict: Dictionary with datetime and appointment_id, or None if no appointments
    """
    # Load appointments and clean up past ones
    appointments = load_appointments()
    cleanup_past(appointments)
    
    # If no appointments, return None
    if not appointments:
        return None
        
    # Get the first item (earliest by date since it's sorted)
    earliest_datetime, appointment_id = next(iter(appointments.items()))
    
    return {
        'datetime': earliest_datetime,
        'appointment_id': appointment_id
    }

def main():
    parser = argparse.ArgumentParser(description='Manage appointments')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all appointments')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new appointment')
    add_parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    add_parser.add_argument('--time', required=True, help='Time in HH:MM format')
    add_parser.add_argument('--id', required=True, help='Appointment ID')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an appointment')
    delete_parser.add_argument('--datetime', help='Datetime in "YYYY-MM-DD HH:MM" format')
    delete_parser.add_argument('--id', help='Appointment ID')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove past appointments')
    
    args = parser.parse_args()
    
    # Load appointments
    appointments = load_appointments()
    
    if args.command == 'list' or args.command is None:
        display_appointments(appointments)
    
    elif args.command == 'add':
        add_appointment(appointments, args.date, args.time, args.id)

    elif args.command == 'earliest':
        earliest_meeting = get_earliest_meeting()
        print(earliest_meeting)
    
    elif args.command == 'delete':
        if not args.datetime and not args.id:
            print("Error: You must specify either --datetime or --id")
            return
        delete_appointment(appointments, args.datetime, args.id)
    
    elif args.command == 'cleanup':
        cleanup_past(appointments)

if __name__ == "__main__":
    main() 