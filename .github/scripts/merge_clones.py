"""Merge the latest GitHub clone response into the stored daily history.

Same merge as https://github.com/MShawon/github-clone-count-badge, without the
step that folds days older than about 100 into YYYY-MM month buckets.
"""

import json

with open("clone.json", encoding="utf-8") as fh:
    now = json.load(fh)

with open("clone_before.json", encoding="utf-8") as fh:
    before = json.load(fh)

timestamps = {
    before["clones"][i]["timestamp"]: i for i in range(len(before["clones"]))
}

latest = dict(before)
for entry in now["clones"]:
    timestamp = entry["timestamp"]
    if timestamp in timestamps:
        latest["clones"][timestamps[timestamp]] = entry
    else:
        latest["clones"].append(entry)

latest["count"] = sum(int(entry["count"]) for entry in latest["clones"])
latest["uniques"] = sum(int(entry["uniques"]) for entry in latest["clones"])

with open("clone.json", "w", encoding="utf-8") as fh:
    json.dump(latest, fh, ensure_ascii=False, indent=4)
