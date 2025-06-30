from django.db import models
from status.models import LocalGoverment

# Create your models here.

class Opinion(models.Model):
    opinion_id = models.AutoField(primary_key=True)
    local = models.ForeignKey(LocalGoverment, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="의견 제목")
    content = models.TextField(verbose_name="의견 내용")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.opinion_id} : {self.local} - {self.title}"
    
class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    local = models.ForeignKey(LocalGoverment, on_delete=models.CASCADE)
    program_name = models.CharField(max_length=50, verbose_name="행사명")
    program_content = models.TextField(verbose_name="행사 내용")
    url = models.URLField(verbose_name="URL 링크", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.program_id} : {self.local} - {self.program_name}"