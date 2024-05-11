#Import python libraries
import os
import base64
import re
import pandas as pd
import requests

# Channel mapping
channel_mapping = {
    '#EXTINF:-1, Nat Geo Wild': 'https://www.seir-sanduk.com/?player=1&id=hd-nat-geo-wild-hd&pass=',
    '#EXTINF:-1, Kitchen 24': 'https://www.seir-sanduk.com/?player=1&id=hd-24-kitchen-hd&pass=',
    '#EXTINF:-1, BNT 1': 'https://www.seir-sanduk.com/?player=1&id=hd-bnt-1-hd&pass=',
    '#EXTINF:-1, BNT 3': 'https://www.seir-sanduk.com/?player=1&id=hd-bnt-3-hd&pass=',
    '#EXTINF:-1, Max Sport 4': 'https://www.seir-sanduk.com/?player=3&id=hd-max-sport-4-hd&pass=',
    '#EXTINF:-1, Max Sport 3': 'https://www.seir-sanduk.com/?player=3&id=hd-max-sport-3-hd&pass=',
    '#EXTINF:-1, Diema Sport 3': 'https://www.seir-sanduk.com/?player=3&id=hd-diema-sport-hd&pass=',
    '#EXTINF:-1, Food Network BG': 'https://www.seir-sanduk.com/?player=1&id=hd-food-network-hd&pass=',
    '#EXTINF:-1, Epic Drama': 'https://www.seir-sanduk.com/?player=1&id=hd-epic-drama-hd&pass=',
    '#EXTINF:-1, Discovery Channel': 'https://www.seir-sanduk.com/?player=1&id=hd-discovery-channel-hd&pass=',
    '#EXTINF:-1, Star Crime': 'https://www.seir-sanduk.com/?player=1&id=hd-star-crime-hd&pass=',
    '#EXTINF:-1,Travel TV': 'https://www.seir-sanduk.com/?player=1&id=hd-travel-channel-hd&pass=',
    '#EXTINF:-1, Nova News': 'https://www.seir-sanduk.com/?player=1&id=hd-nova-news-hd&pass=',
    '#EXTINF:-1, Nova TV': 'https://www.seir-sanduk.com/?player=1&id=hd-nova-tv-hd&pass=',
    '#EXTINF:-1, BTV': 'https://www.seir-sanduk.com/?player=1&id=hd-btv-hd&pass=',
    '#EXTINF:-1, Max Sport 1': 'https://www.seir-sanduk.com/?player=3&id=hd-max-sport-1-hd&pass=',
    '#EXTINF:-1, Max Sport 2': 'https://www.seir-sanduk.com/?player=3&id=hd-max-sport-2-hd&pass=',
    '#EXTINF:-1, Nova Sports': 'https://www.seir-sanduk.com/?player=3&id=hd-nova-sport-hd&pass=',
    '#EXTINF:-1, TLC 1 RU': 'http://rutv.pw/tlc',
    '#EXTINF:-1, Dorama RU': 'http://rutv.pw/dorama',
    '#EXTINF:-1, EDA RU': 'http://rutv.pw/edahd'
    # Add more channels as needed
}

#Creating function to m3u8 sinffer
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

#Use function to sniff channels links in mapping
data_list = []

for channel, source_link in channel_mapping.items():
    fetched_link = update_links(channel, source_link)
    data_list.append({'Channel': channel, 'SourceLink': source_link, 'LinkToUpdate': fetched_link})

channel_df = pd.DataFrame(data_list)

#Since IP block is generating some wrong links, reutilizing valid token
valid_token = None
for link in channel_df.loc[channel_df['LinkToUpdate'].str.startswith('https://mx86.glebul.com/hlsfhd/'), 'LinkToUpdate']:
    match = re.search(r'\.m3u8\?e=(\d+)&hash=([^\&]+)', link)
    if match:
        valid_token = match.group(0)
        break

wrong_links_to_edit = channel_df[channel_df['LinkToUpdate'].str.startswith('https://ro.gledam.xyz/hls/')]
wrong_links_to_edit['FinalLinkToUse'] = wrong_links_to_edit['LinkToUpdate'].apply(lambda x: re.sub(r'^https://ro.gledam.xyz/hls/(.+?)/(.+)$', f'https://cdn1.gledam.xyz/hlsfhd/\\1{valid_token}', x))

updated_channel_df = pd.merge(channel_df, wrong_links_to_edit, on='LinkToUpdate', how='left', suffixes=('', '_y'))
updated_channel_df['LinkToUpdate'] = updated_channel_df.apply(lambda row: row['FinalLinkToUse'] if pd.notnull(row['FinalLinkToUse']) else row['LinkToUpdate'], axis=1)
updated_channel_df.drop(['FinalLinkToUse','Channel_y','SourceLink_y'], axis=1, inplace=True)

#Reading playlist instance
file_path = 'TV.m3u'

with open(file_path, 'r') as file:
    tv_m3u_content = file.read()

tv_m3u_content_updated = tv_m3u_content

#Updating links in file
for index, row in updated_channel_df.iterrows():
    channel_name = row['Channel']
    link_to_update = row['LinkToUpdate']
    if link_to_update is not None:
        pattern = re.escape(channel_name) + r'\n(https://[^\n]+)'
        tv_m3u_content_updated = re.sub(pattern, f"{channel_name}\n{link_to_update}", tv_m3u_content_updated)

# Write the updated content back to the file
with open(file_path, 'w') as file:
    file.write(tv_m3u_content_updated)

print(f"File {file_path} successfully updated.")
