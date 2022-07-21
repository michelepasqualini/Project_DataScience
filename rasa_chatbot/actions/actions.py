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
import datetime as dt

'''
class ActionFindInfo(Action):

    def name(self) -> Text:
        return "action_find_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name=str(tracker.get_slot('country'))
        r=requests.get(url='https://restcountries.com/v3.1/name/{}'.format(name.lower()))

        if r.status_code==200:
            data=r.json()
            flag=list(data[0]['flags'].values())[0]
            capital=list(data[0]['capital'][0])
            moneta=list(data[0]['currencies'][0].values())[0]['name']
            subregion=data[0]['subregion']
            area=data[0]['area']
            output='{} is a state located in {}, the area is {}, the capital is{}, the currencies is {} and you can see the flag at this link {}'
        else:
            output='something went wrong'
        
        dispatcher.utter_message(text=output)

        return []
'''
    
class ActionBookRoom(Action):
    
    def name(self) -> Text:
        return "action_booking_room"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        number = tracker.get_slot("number")
        room_type = tracker.get_slot("room_type")

        dispatcher.utter_message(text=f'You have chosen to book {number} {room_type} rooms.')

        return [SlotSet("number"), SlotSet("room_type")]
    
    
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

    
