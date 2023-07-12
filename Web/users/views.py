from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.db.models.query_utils import Q

from django.http import HttpResponse, FileResponse, JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required

from reply.forms import ReplyForm
from reply.models import Reply

from .models import User, Post, Video
from .forms import PostForm, VideoForm

from .tokens import account_activation_token

from datetime import timedelta
import datetime

import os
import sys
import asyncio
from threading import Thread
import time
from django.contrib.auth.hashers import make_password
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

# 07-02
import json
from asgiref.sync import async_to_sync 
from .consumers import CaptionProcessingConsumer
from channels.layers import get_channel_layer


from ai.barrier_free_caption_gen import *
print()
bfcg = BarrierFreeCaptionGenerator()
def upload_view(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            video = Video(file=file)
            video.save()
            
            input_filepath = video.get_file_path()
            output_filepath = input_filepath.split("/")
            output_filepath[-2] = "subtitle"
            output_filepath[-1] = output_filepath[-1][:-3] + "vtt"
            output_filepath = "/".join(output_filepath)
            caption = bfcg.make_caption_from_file(input_filepath, language="en")
            
            with open(output_filepath, mode="w", encoding="utf-8") as text_file:
                text_file.write(caption)
            
            # messages.success(request, 'File uploaded successfully.')
            # return render(request, 'sub_test.html', {'form':form, 'video':video})
        else:
            messages.error(request, 'Invalid form data. Please try again.')
    else:
        form = VideoForm()  
    return render(request, 'sub_test.html', {'form':form})
# Create your views here.

def index_view(request):
    return render(request, 'index.html')


def signup_view(request):
    if request.method == "POST":
        print(request.POST)
        email = request.POST["email"]
        password = request.POST["password"]
        nickname = request.POST["nickname"]
        if User.objects.filter(username=email).exists():
            return HttpResponse("이미 사용 중인 이메일 입니다")
        user = User.objects.create_user(username=email, email=email, password=password, nickname=nickname)
        user.is_active = False
        user.save()
        current_site = get_current_site(request)
        message = render_to_string('activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        mail_title = "가입 확인 이메일"
        mail_to = request.POST["email"]
        email = EmailMessage(mail_title, message, to=[mail_to])
        email.send()
    return redirect("user:index")

def activate(request, uidb64, token):
    message = None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
    return redirect("user:index")
    # else:
    #     return render(request, 'index.html', {'error': '계정 활성화 오류'})

def login_view(request):
    message = None
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(username=email, password=password)
        if user is not None:
            print("Success!!")
            login(request, user)
        else:
            if User.objects.filter(username=email).exists():
                message = "작성한 이메일로 가입 확인 이메일을 보냈습니다. 이메일을 확인하여 계정을 활성화해주세요."
            else:
                message = "회원 가입이 필요합니다 회원 가입을 해주세요!"
    return render(request, 'index.html', {'message': message})
     

@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect("user:index")

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = get_user_model().objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = '비밀번호 재설정'
					email_template_name = "password_reset_email.txt"
					c = {
						"email": user.email,
						# local: '127.0.0.1:8000', prod: 'givwang.herokuapp.com'
						# 'domain': settings.HOSTNAME,
						# 'site_name': 'givwang',
                        'domain': '127.0.0.1:8000',
						'site_name': '127.0.0.1:8000',
						# MTE4
						"uid": urlsafe_base64_encode(force_bytes(user.pk)),
						"user": user,
						# Return a token that can be used once to do a password reset for the given user.
						'token': default_token_generator.make_token(user),
						# local: http, prod: https
						# 'protocol': settings.PROTOCOL,
                        'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, '8370kjw@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(
		request=request,
		template_name='password_reset.html',
		context={'password_reset_form': password_reset_form}
    )

@login_required(login_url='/')
def withdraw(request):
    user = request.user
    user.delete()
    logout(request)
    return redirect('user:index')

@login_required(login_url='/')
def mypage_view(request, id):
    my = User.objects.get(id=id)
    if str(request.user) == str(my.username):
        print("Success!!")
        return render(request, 'mypage.html', {'my':my})
    else:
        print("Fail!!")
        return redirect('user:index')
    
@login_required(login_url='/')
def mypage_update(request, id):
    my = User.objects.get(id=id)
    if request.method == "POST":        
        if str(request.user) == str(my.username):
            print("All", request)
            my.nickname = request.POST.get('nickname')
            my.save()
            return redirect('user:mypage', id)
        else:
            print("Fail!!")
            return redirect('user:index')
    else:
        return render(request, 'mypage.html', {'my':my})

@login_required(login_url='/')
def new_password(request, id):
    my = User.objects.get(id=id)
    if request.method == "POST":        
        if str(request.user) == str(my.username):
            new_password = request.POST.get('new_password')
            hashed_password = make_password(new_password)
            my.password = hashed_password
            my.save()
            return redirect('user:mypage', id)
        else:
            print("Fail!!")
            return redirect('user:index')
    else:
        return render(request, 'mypage.html', {'my':my})
        

@login_required(login_url='user:index')
def blog_view(request):
    postlist = Post.objects.all()
    paginator = Paginator(postlist, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('user:blog')
    else:
        form = PostForm()
    return render(request, 'blog.html', {'posts':posts, 'form': form})

@login_required(login_url='/')
def blogdt_view(request, post_id):
    post = Post.objects.prefetch_related('reply_set').get(id=post_id)
    replyForm = ReplyForm()
    response = render(request, 'blog-details.html', {'post':post, 'replyForm':replyForm})
    
    expire_date, now = datetime.datetime.now(), datetime.datetime.now()
    expire_date += timedelta(days=1)
    expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
    expire_date -= now
    max_age = expire_date.total_seconds()
    
    cookie_value = request.COOKIES.get('hitblog', '_')

    if f'_{post_id}_' not in cookie_value:
        cookie_value += f'{post_id}_'
        response.set_cookie('hitblog', value=cookie_value, max_age=max_age, httponly=True)
        post.view_count += 1
        post.save()
    return response

@login_required(login_url='/') 
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author_id = request.user.id  # Set the author ID
            post.save()
            return redirect('user:blog')
    else:
        form = PostForm(user=request.user)
    return render(request, 'create.html', {'form': form})

@login_required(login_url='/')
def delete(request, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    return redirect('user:blog')

@login_required(login_url='/')
def edit(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        postForm = PostForm(request.POST, request.FILES, instance=post)
        if postForm.is_valid():
            postForm.save()
            return redirect('user:blogdt', post_id)
    else:
        postForm = PostForm(instance=post, initial={
            'title': post.title,
            'content': post.content,
            'file': post.file,
        })
        postForm.fields['file'].required = False
    return render(request, 'change_create.html', {'form':postForm, 'post':post})

def download_file(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    file_path = post.file.path
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

@login_required(login_url='/')
def delete_comment(request, post_id, com_id):
    my_com = Reply.objects.get(id=com_id)
    my_com.delete()
    return redirect('/blog/'+str(post_id))

@login_required(login_url='/')
def edit_comment(request, post_id, com_id):
    post = Post.objects.prefetch_related('reply_set').get(id=post_id)
    comment = get_object_or_404(Reply, id=com_id)
    if request.method == "POST":
        replyForm = ReplyForm(request.POST, instance=comment)
        if replyForm.is_valid():
            comment = replyForm.save()
            return redirect('user:blogdt', post_id)
    else:
        replyForm = ReplyForm(instance=comment)
    return render(request, 'comment_edit.html', {'post':post, 'comment':comment})
    
    
@login_required(login_url='/')    
def my_post(request):
    user_id = request.user.id
    my_posts = Post.objects.filter(author=user_id)
    return render(request, 'my_blogpost.html', {'my_posts':my_posts})
    