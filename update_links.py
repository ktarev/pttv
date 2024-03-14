import os
import base64
import re
import pandas as pd
import requests

# Channel mapping
channel_mapping = {
    '#EXTINF:-1,EuroSport 1 BG': 'https://www.seirsanduk.net/?player=1&id=hd-eurosport-1-hd&pass=',
    '#EXTINF:-1,EuroSport 2 BG': 'https://www.seirsanduk.net/?player=1&id=hd-eurosport-2-hd&pass=',
    '#EXTINF:-1, Kitchen 24': 'https://www.seirsanduk.net/?player=1&id=hd-24-kitchen-hd&pass=',
    '#EXTINF:-1, BNT 1': 'https://www.seirsanduk.net/?player=1&id=hd-bnt-1-hd&pass=',
    '#EXTINF:-1, BNT 3': 'https://www.seirsanduk.net/?player=1&id=hd-bnt-3-hd&pass=',
    '#EXTINF:-1, Max Sport 4': 'https://www.seirsanduk.net/?player=1&id=hd-max-sport-4-hd&pass=',
    '#EXTINF:-1, Max Sport 3': 'https://www.seirsanduk.net/?player=1&id=hd-max-sport-3-hd&pass=',
    '#EXTINF:-1, Max Sport 3': 'https://www.seirsanduk.net/?player=1&id=hd-max-sport-3-hd&pass=',
    '#EXTINF:-1, Diema Sport 3': 'https://www.seirsanduk.net/?player=1&id=hd-diema-sport-3-hd&pass=',
    '#EXTINF:-1, Nat Geo Wild': 'https://www.seirsanduk.net/?player=1&id=hd-nat-geo-wild-hd&pass=',
    '#EXTINF:-1, Food Network BG': 'https://www.seirsanduk.net/?player=1&id=hd-food-network-hd&pass=',
    '#EXTINF:-1, Epic Drama': 'https://www.seirsanduk.net/?player=1&id=hd-epic-drama-hd&pass=',
    '#EXTINF:-1, Discovery Channel': 'https://www.seirsanduk.net/?player=1&id=hd-discovery-channel-hd&pass=',
    '#EXTINF:-1, Star Crime': 'https://www.seirsanduk.net/?player=1&id=hd-star-crime-hd&pass=',
    '#EXTINF:-1,Travel TV': 'https://www.seirsanduk.net/?player=1&id=hd-travel-channel-hd&pass=',
    '#EXTINF:-1, Nova News': 'https://www.seirsanduk.net/?player=1&id=hd-nova-news-hd&pass=',
    '#EXTINF:-1, 1+1': 'https://iptv-web.app/UA/1Plus1.ua/'
    # Add more channels as needed
}

def update_links(channel, source_link):
    with requests.Session() as session:
        response = session.get(source_link)
        match = re.search(r'https://[^\s"]+\.m3u8(?:\?[^\s"]*)?', response.text)
        if match:
            m3u_link = match.group(0)
            print(f"Fetched m3u link for {channel}: {m3u_link}")
            return m3u_link
        else:
            print(f"No m3u link found for {channel}")
            return None

data_list = []

for channel, source_link in channel_mapping.items():
    fetched_link = update_links(channel, source_link)
    data_list.append({'Channel': channel, 'SourceLink': source_link, 'LinkToUpdate': fetched_link})

channel_df = pd.DataFrame(data_list)

file_path = 'TV.m3u'

# Read the contents of the TV.m3u file
with open(file_path, 'r') as file:
    tv_m3u_content = file.read()

tv_m3u_content_updated = tv_m3u_content

for index, row in channel_df.iterrows():
    channel_name = row['Channel']
    link_to_update = row['LinkToUpdate']
    if link_to_update is not None:
        pattern = re.escape(channel_name) + r'\n(https://[^\n]+)'
        tv_m3u_content_updated = re.sub(pattern, f"{channel_name}\n{link_to_update}", tv_m3u_content_updated)

# Write the updated content back to the file
with open(file_path, 'w') as file:
    file.write(tv_m3u_content_updated)

print(f"File {file_path} successfully updated.")
