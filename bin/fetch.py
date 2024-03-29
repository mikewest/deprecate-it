import datetime
import json
import requests
import os
import sys
from datetime import date, timedelta
from jinja2 import Environment, FileSystemLoader

#
# Step 1: Load UseCounter JSON files, and merge them into a single data structure.
# Then use that structure to build up a representation of the last ~2 months of
# data that can be passed to the template.
#
use_counters = {
    # document.domain
    'DocumentDomainBlockedCrossOriginAccess': 2543,
    'DocumentDomainEnabledCrossOriginAccess': 2544,
    'CrossOriginAccessBasedOnDocumentDomain': 4171,

    # SharedArrayBuffer
    'SABConstructed': 3114,
    'SABConstructedWithoutIsolation': 3721,

    # MIME types
    'SameOriginApplicationOctetStream': 2167,
    'SameOriginApplicationXml': 2168,
    'SameOriginTextHtml': 2169,
    'SameOriginTextPlain': 2170,
    'SameOriginTextXml': 2171,
    'SameOriginJSON': 3737,
    'SameOriginOtherBlockedByStrict': 3739,
    'CrossOriginApplicationOctetStream': 2172,
    'CrossOriginApplicationXml': 2173,
    'CrossOriginTextHtml': 2174,
    'CrossOriginTextPlain': 2175,
    'CrossOriginTextXml': 2176,
    'CrossOriginJSON': 3738,
    'CrossOriginOtherBlockedByStrict': 3740,
    'StrictWouldBlockWorker': 3090,

    # CORS-RFC1918
    'LocalInSecurePrivate': 3753,
    'LocalInNonsecurePrivate': 3754,
    'LocalInSecurePublic': 3755,
    'LocalInNonsecurePublic': 3756,
    'PrivateInSecurePublic': 3757,
    'PrivateInNonsecurePublic': 3758,
    'LocalInSecureUnknown': 3759,
    'LocalInNonsecureUnknown': 3760,
    'PrivateInSecureUnknown': 3761,
    'PrivateInNonsecureUnknown': 3762,

    # `javascript:` URLs.
    'ExecutedJavaScriptURL': 2955,
    'ReplacedDocumentViaJavaScriptURL': 215,

    # Bad Markup
    'ClobberedVariableAccessed': 1824,
    'NestedForm': 1972,
    'DuplicateScriptAttribute': 2251,

    # Plugin Elements
    "EmbedLoadedDocument": 3046,
    "EmbedLoadedImage": 3047,
    "EmbedLoadedExternal": 3048,

    # Frames
    "CrossOriginFrameWithoutOptIn": 3752,

    # Module Sharing
    "WASMModuleSharing": 3801,
    "WASMModuleSharingCrossOrigin": 3802,
}

days = set()
data = {}
for key, bucket in use_counters.items():
    print(f"Requesting '{key}'", file=sys.stderr)
    response = json.loads(requests.get("https://chromestatus.com/data/timeline/featurepopularity?bucket_id=%s"%(bucket)).text)
    for item in response:
        days.add(item["date"])
        if item["date"] not in data: data[item["date"]] = {}
        data[item["date"]][bucket] = round(item["day_percentage"] * 100, 5)

beginning = date.fromisoformat(sorted(days)[-90])
end = date.fromisoformat(sorted(days)[-1])
use_counter_days = []
while beginning <= end:
    use_counter_days.append(beginning.isoformat())
    beginning += timedelta(days=1)
use_counter_days = sorted(use_counter_days)[-90:]

use_counter_buckets = {}
for bucket in use_counters.values():
    use_counter_buckets[bucket] = []
    for day in use_counter_days:
        use_counter_buckets[bucket].append(data.get(day, {}).get(bucket, 0))

#
# Step 2: Render some HTML.
#
root = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(root))
template = env.get_template("template.html")

print(template.render(
    datestamp = datetime.date.today(),
    use_counter_days = use_counter_days,
    use_counter_buckets = use_counter_buckets))
