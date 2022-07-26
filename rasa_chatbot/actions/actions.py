# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import math
from random import randint
import datetime as dt
import os.path
import csv
import pandas as pd

reservations_filename = f'./files/reservations.csv'
clean_filename = f'./files/cleaning.csv'

def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


##########################################################################
############################### RESERVATION ##############################
##########################################################################


#action per prenotare una stanza
class ActionBookRoom(Action):
    
    def name(self) -> Text:
        return "action_booking_room"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        number = tracker.get_slot("number")
        room_type = tracker.get_slot("room_type")
        days = tracker.get_slot("days")

        dispatcher.utter_message(text=f'You have chosen to book {number} {room_type} rooms for {days} days. Do you want to confirm your reservation?')
       
        return []
    

#action per salvare una prenotazione       
class ActionSaveReservation(Action): 
    
    def name(self) -> Text:
        return "action_save_reservation"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        number =str(tracker.get_slot("number"))
        room_type = str(tracker.get_slot("room_type"))
        days = str(tracker.get_slot("days"))
        
        #create a random order ID
        reservation_id = f'AA{random_with_N_digits(5)}'

        #check if reservation file exists
        if os.path.exists(reservations_filename):
            # append if already exists
            file = open(reservations_filename, 'a', newline='')
        else:
            # make a new file if not
            file = open(reservations_filename, 'w', newline='')
            writer = csv.writer(file)
            writer.writerow(['Reservation ID', 'Room Type', 'Number of rooms', 'Days'])

        writer = csv.writer(file)
        writer.writerow([reservation_id, room_type, number, days])
        file.close()
        dispatcher.utter_message(text=f'Your reservation has been confirmed! The reservation ID is {reservation_id}.')
        # ripulire slot finita una storia
                
        return [SlotSet("reservation_id",reservation_id), SlotSet("number"), SlotSet("room_type"), SlotSet("days")]
    
    
# action per visualizzate una prenotazione    
class ActionSeeReservation(Action):
    
    def name(self) -> Text:
        return "action_see_reservation"
    
    def run(self, dispatcher : CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        reservation_id = str(tracker.get_slot('reservation_id'))
        
        df = pd.read_csv(reservations_filename)

        # get index of the row with specified order ID
        index = df.index
        condition = df['Reservation ID'] == reservation_id
        reservation_index = index[condition]
        if len(reservation_index) == 0:
            # reservation not found
            # send message to the user
            dispatcher.utter_message(response='utter_no_reservations')
        else:
            # get details
            number = df.loc[reservation_index[0], 'Number of rooms']
            room_type = df.loc[reservation_index[0], 'Room Type']
            days = df.loc[reservation_index[0], 'Days']

            dispatcher.utter_message(text=f'The reservation {reservation_id} have booked {number} {room_type} rooms for {days} days.') 

        return [SlotSet('reservation_id', None)]  # per ripulire lo slot finita una storia

        
# action per modificare una prenotazione
class ActionEditReservation(Action):

    def name(self) -> Text:
        return 'action_edit_reservation'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        reservation_id = str(tracker.get_slot('reservation_id'))
        number = tracker.get_slot("number")
        room_type = tracker.get_slot("room_type")
        days = tracker.get_slot("days")

        df = pd.read_csv(reservations_filename)

        # get index of the row with specified order ID
        index = df.index
        condition = df['Reservation ID'] == reservation_id
        reservation_index = index[condition]
        if len(reservation_index) == 0:
            # reservation not found
            # send message to the user
            dispatcher.utter_message(response='utter_no_reservations')
        else:
            df.loc[reservation_index[0], 'Number of rooms'] = number
            df.loc[reservation_index[0], 'Room Type'] = room_type
            df.loc[reservation_index[0], 'Days'] = days
            # save the file
            df.to_csv(reservations_filename, index=False)
            dispatcher.utter_message(text=f'The reservation with the ID {reservation_id} has been updated with success!')
              
        
        return [SlotSet("reservation_id"), SlotSet("number"), SlotSet("room_type"), SlotSet("days")]

# action per modificare una prenotazione
class ActionDeleteReservation(Action):

    def name(self) -> Text:
        return 'action_delete_reservation'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        reservation_id = str(tracker.get_slot('reservation_id'))

        df = pd.read_csv(reservations_filename)

        # get index of the row with specified order ID
        index = df.index
        condition = df['Reservation ID'] == reservation_id
        reservation_index = index[condition]

        if len(reservation_index) == 0:
            # reservation not found
            # send message to the user
            dispatcher.utter_message(response='utter_no_reservations')
        else:
            df = df.drop(reservation_index[0])

            # save the file
            df.to_csv(reservations_filename, index=False)
            dispatcher.utter_message(text=f'The reservation with the ID {reservation_id} has been deleted with success!')
              
        return []
        #return [SlotSet("reservation_id")]


##########################################################################
################################ CLEANING ################################
##########################################################################


    
# action per prenotare la pulizia della camera    
class ActionScheduleCleaning(Action):
    
    def name(self) -> Text:
        return "action_schedule_cleaning"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        duration = tracker.get_slot("duration")
        unit = tracker.get_slot("time_unit")
        
        if duration is None:
            dispatcher.utter_message(text='Sure, i will send someone to your room right away.')
            return [SlotSet("time_unit"), SlotSet("hour"), SlotSet("minute"), SlotSet("suff")]

        if unit is None:
            dispatcher.utter_message(text='Sure, sending a cleaner to your room.')
            return [SlotSet("duration"), SlotSet("hour"), SlotSet("minute"), SlotSet("suff")]

        time_tuple = dt.datetime.now().timetuple()
        h = time_tuple[3]
        m = time_tuple[4]

        if unit == "min":
            m += int(duration)
            if m > 60:
                h += int(m/60)
                m = m % 60

        elif unit == "hour":
            h += int(duration)

        h = h % 24
        if h > 12:
            h = h - 12
            suff = 'PM'
        else:
            suff = 'AM'
        m = "%02d" % m
        dispatcher.utter_message(text=f'Sure, i have scheduled a cleaning for {h}:{m} {suff}.') 

        return [SlotSet("duration"), SlotSet("time_unit"), SlotSet("hour", h), SlotSet("minute", m), SlotSet("suff", suff)]
  



# action per visulizzare la prenotazione della pulizia della stanza    
class ActionSeeCleaningSchedule(Action):
    
    def name(self) -> Text:
        return "action_see_cleaning_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        h = tracker.get_slot("hour")
        m = tracker.get_slot("minute")
        suff = tracker.get_slot("suff")

        if ((h is None) or (m is None) or (suff is None)):
            dispatcher.utter_message(response='utter_no_cleaning_scheduled')
        else:
            dispatcher.utter_message(text=f'We have scheduled a cleaning for {h}:{m} {suff}.') 

        return []
