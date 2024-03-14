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
    '#EXTINF:-1, TLC': 'https://www.seirsanduk.net/?player=1&id=tlc&pass=',
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
channel_df['LinkToUpdate'] = channel_df['LinkToUpdate'].str.rstrip(',"')
channel_df = channel_df.assign(Old_Link=None)

file_path = 'TV.m3u'
branch_name = 'main'

# Read the contents of the TV.m3u file
with open(file_path, 'r') as file:
    tv_m3u_content = file.read()

for index, row in channel_df.iterrows():
    channel_name = row['Channel']
    pattern = re.escape(channel_name) + r'\n(https://[^\n]+)'
    match = re.search(pattern, tv_m3u_content)
    if match:
        old_link = match.group(1)
        channel_df.at[index, 'Old_Link'] = old_link

tv_m3u_content_updated = tv_m3u_content

for index, row in channel_df.iterrows():
    channel_name = row['Channel']
    link_to_update = row['LinkToUpdate']
    if link_to_update is not None:  # Add this condition
        pattern = re.escape(channel_name) + r'\n(https://[^\n]+)'
        match = re.search(pattern, tv_m3u_content_updated)
        if match:
            old_link = match.group(1)
            tv_m3u_content_updated = tv_m3u_content_updated.replace(old_link, link_to_update)

file_content_bytes = bytes(tv_m3u_content_updated, 'utf-8')
repo.update_file(file_path, "Auto update TV.m3u", file_content_bytes, file.sha, branch=branch_name)
print(f"File {file_path} successfully updated in the repository.")
