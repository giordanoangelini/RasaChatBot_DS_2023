# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted
from rasa_sdk.executor import CollectingDispatcher
import requests
from dotenv import load_dotenv
import os

load_dotenv()
KEY = os.getenv('SPOONACULAR_KEY')

RECIPE_LIST = []

def recipe_details(id, dispatcher):
    url_query = f'https://api.spoonacular.com/recipes/{id}/information?apiKey={KEY}'
    r = requests.get(url=url_query)
    
    if r.status_code == 200:
        data = r.json()
        title = data['title']
        price = data['pricePerServing']
        time = data['readyInMinutes']
        try: 
            url = data['spoonacularSourceUrl']
        except: 
            url = data['sourceUrl']
        dispatcher.utter_message(
            text=f"{title}\n 🕐: {time} m - 💰: {round(float(price/100),2)}$ per serving\n{url}"
        )

    else:
        output = "I do not know anything about, what a mistery!? Are you sure it is correctly spelled?"
        dispatcher.utter_message(text=output)

class SearchByIngredient(Action):

    def name(self) -> Text:
        return "action_search_by_ingredient"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        list_ingredients = tracker.get_slot('ingredient')
        if type(list_ingredients) != list: 
             output = "I haven't found any recipe with the ingredients listed"
             dispatcher.utter_message(text=output)
             return []
        query = ','.join(list_ingredients)
        url_query = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={query}&apiKey={KEY}'
        r = requests.get(url=url_query)
        if r.status_code == 200:
            data = r.json()
            
            if len(data) == 0:
                output = "I haven't found any recipe with the ingredients listed"
                dispatcher.utter_message(text=output)
            else:
                data.sort(key = lambda x: x["likes"], reverse = True)
                recipe=data[0]
                title = recipe["title"]
                image = recipe["image"]
                id = recipe["id"]
                likes = recipe["likes"]
                dispatcher.utter_message(
                    text=f"{title} ({likes} 👍)\nYou can find the image here:\n{image}",
                    buttons = [
                        {"payload": f'/show_recipe_details{{"id":{id}}}', "title": "Let's cook this"},
                        {"payload": "/show_more", "title": "Show more recipes!!"}
                    ]
                )
                
                global RECIPE_LIST
                RECIPE_LIST = data[1:]
        else:
            output = "I do not know anything about, what a mistery!? Are you sure it is correctly spelled?"
            dispatcher.utter_message(text=output)
            return []

class MyFallback(Action):
    
    def name(self) -> Text:
        return "action_random_recipe"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        url_query = f'https://api.spoonacular.com/recipes/random?apiKey={KEY}'
        r = requests.get(url=url_query)
        
        if r.status_code == 200:
            data = r.json()

            id = data['recipes'][0]['id']
            title = data['recipes'][0]['title']
            image = data['recipes'][0]['image']
            dispatcher.utter_message(
                text=f"{title}\nYou can find the image here:\n{image}",
                buttons = [{"payload": f'/show_recipe_details{{"id":{id}}}', "title": "Let's cook this"}]
            )

        else:
            output = "I do not know anything about, what a mistery!? Are you sure it is correctly spelled?"
            dispatcher.utter_message(text=output)
        
        return []
    
class ShowMore(Action):
    
    def name(self) -> Text:
        return "action_show_more"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global RECIPE_LIST
        data = RECIPE_LIST
       
        number = 3
        
        if len(data) == 0:
                output = "I haven't found more recipes"
                dispatcher.utter_message(text=output)

        else:
            recipe = data[0]
            title = recipe["title"]
            image = recipe["image"]
            id = recipe["id"]
            try: 
                likes = f'({recipe["likes"]} 👍)'  
            except: 
                likes = ''
            dispatcher.utter_message(
                text=f"{title} {likes}\nYou can find the image here:\n{image}",
                buttons = [
                    {"payload": f'/show_recipe_details{{"id":{id}}}', "title": "Let's cook this"},
                    {"payload": "/show_more", "title": "Show more recipes!!"}
                ]
            )
            RECIPE_LIST = data[1:]
        return []

class SearchRecipe(Action):
    
    def name(self) -> Text:
        return "action_search_recipe"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        recipe = tracker.get_slot('recipe')
        r = requests.get(url=f'https://api.spoonacular.com/recipes/autocomplete?query={recipe}&apiKey={KEY}')
        if r.status_code == 200:
            data = r.json()
            
            if len(data) == 0:
                output = "I haven't found requested recipe"
                dispatcher.utter_message(text=output)
            else:
                recipe=data[0]
                id = recipe["id"]           
                recipe_details(id,dispatcher)
        else:
            output = "I do not know anything about, what a mistery!? Are you sure it is correctly spelled?"
            dispatcher.utter_message(text=output)

        return []

class ShowRecipeDetails(Action):
    
    def name(self) -> Text:
        return "action_show_recipe_details"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        id = tracker.get_slot('id')
        recipe_details(id,dispatcher)
        return []

class SearchCuisine(Action):
    
    def name(self) -> Text:
        return "action_search_cuisine"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        cuisine = tracker.get_slot('cuisine')
        
        url_query = f'https://api.spoonacular.com/recipes/complexSearch?cuisine={cuisine}&apiKey={KEY}'
        r = requests.get(url=url_query)
        if r.status_code == 200:
            data = r.json()['results']
            
            if len(data) == 0:
                output = f"I haven't found any recipe"
                dispatcher.utter_message(text=output)
            else:
                recipe=data[0]
                title = recipe["title"]
                image = recipe["image"]
                id = recipe["id"]
                dispatcher.utter_message(
                    text=f"{title}\nYou can find the image here:\n{image}",
                    buttons = [
                        {"payload": f'/show_recipe_details{{"id":{id}}}', "title": "Let's cook this"},
                        {"payload": "/show_more", "title": "Show more recipes!!"}
                    ]
                )
                
                global RECIPE_LIST
                RECIPE_LIST = data[1:]
        else:
            output = "I do not know anything about, what a mistery!? Are you sure it is correctly spelled?"
            dispatcher.utter_message(text=output)
            return []

class SearchMealType(Action):
    
    def name(self) -> Text:
        return "action_search_meal_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        meal_type = tracker.get_slot('meal_type')
        
        url_query = f'https://api.spoonacular.com/recipes/complexSearch?type={meal_type}&apiKey={KEY}'
        r = requests.get(url=url_query)
        if r.status_code == 200:
            data = r.json()['results']
            
            if len(data) == 0:
                output = f"I haven't found any {meal_type}"
                dispatcher.utter_message(text=output)
            else:
                recipe=data[0]
                title = recipe["title"]
                image = recipe["image"]
                id = recipe["id"]
                dispatcher.utter_message(
                    text=f"{title}\nYou can find the image here:\n{image}",
                    buttons = [
                        {"payload": f'/show_recipe_details{{"id":{id}}}', "title": "Let's cook this"},
                        {"payload": "/show_more", "title": "Show more recipes!!"}
                    ]
                )
                
                global RECIPE_LIST
                RECIPE_LIST = data[1:]
        else:
            output = "I do not know anything about, what a mistery!? Are you sure it is correctly spelled?"
            dispatcher.utter_message(text=output)
            return []
        


        