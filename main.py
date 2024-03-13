import feedgen.feed
import os
import subprocess
import sys
import json

def generate_podcast_feed(youtube_urls):
    feed = feedgen.feed.FeedGenerator()
    feed.id('urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6') # ID único del feed
    feed.title('Mi Podcast de YouTube')
    feed.author({'name': 'Tu Nombre', 'email': 'tu@email.com'})
    feed.link(href='https://tu-sitio-web.com', rel='alternate') # Enlace alternativo al feed
    feed.description('Episodios de mi canal de YouTube convertidos a podcast')

    for youtube_url in youtube_urls:
        # Obtener la lista de los dos últimos videos del canal de YouTube
        youtube_dl_command = f'yt-dlp -j --flat-playlist {youtube_url}'
        try:
            output = subprocess.check_output(youtube_dl_command, shell=True, text=True)
            videos = output.strip().split('\n')
            for video in videos[:1]:
                video_info = json.loads(video)
                video_url = video_info['url']
                title = video_info['title']
                channel_name = "Soy Motor"
                # Crear el directorio del canal si no existe
                channel_dir = f'/data/{channel_name}'
                os.makedirs(channel_dir, exist_ok=True)
                audio_file = f'/data/{channel_name}/{title}.mp3'

                # Descargar el audio del video
                download_command = f'yt-dlp -x --audio-format mp3 --audio-quality 128K -o "{audio_file}" {video_url}'
                os.system(download_command)

                audio_url = f'https://10.12.12.34:9999/{channel_name}/{title}.mp3'

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
    config_file = '/data/youtube_channels.xml'
    with open(config_file, 'r') as f:
        youtube_urls = [line.strip() for line in f.readlines() if line.strip()]
    
    generate_podcast_feed(youtube_urls)

