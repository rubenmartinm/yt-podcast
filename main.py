import feedgen.feed
import yt_dlp
import os
import glob
import yaml
import re
from urllib.parse import quote_plus
import unicodedata
from datetime import datetime, timezone

def cleanup_old_episodes(channel_name, total_videos):
    channel_dir = f'/podcasts/{channel_name}'
    files = glob.glob(os.path.join(channel_dir, '*.mp3'))
    files.sort(key=os.path.getmtime, reverse=True)
    print(files)
    if len(files) > total_videos:
        print(f'({channel_name}) hay mas files que {total_videos}')
        for file in files[total_videos:]:
            os.remove(file)

def shorter_than_59_minutes(info, *, incomplete):
    """Download only videos shorter than 59 minute (or with unknown duration)"""
    duration = info.get('duration')
    if duration and duration > 3540:
        return 'The video is too long'

def generate_podcast_feed(youtube_channels):
    my_webserver_ip = os.environ.get('MY_WEBSERVER_IP')
    my_webserver_port = os.environ.get('MY_WEBSERVER_PORT')

    for channel_name, channel_data in youtube_channels.items():
        youtube_channel = channel_data['youtube_channel']
        channel_image = channel_data['image_url']
        total_videos = int(channel_data.get('total_videos', 1))

        feed = feedgen.feed.FeedGenerator()
        feed.id('urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6') # uniq ID for the feed
        feed.title(f'YT-Podcast {channel_name}')
        feed.author({'name': 'YOUR NAME', 'email': 'your@email.com'})
        feed.link(href=f'http://{my_webserver_ip}:{my_webserver_port}', rel='alternate')
        feed.description(f'YT {channel_name} videos converted into a podcast')
        feed.image(url=f'{channel_image}', title='Channel image', link=f'{channel_image}')

        channel_dir = f'/podcasts/{channel_name}'
        os.makedirs(channel_dir, exist_ok=True)

        ydl_opts = {
            'format': 'mp3/bestaudio/best', 
            'playlistend': total_videos,
            'match_filter': shorter_than_59_minutes,
            'outtmpl': f'/podcasts/{channel_name}/%(id)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(youtube_channel)
                videos = info_dict['entries']
                for video in videos[:total_videos]:
                    id = video['id']
                    video_url = video['webpage_url']
                    title = video['title']
                    upload_date = datetime.strptime(video['upload_date'], '%Y%m%d')
                    pub_date = upload_date.astimezone(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
                    audio_url = f'http://{my_webserver_ip}:{my_webserver_port}/{channel_name}/{id}.mp3'
                    fe = feed.add_entry()
                    fe.id(id)
                    fe.title(title)
                    fe.link(href=video_url)
                    fe.description(title)
                    fe.enclosure(url=audio_url, length='123456', type='audio/mpeg')
                    fe.pubDate(pub_date)

            except yt_dlp.DownloadError as e:
                print(f'Error downloading video: {e}')
                continue

        feed_file = f'/podcasts/{channel_name}_feed.xml'
        feed.rss_file(feed_file)

        print(f'This is your generated RSS feed: http://{my_webserver_ip}:{my_webserver_port}/{channel_name}_feed.xml')

        cleanup_old_episodes(channel_name, total_videos)

if __name__ == '__main__':
    config_file = '/config/yt_channels.yaml'
    with open(config_file, 'r') as f:
        youtube_channels = yaml.safe_load(f)

    generate_podcast_feed(youtube_channels['podcasts'])
