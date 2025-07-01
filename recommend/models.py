from django.db import models
from status.models import Nation

# Create your models here.
class EnvironIssueData(models.Model):
    environ_data_id = models.AutoField(primary_key=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
    environ_data_title = models.CharField(max_length=50, verbose_name="환경데이터 제목")
    pub_date = models.DateField(null=True, blank=True, verbose_name="등록일")

    class Meta:
        verbose_name_plural = "[공공데이터] (환경이슈관련 모델) EnvironIssueDatas"