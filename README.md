# py-xtream-codes
Python module to interact with Xtream-Codes IPTV servers

https://forum.xtream-codes.com/topic/3511-how-to-player-api-v2/

## Initialize:

```python
import xtream

# Iris
server   = config.provider['server']
username = config.provider['username']
password = config.provider['password']

x = xtream.XTream(server, username, password)
r = x.authenticate()
```

## Authentication

```python
r = x.authenticate()

data = r.json()
```
returns:
```json
{
   "user_info":{
      "username":"11111111",
      "password":"22222222",
      "message":"Welcome back my friends",
      "auth":1,
      "status":"Active",
      "exp_date":"1558621852",
      "is_trial":"0",
      "active_cons":"0",
      "created_at":"1542987052",
      "max_connections":"2",
      "allowed_output_formats":[
         "m3u8",
         "ts",
         "rtmp"
      ]
   },
   "server_info":{
      "url":"111.222.333.444",
      "port":"83",
      "https_port":"85",
      "server_protocol":"http",
      "rtmp_port":"84",
      "timezone":"Europe\/London",
      "timestamp_now":1545170300,
      "time_now":"2018-12-18 21:58:20"
   }
}
```
## Streams

Three types of streams:
```python
live_type = "Live"
vod_type = "VOD"
series_type = "Series"
```

## Stream Categories

```python
r = x.categories(x.live_type)
live_category_data = r.json()

r = x.categories(x.vod_type)
vod_category_data = r.json()

r = x.categories(x.series_type)
series_category_data = r.json()
```

## Streams
```python
r = x.streams(x.live_type)
live_stream_data = r.json()

r = x.streams(x.vod_type)
vod_stream_data = r.json()

r = x.streams(x.series_type)
series_stream_data = r.json()
```

## Streams by Category
```python
r = x.streams_by_category(x.live_type, live_category_data[0]['category_id'])
live_stream_data = r.json()

r = x.streams_by_category(x.vod_type, vod_category_data[0]['category_id'])
vod_stream_data = r.json()

r = x.streams_by_category(x.series_type, series_category_data[0]['category_id'])
series_stream_data = r.json()
```

## Series Info
```python
r = x.series_info_by_id(series_stream_data[0]['id'])
series_info_data = r.json()
```

## GET VOD Info
```python
r = x.vod_info_by_id(vod_stream_data[0]['num'])
vod_info_data = r.json()
```

## GET short_epg for LIVE Streams (same as stalker portal, prints the next X EPG that will play soon)
"Limit" is count of EPG listings wanted
```python
r = x.live_epg_by_stream(live_stream_data[0]['stream_id'])
live_epg_data = r.json()

r = x.live_epg_by_stream_and_limit(live_stream_data[0]['stream_id'], 24)
live_epg_data = r.json()
```

##  GET ALL EPG for LIVE Streams (same as stalker portal, but it will print all epg listings regardless of the day)
```python
r = x.all_live_epg_by_stream(live_stream_data[0]['stream_id'])
live_epg_data = r.json()
```

## Full EPG List for all Streams
```python
r = x.all_epg()
live_epg_data = r.json()
```

# Quickstart

1. Clone the repo locally
1. Install [python-poetry](https://python-poetry.org/docs/)
1. `poetry install`
1. `poetry shell`
1. Copy `config.py.example` to `config.py`.
1. edit `config.py` as required
1. run `python xtream-testing.py`
