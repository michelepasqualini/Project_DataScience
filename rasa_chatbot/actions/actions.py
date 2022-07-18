# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import json

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
    
class BookRoomInfo(Action):
    def name(self) -> Text:
        return "form_book_room"
    
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["number", "room_type"]
    
    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        
        dispatcher.utter_message(template="utter_submit", number=tracker.get_slot('number'),
                                 room_type=tracker.get_slot('room_type'))
        return []
    
    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        
        return{"number": self.from_entity(entity="number", intent='num_rooms'),
            "room_type": self.from_entity(entity="room_type", intent="type_rooms")
        }
    
