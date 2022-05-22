from asyncore import dispatcher
from contextlib import redirect_stderr
from rasa_sdk import Tracker, FormValidationAction, ValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from typing import Text, List, Any, Dict

info_db = {
    'Austria': 'If you have the Ukrainian nationality or if you were granted protection status in Ukraine, you and your family members are entitled to “temporary protection” under certain conditions. You will need to register with the police at specific police stations or special reception centers (“Erfassungsstellen”).',
    'Belgium':'Registration for temporary protection takes place at Brussels Expo, Palais (8) Heysel. The registration centre is open every weekday from 8.30 am to 5.30 pm and Saturday from 8.30 am to 13 pm. Closed on Sunday.',
    'Bulgaria':'You can enter using your personal car, with or without international insurance. You can enter with your pets. If they do not have the necessary documents, a simplified procedure is applicable.',
    'Cyprus':'If you were permanently residing in Ukraine, and you left the country to escape war from 24 February 2022 on, you may be entitled to temporary protection according to the Council Implementing Decision (EU) 2022/382 of 4 March 2022 establishing the existence of a mass influx of displaced persons from Ukraine within the meaning of Article 5 of Directive 2001/55/EC, and having the effect of introducing temporary protection.',
    'Czech Republic':'Call this number for help +420 974 801 802',
    'Denmark':'You can be granted a temporary residence permit under the law on temporary residence permits for displaced persons from Ukraine (the Special Act), if you are staying in Denmark, and you are either a Ukrainian citizen or recognized as a refugee in Ukraine.',
    'Estonia':'Once you have arrived in Estonia, move to your destination. When you are in transit, continue to the bus station, port, or airport. If you plan to stay in Estonia, please apply for temporary protection as soon as possible. You can do this at the Police and Border Guard Board.',
    'Finland':'Those who have fled Ukraine can apply for temporary protection in Finland. The process is faster than when applying for asylum. Those who apply for and are granted temporary protection have always the same right as asylum seekers to live in a reception centre.',
    'France':'Ukrainian citizens holding a biometric passport do not need a short-stay visa to travel to the Schengen area and thus to France.',
    'Germany':'The German Federal Office for Migration and Refugees recommends persons who dont have sufficient financial means or need shelter to contact the local police station or the local immigration office.',
    'Greece':'Upon entry to Greece in a private vehicle, the driver is required to present a valid driving license. Ukrainian private vehicles are exempted from paying highway tolls. If you enter with a private vehicle, you will need to declare your information at the citys customs office. For a 6-month period after your entry in the country, you may move freely with your vehicle. Proceed to the Customs office at the border crossing point to receive a paper slip marking the date of the car’s entry in Greece. You should contact the Customs office at your place of residence for further information.',
    'Hungary':'If you are just arriving from Ukraine, there are some organisations that may be able to help you at the border and across Hungary with legal counselling, finding transportation, accommodation, relief items, among others. The support can change depending on where you are. Members of the Charity Council are providing support at “Help Points” close to the border crossings. You can ask for directions to your closest one when crossing the border, or if you arrive on foot, you will be taken there by bus. You can also get in touch with organisations directly. You can find their contact details and other information by clicking on the name of each organisation below.',
    'Ireland':'You should go to a reception hub in the airport or port when you arrive. Otherwise, you can get help at a Ukraine Support Centre. These centres are currently in Dublin, Limerick and Cork. They can help you to get somewhere to stay and help you to apply for social welfare (financial help).',
    'Italy':'Anyone who arrives in Italy must present him or herself to the national authorities to be identified. Do not be afraid of the police, as they can help and protect you.  ',
    'Latvia':'A hotline for services and support available for Ukraine residents in Riga: +371 27 380 380 (available 24/7)',
    'Lithuania':'You can reach us at +370 526 40 200, we work Monday-Friday 8:00-18:00  (Vilnius/Kyiv time GMT+2). If you can’t get through – please try again later, we will do our best to constantly increase our ability to take more calls.',
    'Luxembourg':'This emergency reception centre, open 24/7, is located at the SHUK (Structure d’hébergement d’urgence au Kirchberg), 11, rue Carlo Hemmer in Luxembourg-City. This centre offers shelter for the first few days, meals and basic necessities to people wishing to apply for temporary protection in Luxembourg, but also for those wishing to move to another European country. After the first few days, you will be directed to other governmental structures.',
    'Malta':'',
    'Netherlands':'You do not need to report to the IND when you arrive in the Netherlands. Do you not yet have a place to stay? Special emergency reception centres are being opened by some Dutch local councils. You can ask for assistance at all local councils.  At Utrecht Central station and Amsterdam Central Station are support centres for the initial reception. The Red Cross is also helping people who need a place to stay. Ask them a question in Ukrainian, Russian or English via Whatsapp: +31 6 48 15 80 53.',
    'Poland':'Any person hoping to enter Poland from Ukraine will be allowed to enter.',
    'Portugal':'The Government has streamlined the requirements for displaced Ukrainians, who have fled the country due to the war, to obtain temporary one-year protection, which can be extended by two six-month periods. It is no longer necessary for the person to prove he or she is in danger and the proof of identity can be done in any way.',
    'Romania':'Depending on where you are located, different forms of asylum procedures may apply. You may ask for asylum at the Border Police, the Police, or the General Inspectorate for Immigration.  ',
    'Slovakia':'',
    'Slovenia':'Do not worry if you do not have a place to stay. Inform the border authorities that you need help with accommodation. They will arrange for you to stay at one of the locations they have prepared for you.',
    'Spain':'',
    'Sweden':''
}

info2_db = {
    'Austria': 'Please call the following number, they speak Ukrainian and will be able to help you: +43 1 2676 870 9460',
    'Belgium':'Please call this number 1813. You will talk to a human. Take a deep breath. I will be waiting here.',
    'Bulgaria':'Telephone number for more information: 0800 11 466 (every day from 8:00 to 18:00)',
    'Cyprus':'Call this number please: 80007773. You will talk with a human. Be brave and explain your situation. You can do this!',
    'Czech Republic':'Contact: Kovářská 4, 190 00 Praha 9, phone: +420 730 158 779',
    'Denmark':'Call this number 70 201 201. Everything will be ok.',
    'Estonia':'You are doing great! Do one last thing for me, call this number 678 7422. A human will pick up.',
    'Finland':'Call this number on your phone (09)41350501.',
    'France':'You are doing great! I just want you to do one last thing. Call this number 0033 1 40 44 46 45.',
    'Germany':'Call this number on your phone 114.',
    'Greece':'Call this number on your phone 114.',
    'Hungary':'Please, call this number on your phone 116 11.',
    'Ireland':'You are doing great! Please call this number 116 123.',
    'Italy':'Call this number now 199 284 284.',
    'Latvia':'You are doing great! I need one last thing from you. I want you to speak with a human friend of mine. Call this number 6 7222 922. She is very friendly!',
    'Lithuania':'Call this number 116 111.',
    'Luxembourg':'Call this number 454545.',
    'Malta':'Hang on tight! Help is on the way! ',
    'Netherlands':'Call this number 113.',
    'Poland':'You are doing great, however I think you might need to get in touch with someone. I want to introduce you to a human friend of mine. Please contact +488919288.',
    'Portugal':'You seem very stressed. Do me a favour, get in touch with this number +351800916800. I think you should hear what they have to say.',
    'Romania':'Call 0800 801 200',
    'Slovakia':'Call 02 5443 0395',
    'Slovenia':'Call +386 1 4750 685',
    'Spain':'Call 902 500 002',
    'Sweden':'Call 1177'
}

def clean_name(name):
    return "".join([c for c in name if c.isalpha()])

class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"first_name": None}
        return {"first_name": name}


class ActionInfoCountry(Action):

    def name(self) -> Text:
        return "action_info_country"

    def run(self,
        dispacher: CollectingDispatcher,
        tracker: Tracker, domain: Dict[Text,Any]) -> List[Dict[Text,Any]]:
    
        country = tracker.get_slot('pais')

        tz_string = info_db.get(country,None)
        if not tz_string:
            msg=f"I didn't recognize {country}, is it spelled correctly?"
            dispacher.utter_message(text=msg)
            return []

        msg = f"Info: {(info_db[country])}"
        dispacher.utter_message(text=msg)

        return []

class ActionGetScore (Action):

    def name(self) -> Text:
        return "action_get_score"
    
    def run(self,
        dispacher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text,Any]) -> List[Dict[Text,Any]]:



        num = int(tracker.get_slot("number"))
        num1 = int(tracker.get_slot("number_1"))
        num2 = int(tracker.get_slot("number_2"))
        num3 = int(tracker.get_slot("number_3"))
        num4 = int(tracker.get_slot("number_4"))
        num5 = int(tracker.get_slot("number_5"))
        num6 = int(tracker.get_slot("number_6"))
        num7 = int(tracker.get_slot("number_7"))
        num8 = int(tracker.get_slot("number_8"))
        num9 = int(tracker.get_slot("number_9"))
        num10 = int(tracker.get_slot("number_10"))
        num11 = int(tracker.get_slot("number_11"))
        num12 = int(tracker.get_slot("number_12"))
        num13 = int(tracker.get_slot("number_13"))
        num14 = int(tracker.get_slot("number_14"))
        num15 = int(tracker.get_slot("number_15"))
        num16 = int(tracker.get_slot("number_16"))
        num17 = int(tracker.get_slot("number_17"))
        num18 = int(tracker.get_slot("number_18"))
        num19 = int(tracker.get_slot("number_19"))

        total = num + num1 + num2 + num3 + num4 + num5 + num6 + num7 + num8 + num9 + num10 + num11 + num12 + num13 + num14 + num15 + num16 + num17 + num18 + num19

        msg = f"Score:{total}"
        dispacher.utter_message(text=msg)

        if total > 44:
            country = tracker.get_slot('pais')
            msg = f"{(info2_db[country])}" 
            dispacher.utter_message(text=msg)

        else:
            msg = "Let's do an exercise. Hold your breath for 4 seconds. Slowly exhale through your mouth for 4 seconds. Repeat this until you feel more relaxed. Talk to me again if you still feel bad."
            dispacher.utter_message(text=msg)

            

        return []