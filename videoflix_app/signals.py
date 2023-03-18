from django.dispatch import receiver

from  videoflix_app.tasks import convert_480p
from .models import Video
from django.db.models.signals import post_save, post_delete
import os
import django_rq

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video wurde pespeichert')
    if created:
        print('New video created')
        queue = django_rq.get_queue('default',autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path)
        #convert_480p(instance.video_file.path)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """Deletes files from filesystem when corresponding 'Video' object is deleted """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
            print('New video deleted')