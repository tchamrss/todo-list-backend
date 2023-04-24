import subprocess
    
def convert_480p(source):
    source_without_extension = source[:-4]
    target = source_without_extension + '_480p.mp4'
    ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
    cmd = '{} -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(ffmpeg_path, source, target)
    subprocess.run(cmd, shell=True)
    
def convert_720p(source):
    source_without_extension = source[:-4]
    target = source_without_extension + '_720p.mp4'
    ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
    cmd = '{} -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(ffmpeg_path, source, target)
    subprocess.run(cmd, shell=True)

def convert_1080p(source):
    source_without_extension = source[:-4]
    target = source_without_extension + '_1080p.mp4'
    ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
    cmd = '{} -i "{}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(ffmpeg_path, source, target)
    subprocess.run(cmd, shell=True)