from django.dispatch import receiver

from  videoflix_app.tasks import convert_480p, convert_720p, convert_1080p
from .models import Video
from django.db.models.signals import post_save, post_delete
import os
import django_rq

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video wurde gespeichert')
    if created:
        print('New video created')
        queue = django_rq.get_queue('default',autocommit=True)
        queue.enqueue(convert_480p, instance.video_file_480p.path)
        print('New video convert_480p')
        queue.enqueue(convert_720p, instance.video_file_720p.path)
        print('New video convert_720p')
        queue.enqueue(convert_1080p, instance.video_file_1080p.path)
        print('New video convert_1080p')


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """Deletes files from filesystem when corresponding 'Video' object is deleted """
    if instance.video_file_480p:
        if os.path.isfile(instance.video_file_480p.path):
            os.remove(instance.video_file_480p.path)
            print('480p video deleted')
    if instance.video_file_720p:
        if os.path.isfile(instance.video_file_720p.path):
            os.remove(instance.video_file_720p.path)
            print('720p video deleted')
    if instance.video_file_1080p:
        if os.path.isfile(instance.video_file_1080p.path):
            os.remove(instance.video_file_1080p.path)
            print('1080p video deleted')