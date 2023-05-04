from django.db.models.signals import post_save
from django.dispatch import receiver

from tenders.models import ActiveTender
from tenders.tasks import user_notification


@receiver(post_save, sender=ActiveTender)
def on_order_save_in_thread(sender, instance: ActiveTender, created, **kwargs):
    if created:
        # print('receiver triggered')
        message = 'Здравствуйте! Уведомляем Вас о появившемся новом тендере в интересующем Вас разделе: '
        link = instance.link
        obj_id = instance.id
        user_notification.apply_async(args=[obj_id, link, message], countdown=1)
    # else:
    #     message = 'Здравствуйте! Уведомляем Вас о внесении изменений в тендер в интересующем Вас разделе: '
    #     link = instance.link
    #     dk_numbers = [dk.dk_number for dk in instance.dk_numbers.all()]
    #     user_notification(dk_numbers, link, message)
