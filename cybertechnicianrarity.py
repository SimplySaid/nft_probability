import hashlib
import json
import requests
import urllib.request

images = dict()

with open("CyberTechnician-metadata.json") as f:
    jdata = json.load(f)

for row in jdata:
    address = requests.get(row['arweaveUri']).json()
    image_url = address['image']

    if image_url not in images.keys():
        images.update({image_url: 1})
    else:
        images[image_url] += 1

print(images)
    # print(image_url)
    # img = urllib.request.urlretrieve(image_url)
    # print(img[1])
    # #hashstr = hashlib.sha1(open(img).read()).hexdigest()

    # #print(hashstr)

    
    

