"""Merge the latest GitHub view response into the stored daily history.

Same merge as the MShawon traffic.py gist, without the step that folds days
older than about 100 into YYYY-MM month buckets.
"""

import json

with open("traffic.json", encoding="utf-8") as fh:
    now = json.load(fh)

with open("traffic_before.json", encoding="utf-8") as fh:
    before = json.load(fh)

timestamps = {
    before["views"][i]["timestamp"]: i for i in range(len(before["views"]))
}

latest = dict(before)
for entry in now["views"]:
    timestamp = entry["timestamp"]
    if timestamp in timestamps:
        latest["views"][timestamps[timestamp]] = entry
    else:
        latest["views"].append(entry)

latest["count"] = sum(int(entry["count"]) for entry in latest["views"])
latest["uniques"] = sum(int(entry["uniques"]) for entry in latest["views"])

with open("traffic.json", "w", encoding="utf-8") as fh:
    json.dump(latest, fh, ensure_ascii=False, indent=4)
