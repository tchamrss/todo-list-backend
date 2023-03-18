import subprocess

""" def convert_480p(source):
    target = source + '_480p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, target)
    subprocess.run(cmd) """
    
def convert_480p(source):
    source_without_extension = source[:-4]
    target = source_without_extension + '_480p.mp4'
    ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
    cmd = '{} -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(ffmpeg_path, source, target)
    subprocess.run(cmd, shell=True)