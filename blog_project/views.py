import datetime
from django.shortcuts import render,redirect
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from read_statistics.utils import get_seven_days_read_data,get_today_hot_data,get_yesterday_hot_data
from blog.models import Blog
from django.utils import timezone
from django.db.models import Sum
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import LoginForm,RegForm
def get_7_days_hot_days():
    today=timezone.now().date()
    data=today-datetime.timedelta(days=7)
    read_details = Blog.objects\
        .filter(read_details__date__lt=today,read_details__date__gte=data)\
        .values('id','title')\
        .annotate(read_num_sum=Sum('read_details__read_num'))\
        .order_by('-read_num_sum')
    return read_details[:7]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    #获取七天热门博客的缓存数据
    week_hot_data=cache.get('week_hot_data')
    if week_hot_data is None:
        week_hot_data=get_7_days_hot_days()
        cache.set('week_hot_data', week_hot_data , 3600)

    context = {}
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['week_hot_data'] = week_hot_data
    context['dates'] = dates
    context['read_nums'] = read_nums
    return render(request,'home.html', context)

def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
                user = login_form.cleaned_data['user']
                auth.login(request,user)
                return redirect(request.GET.get('from',reverse('home')))
    else:
        login_form=LoginForm()
    context ={}
    context['login_form']=login_form
    return render(request,'login.html',context)

def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username=reg_form.cleaned_data['username']
            email=reg_form.cleaned_data['email']
            password=reg_form.cleaned_data['password']
            user=User.objects.create_user(username,email,password)
            user.save()

            user=auth.authenticate(username=username,password=password)
            auth.login(request,user)
            return redirect(request.GET.get('from',reverse('home')))
    else:
        reg_form=RegForm()
    context ={}
    context['reg_form']=reg_form
    return render(request,'register.html',context)


