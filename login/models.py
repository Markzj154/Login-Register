from django.db import models

# Create your models here.

class User(models.Model):

	gender = (
			('male', '男'),
			('female', '女'),
		)
	name = models.CharField(max_length=128, unique=True)  # 用户名，必填，最长不能超过128个字符，并且用户名不能重复
	password = models.CharField(max_length=256)  # 密码，必填，最长字符不能超过256个字符
	email = models.EmailField(unique=True)  # 邮箱， 使用Django内置的邮箱类型，并且唯一
	sex = models.CharField(max_length=32, choices=gender, default='男')  # 性别，使用了一个choices，只能选择男或者女，默认为男
	c_time = models.DateTimeField(auto_now_add=-True)  # 创建时间
	has_confirmed = models.BooleanField(default=False)  # 邮箱是否注册

	"""
	注意：这里的用户名指的是网络上注册的用户名，不要等同于现实生活中的真实姓名，所以采用了唯一机制。
	如果是现实中的人名，那是可以重复的，肯定不能设置unique的。另外关于密码至少128位长度，因为密码
	通过加密后的长度很长
	"""

	def __str__(self):
		"""
		使用__str__方法帮助人性化显示对象信息
		"""
		return self.name

	class Meta:
		ordering = ['-c_time']  # 排序方式：优先显示最近创建的
		verbose_name = "用户"
		verbose_name_plural = "用户"


class ConfirmString(models.Model):
	code = models.CharField(max_length=256)
	user = models.OneToOneField('User', on_delete=models.CASCADE)
	c_time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name + ":   " + self.code

	class Meta:
	 	ordering = ['-c_time']
	 	verbose_name = '确认码'
	 	verbose_name_plural = '确认码'
