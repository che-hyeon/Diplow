from django.db import models
from status.models import Nation
# Create your models here.

class MovementData(models.Model):
    CATEGORIES = [
        ('health', '보건/환경/기술'),
        ('edu', '교육/역량강화'),
        ('culture', '문화/공공외교'),
        ('system', '제도/행정/포용'),
        ('etc', '기타'),
    ]
    movement_data_id = models.AutoField(primary_key=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='etc')
    title_kr = models.CharField(max_length=30, verbose_name="국가최신동향 제목(국문)")
    title_en = models.CharField(max_length=50, null=True, blank=True, verbose_name="국가최신동향 제목(영문)")
    content_kr = models.TextField(null=True, blank=True, verbose_name="국가최신동향 내용(국문)")
    content_en = models.TextField(null=True, blank=True, verbose_name="국가최신동향 내용(영문)")
    pub_date = models.CharField(max_length=50, null=True, blank=True, verbose_name="국가최신동향 게시일")

    class Meta:
        verbose_name_plural = "[공공데이터] (최신동향 모델) MovementDatas"

class DiplomacyEvent(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_title = models.CharField(max_length=50, verbose_name="행사 제목")
    event_category = models.CharField(max_length=30, verbose_name="행사 분류")
    event_content = models.TextField(verbose_name="행사 내용")
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "(공공외교행사 모델) DiplomacyEvents"

