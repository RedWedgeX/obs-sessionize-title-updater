import obspython as obs
import requests
from datetime import datetime
import json
import pytz
import hashlib

# Properties
last_fetch_time             = None
schedule_data               = None

local_timezone = datetime.now(pytz.timezone('America/Phoenix')).strftime('%Z')


def update_source_dropdowns(props):
    # Get a list of all sources
    sources = obs.obs_enum_sources()
    list_of_sources = [(obs.obs_source_get_name(source), obs.obs_source_get_name(source)) for source in sources]

    obs.source_list_release(sources)

    # Add dropdown lists for the source names
    for source_name in ["current_title_source", "current_presenters_source", "next_title_source", "next_presenters_source"]:
        prop = obs.obs_properties_get(props, source_name)
        obs.obs_property_list_clear(prop)
        for item in list_of_sources:
            obs.obs_property_list_add_string(prop, *item)

            
            
def script_description():
    return "Updates text sources with current and next session information."

def script_update(settings):
    global url, current_title_source_name, current_presenters_source_name, next_title_source_name, next_presenters_source_name, fake_current_datetime, local_timezone, room_name, fetch_interval_minutes, enabled
    url = obs.obs_data_get_string(settings, "url")
    enabled = obs.obs_data_get_bool(settings, "enabled")
    current_title_source_name = obs.obs_data_get_string(settings, "current_title_source")
    current_presenters_source_name = obs.obs_data_get_string(settings, "current_presenters_source")
    next_title_source_name = obs.obs_data_get_string(settings, "next_title_source")
    next_presenters_source_name = obs.obs_data_get_string(settings, "next_presenters_source")
    fake_current_datetime = obs.obs_data_get_string(settings, "fake_current_datetime")
    local_timezone = obs.obs_data_get_string(settings, "local_timezone")
    room_name = obs.obs_data_get_string(settings, "room_name")
    fetch_interval_minutes = obs.obs_data_get_int(settings, "fetch_interval_minutes")

    props = obs.obs_properties_create()
    update_source_dropdowns(props)
    obs.obs_properties_destroy(props)
    
def script_defaults(settings):
    obs.obs_data_set_default_bool(settings, "enabled", False)
    obs.obs_data_set_default_string(settings, "url", "")
    obs.obs_data_set_default_string(settings, "current_title_source", "")
    obs.obs_data_set_default_string(settings, "current_presenters_source", "")
    obs.obs_data_set_default_string(settings, "next_title_source", "")
    obs.obs_data_set_default_string(settings, "next_presenters_source", "")
    obs.obs_data_set_default_string(settings, "fake_current_datetime", "")
    obs.obs_data_set_default_string(settings, "local_timezone", local_timezone)
    obs.obs_data_set_default_string(settings, "room_name", "")
    obs.obs_data_set_default_int(settings, "fetch_interval_minutes", 5)

    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    
    # Get a list of all sources
    sources = obs.obs_enum_sources()
    list_of_sources = [(obs.obs_source_get_name(source), obs.obs_source_get_name(source)) for source in sources]

    obs.source_list_release(sources)

    # Add dropdown lists for the source names
    for source_name in ["current_title_source", "current_presenters_source", "next_title_source", "next_presenters_source"]:
        prop = obs.obs_properties_add_list(props, source_name, f"{source_name.replace('_', ' ').title()} Field", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
        for item in list_of_sources:
            obs.obs_property_list_add_string(prop, *item)

    obs.obs_properties_add_int(props, "fetch_interval_minutes", "Fetch Interval (minutes)", 1, 60, 1)

    # Get a list of all timezones
    list_of_timezones = [(tz, tz) for tz in pytz.all_timezones]

    # Add dropdown list for the local timezone
    prop = obs.obs_properties_add_list(props, "local_timezone", "Local Timezone", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    for item in list_of_timezones:
        obs.obs_property_list_add_string(prop, *item)

    obs.obs_properties_add_text(props, "url", "URL", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "fake_current_datetime", "Fake Current LOCAL DateTime (format: YYYY-MM-DDTHH:MM:SS)", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "room_name", "Room Name", obs.OBS_TEXT_DEFAULT)

    return props
def fetch_data_from_api(api_url):
    # Send a GET request to the API
    response = requests.get(api_url)
    # Parse the JSON response
    data = response.json()
    # Compute a hash of the data for comparison with the old data
    data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    old_data_hash = None
    try:
        # Try to open the file containing the hash of the old data
        with open('data_hash.txt', 'r') as f:
            # Read the old data hash
            old_data_hash = f.read().strip()
    except FileNotFoundError:
        # If the file does not exist, do nothing
        pass

    # If the old data hash does not match the new data hash
    if old_data_hash != data_hash:
        # Open the file to store the new data
        with open('schedule_data.json', 'w') as f:
            # Write the new data to the file
            json.dump(data, f)
        # Open the file to store the new data hash
        with open('data_hash.txt', 'w') as f:
            # Write the new data hash to the file
            f.write(data_hash)

def get_data_from_local():
    # Open and read the schedule data from the JSON file
    with open('schedule_data.json', 'r') as f:
        data = json.load(f)

    # Set the current time in the local timezone
    local_tz = pytz.timezone(local_timezone)
    current_time = datetime.now(local_tz)

    # If a fake current datetime is provided, use that instead
    if fake_current_datetime:
        current_time = datetime.strptime(fake_current_datetime, "%Y-%m-%dT%H:%M:%S")
        current_time = local_tz.localize(current_time)

    # Convert the current time to UTC
    current_time = current_time.astimezone(pytz.utc).isoformat()

    # Initialize variables for the current and next session titles and presenters
    current_title = None
    current_presenters = None
    next_title = None
    next_presenters = None

    # Loop through each day in the schedule data
    for day in data:
        # Loop through each room, filtering for the specific room name
        for room in [r for r in day['rooms'] if r['name'] == room_name]:
            # Loop through each session in the room
            for session in room['sessions']:
                # If the current time falls within the session's start and end times, set the current session title and presenters
                if session['startsAt'] <= current_time < session['endsAt']:
                    current_title = session['title']
                    current_presenters = ', '.join(speaker['name'] for speaker in session['speakers'])
                # If the current time is before a session's start time and the next session title has not been set yet, set the next session title and presenters
                elif session['startsAt'] > current_time and next_title is None:
                    next_title = session['title']
                    next_presenters = ', '.join(speaker['name'] for speaker in session['speakers'])

    # Return the current and next session titles and presenters
    return current_title, current_presenters, next_title, next_presenters

def set_text(source_name, text):
    # Get the source by its name
    source = obs.obs_get_source_by_name(source_name)
    
    # If the source exists
    if source is not None:
        # Create a new OBS data instance
        settings = obs.obs_data_create()
        
        # Set the 'text' field of the OBS data instance to the provided text
        obs.obs_data_set_string(settings, "text", text)
        
        # Update the source with the new settings
        obs.obs_source_update(source, settings)
        
        # Release the OBS data instance to free up memory
        obs.obs_data_release(settings)
        
        # Release the source to free up memory
        obs.obs_source_release(source)
    else:
        # If the source does not exist, log a warning
        obs.script_log(obs.LOG_WARNING, f"Source {source_name} does not exist.")
        
        
# Function to update the last fetch time
def update_last_fetch_time():
    global last_fetch_time
    # Get the current time in UTC and format it as an ISO 8601 string
    last_fetch_time = datetime.utcnow().isoformat()
    # Open the file 'last_fetch_time.txt' in write mode
    with open('last_fetch_time.txt', 'w') as f:
        # Write the last fetch time to the file
        f.write(last_fetch_time)

# Function to get the last fetch time
def get_last_fetch_time():
    try:
        # Open the file 'last_fetch_time.txt' in read mode
        with open('last_fetch_time.txt', 'r') as f:
            # Read the last fetch time from the file
            last_fetch_time_str = f.read()
            # Convert the last fetch time from an ISO 8601 string to a datetime object and return it
            return datetime.fromisoformat(last_fetch_time_str)
    except FileNotFoundError:
        # If the file 'last_fetch_time.txt' does not exist, return None
        return None
    
# Function to be called every 'seconds' seconds
def script_tick(seconds):
    global last_fetch_time
    if not enabled:
        return


    # Fetch data every fetch_interval_minutes
    if last_fetch_time is None or (datetime.utcnow() - last_fetch_time).total_seconds() >= fetch_interval_minutes * 60:
        try:
            # Fetch data from the API
            fetch_data_from_api(url)
            # Update last_fetch_time in the file
            update_last_fetch_time()
            # Get the updated last_fetch_time from the file
            last_fetch_time = get_last_fetch_time()
        except requests.exceptions.RequestException:
            # If fetching data from the API fails, log a warning and use the last fetched data
            obs.script_log(obs.LOG_WARNING, "Failed to fetch data from API. Using the last fetched data.")

    # Get the current and next session titles and presenters from the local data
    current_title, current_presenters, next_title, next_presenters = get_data_from_local()
    # Set the text of the current and next title and presenter sources
    set_text(current_title_source_name, current_title)
    set_text(current_presenters_source_name, current_presenters)
    set_text(next_title_source_name, next_title)
    set_text(next_presenters_source_name, next_presenters)
    

# Initialize last_fetch_time when the script starts
last_fetch_time = get_last_fetch_time()
