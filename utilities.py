import re
import pandas as pd
from datetime import date, time, datetime

def is_timestamp_in_text(input_text: str) -> bool:
    """Given an input string, return Bool if it matches the time index.
    
    i.e.
        input_text = 'zo\xa013:30 - 14:30:' ==> True
    """
    pattern = re.compile(r"[0-9]+:[0-9]+\s-\s[0-9]+:[0-9]+", re.IGNORECASE)
    result = pattern.search(input_text)
    if result is None:
        return False
    return True

def get_timestamp_indices(stage_list: list) -> list:
    """Given a setlist for a stage, 
    return a list of indices of the list elements that contain timestamp.
    
    """
    timestamp_indices = []
    for item in stage_list:
        if is_timestamp_in_text(item):
            index = stage_list.index(item)
            timestamp_indices.append(index)
    return timestamp_indices

def get_performer_data_per_stage(sliced_list_of_sets: list[list]) -> dict:
    """TO-DO
    """
    festival_set_dict = {}
    for item in sliced_list_of_sets:
        stage_name = item[0]
        stage_performer_data = item[1:]
        festival_set_dict[stage_name] = stage_performer_data
    return festival_set_dict

def map_timestamp_to_artist(timestamp_indices: list, stage_set_list) -> dict:
    """Given a list of timestamp indices and list of festival sets,
    return a dictionary containing a timestamp and corresponding artist. 
    """
    timestamp_artist_map = {}
    for ts_index in timestamp_indices:
        time_stamp = stage_set_list[ts_index]
        timestamp_artist_map[time_stamp] = list()
        # Given the index of a timestamp, look at the next n lines over
        no_lines_to_view = 3
        start_index = ts_index
        end_index = ts_index + no_lines_to_view
        for i in range(start_index, end_index):
            item = stage_set_list[i]
            if 'category:artist' in item:
                timestamp_artist_map[time_stamp].append(item)
    return timestamp_artist_map

def clean_artist_substring_tags(time_stamp_artist_map: dict, substring_to_clean: str):
    """Given a dictionary,
    where the keys are timestamps and the values are artist names,
    construct a dataframe with a specificed column_name. 
    """
    artists = {}
    for k,v, in time_stamp_artist_map.items():
        if len(v) > 0:
            artist = list(set(v))[0]
            artist = artist.replace(substring_to_clean, "").strip()
            artists[k] = artist
    return artists
    
def df_from_stage_setlist(time_stamp_artist_map: dict, column_name: str):
    """Given a dictionary,
    where the keys are timestamps and the values are artist names,
    construct a dataframe with a specificed column_name. 
    """
    timestamps = []
    artists = []
    for k,v, in time_stamp_artist_map.items():
        if len(v) > 0:
            artist = list(set(v))[0]
            artist = artist.replace("category:artist", "").strip()
            artists.append(artist)
            timestamps.append(str(k))
            
    df = pd.DataFrame({
        "artists":artists,
        "timestamps": timestamps
    })
    df = df.assign(stage=f"{column_name}")
    return df


def make_date(date: date, time: time) -> datetime:
    return datetime.combine(date, time)

def timestamp_strings_to_times(timestamp_string: str, split_clean_nr: int = 5):
    """Given a timetstamp string, 
    extract the start and end time from the string.
    Split_clean_nr indicates the position of the character, 
    that is the first/last character of the time in the actual time string.
    
    Convert start and end string to Python datetime objects.
    """
    start, end = timestamp_string.split(" - ")
    start = start[-abs(split_clean_nr):]
    end = end[:split_clean_nr]
    start_time = datetime.strptime(start, '%H:%M').time()
    end_time = datetime.strptime(end, '%H:%M').time()
    return (start_time, end_time)


def combine_date_into_times(times: tuple, festival_date: date) -> tuple:
    start_time, end_time = times
    start_datetime = make_date(festival_date, start_time)
    end_datetime = make_date(festival_date, end_time)
    return (start_datetime, end_datetime)


def map_to_datetime_keys(timestamp_artist_map, festival_date: date):
    datetime_map = {}
    for timestamp_string, value in timestamp_artist_map.items():
        try:
            time_tuple = timestamp_strings_to_times(timestamp_string)
            datetime_tuple = combine_date_into_times(time_tuple, festival_date)
            datetime_map[datetime_tuple] = value
        except Exception as err:
            print(f"{type(err)} | {err}")
            print(f"Failed on timestamp_string == {timestamp_string}")
    return datetime_map

def unpack_festival_datetime_artist_dict(datetime_artist_dict, stage_name: str):
    performances = []
    for key, value in datetime_artist_dict.items():
        start, end = key
        performance_dict = {}
        performance_dict["start"] = start
        performance_dict["end"] = end
        performance_dict["artist"] = value
        performance_dict["stage"] = stage_name
        performances.append(performance_dict)
    return performances