import feedgen.feed
import os
import subprocess
import sys
import yaml
import re
from urllib.parse import quote_plus

def generate_podcast_feed(youtube_channels):
    feed = feedgen.feed.FeedGenerator()
    feed.id('urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6') # ID único del feed
    feed.title('Mi Podcast de YouTube')
    feed.author({'name': 'Tu Nombre', 'email': 'tu@email.com'})
    feed.link(href='https://tu-sitio-web.com', rel='alternate') # Enlace alternativo al feed
    feed.description('Episodios de mi canal de YouTube convertidos a podcast')

    for channel_name, channel_data in youtube_channels.items():
        youtube_channel = channel_data['youtube_channel']
        total_videos = int(channel_data.get('total_videos', 1))

        # Obtener la lista de videos del canal de YouTube
        youtube_dl_command = f'yt-dlp -j --flat-playlist {youtube_channel}'
        try:
            output = subprocess.check_output(youtube_dl_command, shell=True, text=True)
            videos = output.strip().split('\n')
            for video in videos[:total_videos]:
                video_info = yaml.safe_load(video)
                video_url = video_info['url']
                title = video_info['title']
                # Formatear el título para una URL válida
                # Reemplazar la ñ con una n simple
                title = title.replace("ñ", "n")
                title = re.sub(r'\W+', '-', title)  # Reemplaza caracteres no alfanuméricos con guiones
                title = quote_plus(title)

                # Crear el directorio del canal si no existe
                channel_dir = f'/data/{channel_name}'
                os.makedirs(channel_dir, exist_ok=True)

                # Construir la URL pública del archivo de audio
                audio_url = f'http://10.12.12.34:9999/{channel_name}/{title}.mp3'
                audio_file = f'/data/{channel_name}/{title}.mp3'

                # Descargar el audio del video
                download_command = f'yt-dlp -x --audio-format mp3 --audio-quality 128K -o "{audio_file}" {video_url}'
                os.system(download_command)

                # Agregar el episodio al feed
                fe = feed.add_entry()
                fe.id(video_url)
                fe.title(title)
                fe.link(href=video_url)
                fe.description(title)
                fe.enclosure(url=audio_url, length='123456', type='audio/mpeg')

        except subprocess.CalledProcessError as e:
            print(f'Error al ejecutar yt-dlp: {e}')
            sys.exit(1)

    # Guardar el feed en un archivo
    feed_file = '/data/podcast_feed.xml'
    feed.rss_file(feed_file)

    print(f'Feed RSS generado en {feed_file}')

if __name__ == '__main__':
    config_file = '/data/yt_channels.yaml'
    with open(config_file, 'r') as f:
        youtube_channels = yaml.safe_load(f)
    
    generate_podcast_feed(youtube_channels['podcasts'])
