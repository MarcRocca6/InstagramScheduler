# /usr/bin/env python

import datetime
import pandas as pd
from pydrive.auth import GoogleAuth
from gcsa.attachment import Attachment
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA
from .global_path import *

def add_calendar(df):

    image = df['Image']
    start_time = df['Time']
    start_date = df['Date']
    if isinstance(start_time, str): # if 'start_time' a string, convert to datetime
        start_time = datetime.datetime.strptime(start_time, '%I:%M:%S %p').time()
    if isinstance(start_date, str): # if 'start_date' a string, convert to datetime
        start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y')

    start = datetime.datetime.combine(start_date, start_time) 
    end = start + datetime.timedelta(minutes=30)
    calendar = GoogleCalendar(calendar='*************@group.calendar.google.com',
    						credentials_path= resource_path('Creds\\Calendar\\client_secrets_calendar.json'))
    descriptor = df['Caption'] + '\t\t' + df['Image']
    print(descriptor, start, end)
    event = Event(
        'Instagram Post',
        start = start,
        end = end,
        description = descriptor,
        colors = 7,
        minutes_before_popup_reminder  = 5
    )

    calendar.add_event(event)
    print('Added to Calendar')    
