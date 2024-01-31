# OBS Sessionize Plugin

This plugin updates text sources with current and next session information from a [Sessionize.com](https://sessionize.com) event.

## How it Works

The plugin works by sending a GET request to the Sessionize API at the specified interval. It then parses the JSON response and updates the specified OBS text sources with the current and next session information.

The plugin also computes a hash of the fetched data and compares it with the hash of the previously fetched data. If the hashes do not match, it means that the session information has been updated. In this case, the plugin writes the new data and its hash to local `json` and `txt` files respectively.

If for some reason the plugin is unable to query the API (for example, due to network issues), it will use the data from the last successful query, which is stored in the local `json` file. This ensures that the plugin can continue to display session information even when the API is unavailable. (You can also dowload the API output to a file in this folder named `schedule_data.json`if you're unable to query it live)


## Requirements

Before you start, ensure you have met the following requirements:

* You have installed the latest version of [Python](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/). Python is the programming language used for this script, and pip is a package manager for Python that allows you to install additional libraries.

* You have a Windows/Linux/Mac machine. This script should be compatible with these three major systems.

* You have read the [OBS Studio](https://obsproject.com/) documentation. This script is intended to be used with OBS Studio, so you should be familiar with how to use it.

* You have installed the `requests` and `pytz` Python libraries. These can be installed via pip using the command `pip install -r requirements.txt`.

* You have a basic understanding of Python programming. While not strictly necessary to use the script, it will help with understanding and troubleshooting any issues that may arise.

Please note that this script is intended to be used with OBS Studio, and as such, you will need to have OBS Studio installed and set up on your machine.

## Configuration

The plugin requires the following settings, configurable from the OBS Script window:

- `URL`: The URL of the Sessionize API Schedule Grid endpoint.
  -  It should be in the format: `https://sessionize.com/api/v2/{event_id}/view/GridSmart`. Make sure to configure the Sessionize API endpoint with "Use UTC timezone for schedule" enabled and Format set to JSON.
  -  More info on [generating a Sessionize API endpoint](https://sessionize.com/playbook/api)
- `Current Title Field`: The name of the text source for the current session title.
- `Current Presenters Field`: The name of the text source for the current session presenters.
- `Next Title Field`: The name of the text source for the next session title.
- `Next Presenters Field`: The name of the text source for the next session presenters.
- `Local Timezone`: The local timezone of the event.
- `Room Name`: The name of the room for which to display session information.
- `Fetch Interval (minutes)`: The interval in minutes at which to fetch new data from the API.

NOTE: You can also set the `Fake Current LOCAL DateTime` setting, formatted `YYYY-MM-DDTHH:MM:SS` to override the current time during testing. Leave this blank for actual use and it will use your current system time.

## Usage

After configuring the plugin, it will automatically update the specified text sources with the current and next session information at the specified fetch interval.






