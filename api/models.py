from django.db import models
from django.utils import timezone

# Create your models here.

class SystemPrompt(models.Model):
    """系统提示词模型，用于存储大模型生成动画代码时使用的系统提示词"""
    
    # 物理领域分类选项
    CATEGORY_CHOICES = [
        ('general', '通用提示词'),
        ('mechanics', '力学'),
        ('electromagnetism', '电磁学'),
        ('thermodynamics', '热力学'),
        ('fluid', '流体力学'),
        ('quantum', '量子物理'),
        ('relativity', '相对论'),
        ('optics', '光学'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='提示词名称')
    prompt = models.TextField(verbose_name='提示词内容')
    category = models.CharField(
        max_length=30, 
        choices=CATEGORY_CHOICES, 
        default='general',
        verbose_name='物理领域分类'
    )
    is_active = models.BooleanField(default=False, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '系统提示词'
        verbose_name_plural = '系统提示词'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({'激活' if self.is_active else '未激活'})"
    
    def save(self, *args, **kwargs):
        """重写保存方法，确保只有一个提示词处于激活状态"""
        if self.is_active:
            # 如果当前提示词被激活，将其他提示词设为未激活
            SystemPrompt.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active(cls):
        """获取当前活跃的系统提示词"""
        try:
            return cls.objects.filter(is_active=True).first()
        except cls.DoesNotExist:
            return None
            
    @classmethod
    def get_by_category(cls, category):
        """获取特定类别的所有提示词"""
        return cls.objects.filter(category=category)
