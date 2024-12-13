from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Final

import config

import xtream


def writeJSON(filename: str, data: dict[str, Any] | list[Any]) -> None:  # noqa: N802
    if config.write_files == 1:
        p = Path(f"data/{filename}")
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w") as fp:
            json.dump(data, fp)


def EPGString(channel_id: str | None) -> str:  # noqa: N802
    result = "-"
    if not isinstance(channel_id, NoneType):
        result = channel_id
    return result


def VODName(json: dict[str, Any]) -> str | int:  # noqa: N802
    try:
        return json["name"]
    except KeyError:
        return 0


TZ: Final[datetime.timezone] = datetime.UTC
providername = config.provider["name"]

x = xtream.XTream(config.provider["server"], config.provider["username"], config.provider["password"])

r = x.authenticate()

data = r.json()

writeJSON(providername + "-auth.json", data)

user_username = data["user_info"]["username"]
user_status = data["user_info"]["status"]
user_is_trial = data["user_info"]["is_trial"]
user_created_at = str(data["user_info"]["created_at"])
if user_created_at != "None":
    user_created_at = datetime.datetime.fromtimestamp(float(data["user_info"]["created_at"].encode("ascii", "ignore")), tz=TZ).isoformat()
user_auth = data["user_info"]["auth"]
user_allowed_output_formats = data["user_info"]["allowed_output_formats"]
user_exp_date = str(data["user_info"]["exp_date"])
if user_exp_date != "None":
    user_exp_date = datetime.datetime.fromtimestamp(float(data["user_info"]["exp_date"].encode("ascii", "ignore")), tz=TZ).isoformat()
user_active_cons = data["user_info"]["active_cons"]
user_message = data["user_info"]["message"]
user_password = data["user_info"]["password"]
user_max_connections = data["user_info"]["max_connections"]

server_https_port = data["server_info"]["https_port"]
server_url = data["server_info"]["url"]
server_time_now = data["server_info"]["time_now"]
server_server_protocol = data["server_info"]["server_protocol"]
server_timestamp_now = str(data["server_info"]["timestamp_now"])
if server_timestamp_now != "None":
    server_timestamp_now = datetime.datetime.fromtimestamp(float(data["server_info"]["timestamp_now"]), tz=TZ).isoformat()
server_timezone = data["server_info"]["timezone"]
server_rtmp_port = data["server_info"]["rtmp_port"]
server_port = data["server_info"]["port"]


# printing the output
print("Account information:\n")

print(f"Username:               {user_username}")
print(f"Password:               {user_password}")
print(f"Message:                {user_message}")
print(f"Status:                 {user_status}")
print(f"Authorized:             {user_auth}")
print(f"Trial:                  {user_is_trial}")
print(f"Created:                {user_created_at}")
print(f"Expiration:             {user_exp_date}")
print(f"Allowed output formats: {user_allowed_output_formats}")
print(f"Max Connections:        {user_max_connections}")
print(f"Active connections:     {user_active_cons}")

print("\nServer information:\n")

print(f"Server address:         {server_url}")
print(f"Protocol:               {server_server_protocol}")
print(f"Port:                   {server_port}")
print(f"HTTPS port:             {server_https_port}")
print(f"RTMP port:              {server_rtmp_port}")
print(f"Timezone:               {server_timezone}")
print(f"Time now:               {server_time_now}")
print(f"Timestamp now:          {server_timestamp_now}")

total_streams = 0
entry: Any

print("\n\nCategory information:\n")

r = x.categories(x.live_type)

try:
    live_category_data = r.json()

    writeJSON(providername + "-live-categories.json", live_category_data)

    s = x.streams(x.live_type)
    live_stream_data = s.json()

    writeJSON(providername + "-live-streams.json", live_stream_data)

    # live_category_data is list of dict
    live_names = []
    live_ids = []
    pos = 0
    while pos <= len(live_category_data) - 1:
        cat_streams_data = [item for item in live_stream_data if item["category_id"] == live_category_data[pos]["category_id"]]
        live_names.append(
            "{:<40s} - {:>3s} - {:4d} streams".format(
                live_category_data[pos]["category_name"], live_category_data[pos]["category_id"], len(cat_streams_data)
            )
        )
        total_streams += len(cat_streams_data)
        live_ids.append(live_category_data[pos]["category_id"])
        pos += 1
    live_names.sort()

    if len(live_category_data) > 0:
        print(f"Live Category Count:                             {len(live_category_data):>4d}")
        print("=====================================================")

        for _i, entry in enumerate(live_names):
            print(entry)

        print("=====================================================\n")
except ValueError as err:
    print(f"Value error: {err}")

r = x.categories(x.vod_type)

try:
    vod_category_data = r.json()

    writeJSON(providername + "-vod-categories.json", vod_category_data)

    s = x.streams(x.vod_type)
    vod_stream_data = s.json()

    writeJSON(providername + "-vod-streams.json", vod_stream_data)

    vod_names = []
    vod_ids = []
    pos = 0
    while pos <= len(vod_category_data) - 1:
        cat_streams_data = [item for item in vod_stream_data if item["category_id"] == vod_category_data[pos]["category_id"]]
        vod_names.append(
            "{:<40s} - {:>3s} - {:4d} streams".format(
                vod_category_data[pos]["category_name"], vod_category_data[pos]["category_id"], len(cat_streams_data)
            )
        )
        total_streams += len(cat_streams_data)
        vod_ids.append(vod_category_data[pos]["category_id"])
        pos += 1
    vod_names.sort()

    if len(vod_category_data) > 0:
        print(f"VOD Category Count:                              {len(vod_category_data):>4d}")
        print("=====================================================")

        for _i, entry in enumerate(vod_names):
            print(entry)

        print("=====================================================\n")
except ValueError as err:
    print(f"Value error: {err}")

r = x.categories(x.series_type)
try:
    series_category_data = r.json()

    writeJSON(providername + "-series-categories.json", series_category_data)

    s = x.streams(x.series_type)
    series_stream_data = s.json()

    writeJSON(providername + "-series-streams.json", series_stream_data)

    series_names = []
    series_ids = []

    pos = 0
    while pos <= len(series_category_data) - 1:
        cat_streams_data = [item for item in series_stream_data if item["category_id"] == series_category_data[pos]["category_id"]]
        writeJSON(series_category_data[pos]["category_id"] + "-stream-data.json", cat_streams_data)
        series_names.append("{:<47s} - {:>3s}".format(series_category_data[pos]["category_name"], series_category_data[pos]["category_id"]))
        total_streams += len(cat_streams_data)
        series_ids.append(series_category_data[pos]["category_id"])
        pos += 1
    series_names.sort()

    if len(series_category_data) > 0:
        print(f"Series Category Count:                           {len(series_category_data):>4d}")
        print("=====================================================")

        for _i, entry in enumerate(series_names):
            print(entry)

        print("=====================================================\n")
except ValueError as err:
    print(f"Value error: {err}")

print(f"Total Stream Count:     {total_streams}\n")

NoneType = type(None)

if config.display_live_info == 1:
    live_category_data.sort(key=VODName)
    for _i, entry in enumerate(live_category_data):
        print("\n\nStreams for Live category {} - {}:\n".format(entry["category_id"], entry["category_name"]))
        cat_streams_data = [item for item in live_stream_data if item["category_id"] == entry["category_id"]]
        print("{:<75s} {:>5s} {:>4s} ".format("name", "ID", "EPG?"))
        print("======================================================================================")
        for _i, stream in enumerate(cat_streams_data):
            print("{:<75s} {:>5d} {:>4s}".format(stream["name"], stream["stream_id"], EPGString(stream["epg_channel_id"])))
        print("======================================================================================")

if config.display_vod_info == 1:
    for _i, entry in enumerate(vod_category_data):
        print("\n\nStreams for VOD category {} - {}:\n".format(entry["category_id"], entry["category_name"]))
        cat_streams_data = [item for item in vod_stream_data if item["category_id"] == entry["category_id"]]
        cat_streams_data.sort(key=VODName)
        print("{:<75s} {:>5s} {:>5s} {:>4s} {:<6s} {:<6s} {:<9s} ".format("name", "ID", "Type", "Ext", "Video", "Audio", "W x H"))
        print("===================================================================================================================")
        for _i, stream in enumerate(cat_streams_data):
            # {u'direct_source': u'',
            #  u'rating': u'',
            #  u'added': u'1518032077',
            #  u'num': 1776,
            #  u'name': u'Linda Sweet Bare Love',
            #  u'stream_type': u'movie',
            #  u'stream_id': 17254,
            #  u'custom_sid': None,
            #  u'stream_icon': u'',
            #  u'container_extension': u'mp4',
            #  u'category_id': u'102',
            #  u'rating_5based': 0}
            r = x.vod_info_by_id(stream["stream_id"])
            vod_stream_info = r.json()

            if config.write_vod_info_files == 1:
                writeJSON(providername + "-vod-" + str(stream["stream_id"]) + "-info.json", vod_stream_info)

            try:
                vcodec = vod_stream_info["info"]["video"]["codec_name"]
                acodec = vod_stream_info["info"]["audio"]["codec_name"]
                width = vod_stream_info["info"]["video"]["width"]
                height = vod_stream_info["info"]["video"]["height"]
            except TypeError:
                vcodec = "none"
                acodec = "none"
                width = 0
                height = 0
            except KeyError:
                vcodec = "none"
                acodec = "none"
                width = 0
                height = 0
            print(
                "{:<75s} {:>5d} {:>5s} {:>4s} {:<6s} {:<6s} {:<4d}x{:<4d} ".format(
                    stream["name"], stream["stream_id"], stream["stream_type"], stream["container_extension"], vcodec, acodec, width, height
                )
            )
        print("===================================================================================================================")

if config.display_series_info == 1:
    print("{:<60s} {:>5s} {:>3s} {:>3s} ".format("name", "ID", "S", "E"))
    print("==========================================================================")
    for _i, entry in enumerate(series_category_data):
        #     print('\n\nEpisodes for series category {} - {}:\n'.format(entry['category_id'],entry['category_name'])
        cat_streams_data = [item for item in series_stream_data if item["category_id"] == entry["category_id"]]
        for _i, stream in enumerate(cat_streams_data):
            r = x.series_info_by_id(stream["series_id"])
            try:
                series_info = r.json()

                if config.write_series_info_files == 1:
                    writeJSON(providername + "-series-" + str(stream["series_id"]) + "-info.json", series_info)

                season_count = len(series_info["episodes"])
                episode_count = 0
                for _i, ep_entry in enumerate(series_info["episodes"]):
                    episode_count += len(series_info["episodes"][str(ep_entry)])
                print("{:<60s} {:>5d} {:>3d} {:>3d} ".format(stream["name"], stream["series_id"], season_count, episode_count))
            except ValueError as err:
                print(f"Value error: {err} on series {err}")
    print("==========================================================================")
