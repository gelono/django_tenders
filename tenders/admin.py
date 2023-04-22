from django.contrib import admin

# Register your models here.
from tenders.models import ArchiveTender, Subscriber, SubscriberBalance, TransactionIn

admin.site.register(ArchiveTender)
admin.site.register(Subscriber)
admin.site.register(SubscriberBalance)
admin.site.register(TransactionIn)
