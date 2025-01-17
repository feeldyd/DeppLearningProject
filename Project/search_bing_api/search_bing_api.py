from requests import exceptions
import argparse
import requests
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True,  help="search query to search Bing Image API for")
ap.add_argument("-o", "--output", required=True,  help="path to output directory of images")
args = vars(ap.parse_args())

API_KEY = "330925b3af7149e8bb27bc26ba22b62e"
MAX_RESULTS = 100
GROUP_SIZE = 10

URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

EXCEPTIONS = set([IOError, FileNotFoundError,
                  exceptions.RequestException, exceptions.HTTPError,  exceptions.ConnectionError, exceptions.Timeout])

term = args["query"]
headers = {"Ocp-Apim-Subscription-Key" : API_KEY}
params = {"q": term, "offset": 0, "count": GROUP_SIZE}


print("[INFO] searching Bing API for '{}'".format(term))
search = requests.get(URL, headers=headers, params=params)
search.raise_for_status()

results = search.json()
estNumResults = min(results["totalEstimatedMatches"], MAX_RESULTS)
print("[INFO] {} total results for '{}'".format(estNumResults, term))

total = 0


for offset in range(0, estNumResults, GROUP_SIZE):
# update the search parameters using the current offset, then
# make the request to fetch the results
    print("[INFO] making request for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, estNumResults))
    params["offset"] = offset
    search = requests.get(URL, headers=headers, params=params)
    search.raise_for_status()
    results = search.json()
    print("[INFO] saving images for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, estNumResults))

    for v in results["value"]:
    # 이미지 다운로드 처리
        try:
            # make a request to download the image
            print("[INFO] fetching: {}".format(v["contentUrl"]))
            r = requests.get(v["contentUrl"], timeout=30)

             # build the path to the output image
            ext = v["contentUrl"][v["contentUrl"].rﬁnd("."):]
            p = os.path.sep.join([args["output"], "{}{}".format(str(total).zﬁll(8), ext)])

            # write the image to disk
            f = open(p, "wb")
            f.write(r.content)
            f.close()

        except Exception as e:

            # check to see if our exception is in our list of    # exceptions to check for
            if type(e) in EXCEPTIONS:
                print("[INFO] skipping:{}".format(v["contentUrl"]))
                continue

        # try to load the image from disk
        image = cv2.imread(p)

        if image is None:
            print("[INFO] deleting: {}".format(p))
            os.remove(p)
            continue
        total += 1
