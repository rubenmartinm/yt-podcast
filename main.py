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
    channel_dir = f'/data/{channel_name}'
    files = glob.glob(os.path.join(channel_dir, '*.mp3'))
    files.sort(key=os.path.getmtime, reverse=True)
    if len(files) > total_videos:
        for file in files[total_videos:]:
            os.remove(file)

def generate_podcast_feed(youtube_channels):
    for channel_name, channel_data in youtube_channels.items():
        youtube_channel = channel_data['youtube_channel']
        channel_image = channel_data['image_url']
        total_videos = int(channel_data.get('total_videos', 1))

        feed = feedgen.feed.FeedGenerator()
        feed.id('urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6') # ID único del feed
        feed.title(f'YT-Podcast {channel_name}')
        feed.author({'name': 'Tu Nombre', 'email': 'tu@email.com'})
        feed.link(href='https://10.12.12.34:9999', rel='alternate') # Enlace alternativo al feed
        feed.description(f'Episodios del canal de YouTube {channel_name} convertidos a podcast')
        feed.image(url=f'{channel_image}', title='Channel image', link=f'{channel_image}')

        ydl_opts = {
            'format': 'bestaudio/best',  # Elige el mejor formato de audio disponible
            'playlistend': total_videos,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # Convierte el audio a MP3
                'preferredquality': '192'  # Calidad del audio MP3
            }],
            'outtmpl': f'/data/{channel_name}/%(title)s.mp3',  # Ubicación y nombre del archivo descargado
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(youtube_channel, download=False)
                videos = info_dict['entries']
                for video in videos[:total_videos]:
                    video_url = video['url']
                    title = video['title']
                    upload_date = datetime.strptime(video['upload_date'], '%Y%m%d')
                    pub_date = upload_date.astimezone(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
                    # Normalizar y reemplazar caracteres especiales en español
                    title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')
                    # Formatear el título para una URL válida
                    title = re.sub(r'\W+', '-', title)  # Reemplaza caracteres no alfanuméricos con guiones
                    title = quote_plus(title)

                    # Construir la URL pública del archivo de audio
                    audio_url = f'http://10.12.12.34:9999/{channel_name}/{title}.mp3'

                    # Agregar el episodio al feed
                    fe = feed.add_entry()
                    fe.id(video_url)
                    fe.title(title)
                    fe.link(href=video_url)
                    fe.description(title)
                    fe.enclosure(url=audio_url, length='123456', type='audio/mpeg')
                    pub_date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')  # Formato de fecha requerido
                    fe.pubDate(pub_date)

            except yt_dlp.DownloadError as e:
                print(f'Error al descargar el video: {e}')
                continue

        # Guardar el feed en un archivo
        feed_file = f'/data/{channel_name}_feed.xml'
        feed.rss_file(feed_file)

        print(f'Feed RSS generado en {feed_file}')

        # Limpiar episodios antiguos
        cleanup_old_episodes(channel_name, total_videos)

if __name__ == '__main__':
    config_file = '/data/yt_channels.yaml'
    with open(config_file, 'r') as f:
        youtube_channels = yaml.safe_load(f)

    generate_podcast_feed(youtube_channels['podcasts'])
