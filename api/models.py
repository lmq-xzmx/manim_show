from django.db import models

# Create your models here.

class SystemPrompt(models.Model):
    """系统提示词配置，用于LLM代码生成时的系统指令"""
    name = models.CharField(max_length=100, verbose_name='配置名称')
    prompt = models.TextField(verbose_name='系统提示词')
    is_active = models.BooleanField(default=False, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '系统提示词配置'
        verbose_name_plural = '系统提示词配置'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """保存时如果设为活跃，则将其他配置设为非活跃"""
        if self.is_active:
            # 将其他所有配置设为非活跃
            SystemPrompt.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active(cls):
        """获取当前活跃的系统提示词配置"""
        return cls.objects.filter(is_active=True).first()
