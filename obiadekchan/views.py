from django.contrib.auth import authenticate
#from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from pathlib import Path
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import messages 
from .models import Banned, Misc, Post
from .forms import addPostForm
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from .utils import checkBan, bumpThread, incrementPostCount
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.http import JsonResponse



# Create your views here.

banned_ips = []



class IndexView(View):
    template_name = 'obiadekchan/index.html'
    q2 = Post.objects.filter(is_thread=True).order_by('-id')
    for q in q2:
        num = len(q.replies.all())
        q.answers = list(q.replies.all())[-3:]
        if num > 3:
            q.hidden = num - 3
    def get(self, request, *args, **kwargs):
        q2 = Post.objects.all().filter(is_thread=True).order_by('-thread_pos')
        for q in q2:
            num = len(q.replies.all())
            q.answers = list(q.replies.all())[-3:]
            if num > 3:
                q.hidden = num - 3
        #q2 = Thread.objects.all().prefetch_related('thread_ans').order_by('-thread_pos')
        paginator = Paginator(q2, 10)
        page = request.GET.get('page')
        q3 = paginator.get_page(page)
        context = {'q2': q3, 'form': addPostForm()}
        return render(request, 'obiadekchan/index.html', context)

    def post(self, request, *args, **kwargs):
        form = addPostForm(request.POST, request.FILES)
        if request.method == 'POST':
            if 'post_thread' in request.POST:
                t_c_object = Misc.objects.first()
                if t_c_object is None:
                    t_c_object = Misc.objects.create(thread_count=0)
                if form.is_valid():
                    from django.db.models import Max, Min
                    from ipware import get_client_ip
                    result = Post.objects.all().aggregate(Max('thread_pos'))
                    xpkej = form.save(commit=False)
                    xpkej.thread_pos = bumpThread(result)
                    ip_address = get_client_ip(request)
                    xpkej.ip_address = ip_address
                    if checkBan(ip_address):
                        return HttpResponseRedirect(reverse('obiadekchan:banned'))
                    thread_count = t_c_object.thread_count
                    t_c_object.thread_count = thread_count + 1
                    if t_c_object.thread_count > 50:
                        det = Post.objects.all().filter(is_thread=True).order_by('-thread_pos').first()
                        det.delete()
                        t_c_object.thread_count = t_c_object.thread_count - 1
                    xpkej.is_thread = True
                    xpkej.count = xpkej.id
                    if 'is_mode' in request.POST:
                        xpkej.is_mode = True
                    xpkej.password = request.POST.get('password')
                    t_c_object.save()
                    xpkej.save()
                    mail = request.POST.get('op_email')
                    if mail.lower() == 'noko':
                        return HttpResponseRedirect(reverse('obiadekchan:index'))                    
                    return redirect('obiadekchan:thread',pk=xpkej.id)
                else:
                    q2 = self.q2
                    return render(request, self.template_name, {'form':form, 'q2': q2})
            elif 'delete_posts' in request.POST:
                del_posts = request.POST.getlist('rep_choice')
                for i in del_posts:
                    post = Post.objects.get(pk=i)
                    pwd = request.POST.get('password')
                    if post.password == pwd:
                        post.delete()
                return HttpResponseRedirect(reverse('obiadekchan:index'))
            elif 'report_post' in request.POST:
                rep_posts = request.POST.getlist('rep_choice')
                #post = Post.objects.get(pk=request.POST['rep_choice'])
                for i in rep_posts:
                    post = Post.objects.get(pk=i)
                    post.rep = False
                    post.rep_res = request.POST.get('r_reason')
                    post.save()
                return HttpResponseRedirect(reverse('obiadekchan:index'))
            
            
class ThreadDetail(generic.DetailView):
    model = Post
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = addPostForm()
        q2 = Post.objects.filter(is_thread=True).order_by('-thread_pos')
        for q in q2:
            q.answers = list(q.replies.all())
        return context

class ThreadPost(TemplateView):
    template_name = 'obiadekchan/thread.html'
    model = Post


    def get_object(self, *args, **kwargs):
        thread = get_object_or_404(Post, pk=self.kwargs['pk'])
        return thread

    def post(self, request, *args, **kwargs):
        form = addPostForm(request.POST, request.FILES)
        if 'post_reply' in request.POST:
            if form.is_valid():
                t_form = form.save(commit=False)
                thread = get_object_or_404(Post, pk=self.kwargs['pk'])
                #t_form.Thread = thread
                from django.db.models import Max
                from ipware import get_client_ip
                ip_address = get_client_ip(request)
                t_form.ip_address = ip_address
                if checkBan(ip_address):
                    return HttpResponseRedirect(reverse('obiadekchan:banned'))
                result = Post.objects.all().filter(is_thread=True).aggregate(Max('thread_pos'))
                mail = request.POST.get('op_email').lower()
                if mail == 'sage':
                    thread.thread_pos = thread.thread_pos
                else:
                    thread.thread_pos = bumpThread(result)
                #t_c_object = Misc.objects.first()
                #t_form.count = len(thread.replies.all())+1
                t_form.is_thread = False
                t_form.date = timezone.now()
                if 'is_mode' in request.POST:
                    t_form.is_mode = True
                t_form.password = request.POST.get('password')
                if 'is_op' in request.POST and thread.password == t_form.password:
                    t_form.is_op = True
                t_form.save()
                thread.replies.add(t_form)
                thread.save()
                if mail.lower() == 'noko':
                    return HttpResponseRedirect(reverse('obiadekchan:index')) 
                return redirect('obiadekchan:thread', pk=self.kwargs['pk'])             
        elif 'report_post' in request.POST:
            rep_posts = request.POST.getlist('rep_choice')
            #post = Post.objects.get(pk=request.POST['rep_choice'])
            for i in rep_posts:
                post = Post.objects.get(pk=i)
                post.rep = False
                post.rep_res = request.POST.get('r_reason')
                post.save()
            return HttpResponseRedirect(reverse('obiadekchan:index'))
        elif 'delete_posts' in request.POST:
            del_posts = request.POST.getlist('rep_choice')
            for i in del_posts:
                post = Post.objects.get(pk=i)
                pwd = request.POST.get('password')
                if post.password == pwd:
                    post.delete()
            return HttpResponseRedirect(reverse('obiadekchan:index'))


class ThreadView(View):

    def get(self, request, *args, **kwargs):
        view = ThreadDetail.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ThreadPost.as_view()
        return view(request, *args, **kwargs)


class ModeratorView(View):

    #login_url = 'obiadekchan/login'
    #redirect_field_name = 'redirect_to'
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        template_name = 'obiadekchan/mode.html'
        context = {'posts': Post.objects.all().filter(rep=False),
                   'banned': Banned.objects.all()}
        return render(request, template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            from ipware import get_client_ip
            if 'del_post' in request.POST:
                post = Post.objects.get(pk=request.POST['del_post'])
                post.delete()
                t_c_object = Misc.objects.first()
                t_c_object.thread_count = t_c_object.thread_count - 1
                t_c_object.save()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'ban_ip' in request.POST:
                post = Post.objects.get(pk=request.POST['ban_ip'])
                ip_address = post.ip_address
                b_reason = request.POST.get('b_reason')
                b_length = request.POST.get('b_length')
                content = post.post_body
                ban = Banned.objects.create(ip_ad=ip_address, reason=b_reason, length=b_length, post_content=content)
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'unban' in request.POST:
                ban = Banned.objects.get(pk=request.POST['unban'])
                ban.delete()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'del_report' in request.POST:
                post = Post.objects.get(pk=request.POST['del_report'])
                post.rep = True
                post.rep_reason = None
                post.save()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))

@login_required
def history(request):
    template_name = 'obiadekchan/history.html'
    posts = Post.objects.all().order_by('-ip_address')
    context = {'posts': posts}
    return render(request, template_name, context)



def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect(reverse('obiadekchan:index'))

def login(request):
    template_name = 'login.html'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            from django.contrib.auth import login
            login(request, user)
            return HttpResponseRedirect(reverse('obiadekchan:mode'))
        else:
            return HttpResponseRedirect(reverse('obiadekchan:login'))
    else:
        return render(request, 'obiadekchan/login.html')


def banned(request):
    template_name = 'obiadekchan/bane.html'
    from ipware import get_client_ip
    ip_address = get_client_ip(request)
    ban = Banned.objects.all().filter(ip_ad=ip_address)
    context = {'ban': ban}
    return render(request, template_name, context)


def ajaxPostPreview(request,pk):
    post = get_object_or_404(Post, pk=pk)
    #post = Post.objects.filter(id=pk)
    context = {'post': post}
    return render(request,'obiadekchan/post_preview.html', context)

def linking(request, pk):
    post = Post.objects.filter(id=pk)
    if len(post) == 0:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    if post[0].is_thread:
        url = "{}".format(pk)
    else:
        url = "{}".format(post[0].replies.all()[0].id)

    return redirect('obiadekchan:thread',pk=url)