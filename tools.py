from langchain_community.tools import tool,DuckDuckGoSearchResults
from dotenv import load_dotenv
import os,requests
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

load_dotenv()

#create web search tool
search=DuckDuckGoSearchResults(
    max_results=5,
    output_format='list'
)

@tool
def web_search_tool(query:str)->str:
    "search the provided query and give the reliable answer"
    results=search.invoke(query)
    output=[]
    for i,result in enumerate(results,1):
        output.append(
            f'''
            
            Report {i+1}
            Title: {result['title']}
            Content: {result['snippet']}
            Link: {result['link']}
            '''  
        )
    return "\n".join(output)

#create weather tool
@tool
def search_weather(city:str)->str:
    """Get the current weather for any named location, place, town, city,
    region, district, tourist destination, or geographical area.

    Use this tool whenever the user asks about current weather,
    temperature, rain, humidity, wind, or weather conditions.
    """
    api_key=os.getenv('OPENWEATHER_API_KEY')
   
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    
    try:
        response=requests.get(url,params=params)
        data=response.json()
        if response.status_code!=200:
            return f"Unable to fetch the weather of {city}"
        description=data['weather'][0]['description']
        temparature=data['main']['temp']
    
        return f'''
      City : {city}
      Description: {description}
      temparature: {temparature} °C
'''            
    except Exception as e:
        return f"Error {e}"
    

#find current date
@tool
def find_current_date(query:str)->str:
    "find the current date"
    current_date=datetime.now().strftime('%A,%d %B %Y')
    return current_date

#youtube search

youtube_search_engine=DuckDuckGoSearchResults(
    max_results=3,
    output_format='list'
    
)
@tool
def youtube_search(query:str)->str:
    "find the youtube videoes based on the user query"
    try:
        videoes=youtube_search_engine.invoke(
            f"site:youtube.com/watch {query}"
        )
        if not videoes:
            return "no Video found"
        output=[]
        for i,video in enumerate(videoes,1):
            output.append(
                f'''
-------------------------------------
Video {i}
-------------------------------------
Title:{video['title']}
Description:{video['snippet']}
URL:{video['link']}
                '''
            )
        return "\n".join(output)
    except Exception as e:
        return f'Youtube Video search Error: {e}'
    

#create tool that Calculate Distance
@tool
def cal_distance(loc1:str,loc2:str)->str:
    '''
    Calculate the distance and time duration  between {loc1} to {loc2}
    '''
    geolocater=Nominatim(user_agent='multiagent_travel_app')
    
    #find Co-ordinates
    location1=geolocater.geocode(loc1)
    location2=geolocater.geocode(loc2)
    
    if not location1:
        return f'could not find the Location {loc1}'
    if not location2:
            return f'could not find the Location {loc2}'
    
    #find latitude and longitude
    lon1=location1.longitude
    lat1=location1.latitude
    
    lon2=location2.longitude
    lat2=location2.latitude
    #calculate Distance
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}"
    )
    parame={'overview':'false'}
    try:
        response=requests.get(
            url,
            params=parame,
            timeout=10
        )
        if response.status_code !=200:
            return f"could not reach the location"
        data=response.json()
        
        if data.get('code')!='Ok':
            return 'Unable to reach the Location'
        route=data['routes'][0]
        
        distance_km=route['distance']/1000
        
        duration_hr=route['duration']/3600
        hour=int(duration_hr)
        minutes=int((duration_hr-hour)*60)
        
        return f'''
    Distance between {loc1} to {loc2} is {distance_km:.2f}\n
    and Time duration {hour} hr {minutes} min
    '''
    
        
    except Exception as e:
        return f'Error: {e}'
    

#create tool for publish facebook post
@tool
def publish_facebook_post(message:str)->str:
    'publish an approved text on a specified facebook page'
    
    page_id=os.getenv('FACEBOOK_PAGE_ID')
    page_access_token=os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    
    if not page_id:
        print("Page ID is Missing")
    if not page_access_token:
        print('Page Access Token Is Missing')
    
    try:
        data={
            'message':message,
            'access_token':page_access_token
        }
        url=f"https://graph.facebook.com/{page_id}/feed"
        response=requests.post(
            url,
            data,
            timeout=20
        )
        result=response.json()
        if response.ok and 'id' in result:
            return f'''
           Facebook Post Publish Successfully\n
           Post ID: {result['id']}
        '''
        
        return f'Error {result}'
        
    except Exception as e:
        return f"Error: Facebook Connection Failed {str(e)}"


# print(publish_facebook_post.invoke("This is an Automatic Facebook Post Sent my MollaAi"))
    
    

