from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import LocalGoverment

@receiver(post_migrate)
def create_default_local_goverment(sender, **kwargs):
    if not LocalGoverment.objects.filter(pk=0).exists():
        LocalGoverment.objects.create(local_id=0, local_name="전체")