# 测试发送邮件的py文件

import os
from django.core.mail import EmailMultiAlternatives


# 因为我是当前是单独运行send_mail文件，无法自动链接django环境，需要通过os模块对环境变量进行设置
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'


if __name__ == '__main__':
	subject, from_email, to = '来自markzj的邮件测试', '987048466@qq.com', '15181127831@163.com'
	text_context = '欢迎访问markzjlove.cn，这里是markzj的博客，专注于python和django的技术分享'
	html_context = '<p>欢迎访问<a href="http://markzjlove.cn" target=blank>markzjlove.cn</a>这里是markzj的博客，专注于python和django的技术分享</p>'
	msg = EmailMultiAlternatives(subject, text_context, from_email, [to])
	msg.attach_alternative(html_context, 'text/html')
	msg.send()