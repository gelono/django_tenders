from django.db.models.signals import post_save
from django.dispatch import receiver

from tenders.models import ActiveTender
from tenders.tasks import user_notification


@receiver(post_save, sender=ActiveTender)
def on_tender_save(sender, instance: ActiveTender, created, **kwargs):
    if created:
        message = 'Здравствуйте! Уведомляем Вас о появившемся новом тендере в интересующем Вас разделе: '
        link = instance.link
        obj_id = instance.id
        user_notification.apply_async(args=[obj_id, link, message], countdown=1)
