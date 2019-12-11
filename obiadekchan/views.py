from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from pathlib import Path
from django.template import loader
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import messages 
from .models import Thread, Answer, Banned, Misc
from .forms import addThreadForm, addAnswerForm
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from bootstrap_modal_forms.generic import BSModalCreateView
import datetime
from django.utils import timezone
from django.core.paginator import Paginator



# Create your views here.

banned_ips = []



class IndexView(TemplateView):
    template_name = 'obiadekchan/index.html'
    def get(self, request, *args, **kwargs):
        q2 = Thread.objects.all().prefetch_related('thread_ans').order_by('-thread_pos')
        paginator = Paginator(q2, 5)
        page = request.GET.get('page')
        q3 = paginator.get_page(page)
        context = {'q2': q3, 'form': addThreadForm()}
        return render(request, 'obiadekchan/index.html', context)
    def post(self, request, *args, **kwargs):
        form = addThreadForm(request.POST, request.FILES)
        if request.method == 'POST':
            if 'post_thread' in request.POST:
                t_c_object = Misc.objects.first()
                if t_c_object == None:
                    t_c_object = Misc.objects.create(thread_count=1,post_count=1)
                if form.is_valid():
                    from django.db.models import Max
                    from ipware import get_client_ip
                    result = Thread.objects.all().aggregate(Max('thread_pos'))
                    my_list = []
                    for key,value in result.items():
                        my_list.append(value)
                    max_pos = my_list[0]
                    if max_pos is not None:
                        position = max_pos + 1
                    else:
                        position = 1
                    xpkej = form.save(commit=False)
                    xpkej.thread_pos = position
                    ip_address = get_client_ip(request)
                    xpkej.ip_address = ip_address
                    if Banned.objects.all().filter(ip_ad=ip_address):
                        ban = Banned.objects.all().get(ip_ad=ip_address)
                        ban_d = ban.length
                        now = timezone.now()
                        if ban_d > now:
                            return HttpResponseRedirect(reverse('obiadekchan:banned'))
                        else:
                            ban.delete()
                    thread_count = t_c_object.thread_count
                    post_count = t_c_object.post_count + 1
                    xpkej.count = post_count
                    t_c_object.thread_count = thread_count
                    t_c_object.post_count = post_count
                    if t_c_object.thread_count > 5:
                        det = Thread.objects.last()
                        det.delete()
                        t_c_object.thread_count = t_c_object.thread_count - 1
                    t_c_object.save()    
                    xpkej.save()
                    return HttpResponseRedirect(reverse('obiadekchan:index'))
                else:
                    q2 = Thread.objects.all().prefetch_related('thread_ans').order_by('-thread_pos')
                    return render(request, self.template_name, {'form':form, 'q2': q2})
            elif 'report_thread' in request.POST:
                thread = Thread.objects.get(pk=request.POST['report_thread'])
                thread.rep = False
                thread.rep_res = request.POST.get('r_reason')
                thread.save()
                return HttpResponseRedirect(reverse('obiadekchan:index'))
            elif 'delete_thread' in request.POST:
                thread = Thread.objects.get(pk=request.POST['delete_thread'])
                thread.delete()
                return HttpResponseRedirect(reverse('obiadekchan:index'))
            elif 'report_answer' in request.POST:
                answer = Answer.objects.get(pk=request.POST['report_answer'])
                answer.rep = False
                answer.rep_res = request.POST.get('r_reason')
                answer.save()
                return HttpResponseRedirect(reverse('obiadekchan:index'))
            elif 'delete_answer' in request.POST:
                answer = Answer.objects.get(pk=request.POST['delete_answer'])
                answer.delete()
                return HttpResponseRedirect(reverse('obiadekchan:index'))
            
            
class ThreadDetail(generic.DetailView):
    model = Thread
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = addAnswerForm()
        Thread.objects.all().prefetch_related('thread_ans')
        return context

class ThreadPost(TemplateView):
    template_name = 'obiadekchan/thread.html'
    model = Thread

    def get_object(self, *args, **kwargs):
        thread = get_object_or_404(Thread, pk=self.kwargs['pk'])

        return thread

    def post(self, request, *args, **kwargs):
        form = addAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            t_form = form.save(commit=False)
            thread = get_object_or_404(Thread, pk=self.kwargs['pk'])
            t_form.Thread = thread
            from django.db.models import Max
            from ipware import get_client_ip
            ip_address = get_client_ip(request)
            t_form.ip_address = ip_address
            banan = Banned.objects.all().filter(ip_ad=ip_address)
            if Banned.objects.all().filter(ip_ad=ip_address):
                ban = Banned.objects.all().get(ip_ad=ip_address)
                ban_d = ban.length
                now = timezone.now()
                if ban_d > now:
                    return HttpResponseRedirect(reverse('obiadekchan:banned'))
                else:
                    ban.delete()
            result = Thread.objects.all().aggregate(Max('thread_pos'))
            my_list = []
            for key,value in result.items():
                my_list.append(value)
            max_pos = my_list[0]
            position = max_pos + 1
            thread.thread_pos = position
            p_c_object = Misc.objects.first()
            post_count = p_c_object.post_count + 1
            t_form.count = post_count
            p_c_object.post_count = post_count
            p_c_object.save()
            thread.save()
            t_form.save()
            return HttpResponseRedirect(reverse('obiadekchan:index'))

class ThreadView(View):

    def get(self, request, *args, **kwargs):
        view = ThreadDetail.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ThreadPost.as_view()
        return view(request, *args, **kwargs)


class ModeratorView(View):
    def get(self, request, *args, **kwargs):
        template_name = 'obiadekchan/mode.html'
        context = {'threads': Thread.objects.all().filter(rep=False),
                   'answers':Answer.objects.all().filter(rep=False), 'banned': Banned.objects.all()}
        return render(request, template_name, context)
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            from ipware import get_client_ip
            if 'del_thread' in request.POST:
                thread = Thread.objects.get(pk=request.POST['del_thread'])
                thread.delete()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'ban_ip' in request.POST:
                thread = Thread.objects.get(pk=request.POST['ban_ip'])
                ip_address = thread.ip_address
                b_reason = request.POST.get('b_reason')
                b_length = request.POST.get('b_length')
                ban = Banned.objects.create(ip_ad=ip_address, reason=b_reason, length=b_length)
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'del_answer' in request.POST:
                answer = Answer.objects.get(pk=request.POST['del_answer'])
                answer.delete()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'ban_ans_ip' in request.POST:
                answer = Answer.objects.get(pk=request.POST['ban_ans_ip'])
                ip_address = answer.ip_address
                b_reason = request.POST.get('b_reason')
                b_length = request.POST.get('b_length')
                ban = Banned.objects.create(ip_ad=ip_address, reason=b_reason, length=b_length)
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'unban' in request.POST:
                ban = Banned.objects.get(pk=request.POST['unban'])
                ban.delete()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))




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
            return HttpResponseRedirect(reverse('obiadekchan:index'))
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