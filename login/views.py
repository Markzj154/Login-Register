from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import User, ConfirmString
from .forms import UserForm, RegisterForm
import datetime
import hashlib

# Create your views here.

def index(request):
	if request.session.get('is_login', None):
		return redirect('/login/')
	return render(request, 'login/index.html')


def login(request):
	if request.session.get('is_login', None):  # 不允许重复登录
		return redirect('/index/')
	if request.method == 'POST':
		login_form = UserForm(request.POST)
		message = '用户名或密码错误!'
		if login_form.is_valid():
			username = login_form.cleaned_data.get('username')
			password = login_form.cleaned_data.get('password')
			try:
				user = User.objects.get(name=username)
			except:
				return render(request, 'login/login.html', locals())
			if not user.has_confirmed:
				message = '该用户还未经过邮件确认！'
				return render(request, 'login/login.html', locals())
			if user.password == hash_code(password):
				# 网session字典中写入用户状态和数据
				request.session['is_loign'] = True
				request.session['user_id'] = user.id
				request.session['user_name'] = user.name
				return redirect('/index/')
			else:
				return render(request, 'login/login.html', locals())
		else:
			return render(request, 'login/login.html', locals())

	login_form = UserForm()
	return render(request, 'login/login.html', locals())


def register(request):
	if request.session.get('is_lign', None):
		return redirect('/index/')
	if request.method == 'POST':
		register_form = RegisterForm(request.POST)
		message = '请输入符合规范的信息'
		if register_form.is_valid():
			username = register_form.cleaned_data.get('username')
			password1 = register_form.cleaned_data.get('password1')
			password2 = register_form.cleaned_data.get('password2')
			email = register_form.cleaned_data.get('email')
			sex = register_form.cleaned_data.get('sex')
			if password1 != password2:
				message = '两次密码不一致'
				return render(request, 'login/register.html', locals())
			else:
				same_name_user = User.objects.filter(name=username)
				if same_name_user:
					message = '用户名已存在'
					return render(request, 'login/register.html', locals())
				same_email_user = User.objects.filter(email=email)
				if same_email_user:
					message = '该邮箱已被注册'
					return render(request, 'login/register.html', locals())
				new_user = User()
				new_user.name = username
				new_user.password = hash_code(password2)
				new_user.email = email
				new_user.sex = sex
				new_user.save()

				code = make_confirm_string(new_user)
				send_email(email, code)

				message = '请前往邮箱进行确认！'
				return render(request, 'login/confirm.html', locals())
		else:
			return render(request, 'login/register.html', locals())
	register_form = RegisterForm()
	return render(request, 'login/register.html', locals())


def logout(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	request.session.flush()
	# 或者使用下面的方法
	# del request.session['is_login']
	# del request.session['user_id']
	# del request.session['user_name']
	# flush()是比较好的一种做法，而且一次性将session中的所有内容全部清空，确保不留后患。
	return redirect('/login/')


def user_confirm(request):
	code = request.GET.get('code', None)  # 从请求的url地址中获取确认码
	message = ''
	try:
		confirm = ConfirmString.objects.get(code=code)
	except:
		message = '无效的确认请求！'
		return render(request, 'login/confirm.html', locals())
	c_time = confirm.c_time
	now = datetime.datetime.now()
	if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
		confirm.user.delete()
		message = '你的邮件已经过期，请重新注册！'
		return render(request, 'login/confirm.html', locals())
	else:
		confirm.user.has_confirmed = True
		confirm.user.save()
		confirm.delete()
		message = '感谢确认，请使用账号登录！'
		return render(request, '.login/confirm.html', locals())


def hash_code(s, salt='mysite'):
	h = hashlib.sha256()
	s += salt
	h.update(s.encode())
	return h.hexdigest()


def make_confirm_string(user):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	code = hash_code(user.name, now)
	ConfirmString.objects.create(code=code, user=user,)
	return code


def send_email(email, code):
	subject = '来自markzjlove.cn的注册邮件'
	text_content = '''感谢注册markzjlove.cn，这里是markzj博客地址，专注于python、django学习技术分享！如果你看到这条消息，\
					  说明你的邮箱服务器不提供和HTML链接功能，请联系管理员！'''
	html_content = '''<p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>markzjlove.cn</a>, 这里是markzj的博客站点\
					  专注于python、django学习技术分享！</p>
					  <p>请点击站点链接完成注册确认！</p>
					  <p>此链接有效期为{}天！</p>
					  '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
	msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
	msg.attach_alternative(html_content, 'text/html')
	msg.send()

