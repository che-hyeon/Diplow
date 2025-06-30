from django.db import models
from django.core.exceptions import ValidationError

def image_upload_path(instance, filename):
    model_name = instance.__class__.__name__  # 예: 'Nation', 'City' 등
    pk = instance.pk if instance.pk else 'temp'  # 저장 전이면 None이므로 대비
    return f'{model_name}/{pk}/{filename}'

# Create your models here.
class Nation(models.Model):
    nation_id = models.AutoField(primary_key=True)
    nation_name = models.CharField(max_length=20, verbose_name="국가 이름")
    nation_info = models.TextField(verbose_name="국가 정보")
    # nation_image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)

    def __str__(self):
        return self.nation_name
    
class LocalGoverment(models.Model):
    local_id = models.AutoField(primary_key=True)
    local_name = models.CharField(max_length=50, verbose_name="지방자치단체 이름")
    # local_image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    
    def __str__(self):
        return self.local_name

class NationDashboard(models.Model):
    nation_dash_id = models.AutoField(primary_key=True)
    nation = models.OneToOneField(Nation, on_delete=models.CASCADE)

    nation_map_explain = models.TextField(verbose_name="교류 현황 설명")
    nation_ratio_explain = models.TextField(verbose_name="분야별 교류 비율 설명")
    nation_ratio_explain_detail = models.TextField(verbose_name="분야별 교류 비율 상세 설명")
    nation_recent_explain = models.TextField(verbose_name="최근 교류 사례 설명")
    nation_num_tend = models.TextField(verbose_name="교류 사업 수 추이 설명")
    # dash_image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)

class LocalDashboard(models.Model):
    local_dash_id = models.AutoField(primary_key=True)
    local = models.OneToOneField(LocalGoverment, on_delete=models.CASCADE)

    local_map_explain = models.TextField(verbose_name="교류 현황 설명")
    local_sister_explain = models.TextField(verbose_name="자매도시 설명")
    local_friendly_explain = models.TextField(verbose_name="우호 결연 도시 설명")
    local_ratio_explain = models.TextField(verbose_name="주요 교류국 순위 설명")
    local_ratio_explain_detail = models.TextField(verbose_name="주요 교류국 순위 상세 설명")
    local_category_explain = models.TextField(verbose_name="주요 교류 분야 설명")
    local_vision_explain = models.TextField(verbose_name="비전 설명")

class ExchangeData(models.Model):
    CATEGORIES = [
        ('health', '보건/환경/기술'), # 보건 환경 기술
        ('edu', '교육/역량강화'),
        ('culture', '문화/공공외교'),
        ('system', '제도/행정/포용'),
        ('etc', '기타')
    ]
    exchange_id = models.AutoField(primary_key=True)
    exchange_name_kr = models.CharField(max_length=100, null=True, blank=True, verbose_name="교류 데이터 국문 이름")
    exchange_name_en = models.CharField(max_length=100, null=True, blank=True, verbose_name="교류 데이터 영문 이름")
    exchange_category = models.CharField(max_length=50, choices=CATEGORIES, default='etc', verbose_name="분야", null=True, blank=True)
    exchange_content = models.TextField(verbose_name="교류 데이터 내용", null=True, blank=True)
    exchange_nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
    start_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="시작 연도")
    end_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="종료 연도")
    others = models.TextField(verbose_name="기타사항")
    pub_date = models.DateField(verbose_name="등록일")

    def __str__(self):
        return f"{self.exchange_nation} - {self.get_exchange_category_display()} - {self.exchange_name_kr}"