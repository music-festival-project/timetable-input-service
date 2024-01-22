from flask import Flask, request, Response
from config import Config
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date, timedelta
import utilities
import time

app = Flask(__name__)

@app.route("/")
def index():
    return 'timetable input service'

@app.route("/scrape/", methods=['POST'])
def scrape():
    """Takes in a URL of 
    the timetable website to be scraped from the request body. 

    Returns:
        scraped and formatted timetable. 
    """
    request_data = request.get_json()
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(request_data)

    time.sleep(5)
    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, "html.parser")
    driver.quit()
    
    element_list = []

    for i in soup.find_all('span'):
        if i.get_text() == '':
            continue
        if i.has_attr("itemprop"):
            # This ` category:artist` is used later for scraping artist name.
            element_list.append(i.get_text() + ' category:artist')
        if i.has_attr("class"): 
            element_list.append(i.get_text())
            
    NO_STAGES = 17 # 16 stages + 1 for looping
    stage_indices = []
    for i in range(1, NO_STAGES):
        stage_indices.append(element_list.index(f'{i}'))
        

    start_stage_indices = [x + 1 for x in stage_indices]

    end_string_identifier = '@ 12 augustus 2022'
    end_string_index = element_list.index(end_string_identifier)
    end_stage_indices = [x+1 for x in stage_indices[1:]]
    end_stage_indices.append(end_string_index)
    
    assert len(start_stage_indices) == len(end_stage_indices)
    start_stops = list(zip(start_stage_indices, end_stage_indices))
    
    sliced_list_of_sets = [element_list[slice(*s)] for s in start_stops]
    
    festival_set_dict = {}
    for item in sliced_list_of_sets:
        stage_name = item[0]
        stage_performer_data = item[1:]
        festival_set_dict[stage_name] = stage_performer_data
        
    festival_date = date(2022, 4, 7)

    stage_datetime_map = {}
    festival_set_dict = utilities.get_performer_data_per_stage(sliced_list_of_sets)
    for stage, stage_list in festival_set_dict.items():
        time_stamp_indices = utilities.get_timestamp_indices(stage_list)
        time_stamp_artist_map = utilities.map_timestamp_to_artist(time_stamp_indices, stage_list)
        substring_to_clean = "category:artist"
        cleaned_time_stamp_artist_map = utilities.clean_artist_substring_tags(time_stamp_artist_map, substring_to_clean)
        datetime_artist_map = utilities.map_to_datetime_keys(cleaned_time_stamp_artist_map, festival_date)
        stage_datetime_map[stage] = datetime_artist_map
        
    festival_df = pd.DataFrame()
    for stage, setlist in stage_datetime_map.items():
        setlist = utilities.unpack_festival_datetime_artist_dict(setlist, stage)
        setlist_df = pd.DataFrame.from_dict(setlist)
        festival_df = pd.concat([festival_df, setlist_df], axis = 0)
        
    entries = festival_df["start"] > festival_df["end"]
    festival_df.loc[entries, "end"] = festival_df.loc[entries, "end"].apply(lambda end: end + timedelta(days=1))
    
    out = festival_df.to_json(orient='records')
    with open("scraper_result.json", "w") as outfile:
        outfile.write(out)
    return Response()
    
if __name__ == "__main__":
    app.run(port=Config.PORT)