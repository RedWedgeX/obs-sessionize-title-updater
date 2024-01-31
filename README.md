# OBS Sessionize Plugin

This plugin updates text sources with current and next session information from a Sessionize event.

## Installation

Before running the plugin, you need to install the required Python libraries. These libraries are listed in the `requirements.txt` file. To install them, run the following command in your terminal:

```bash
pip install -r requirements.txt
```

## Configuration

The plugin requires the following settings, configurable from the OBS Script window:

- `URL`: The URL of the Sessionize API Schedule Grid endpoint. It should be in the format: `https://sessionize.com/api/v2/{event_id}/view/GridSmart`. Make sure to configure the Sessionize API endpoint with "Use UTC timezone for schedule" enabled and Format set to JSON.
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
