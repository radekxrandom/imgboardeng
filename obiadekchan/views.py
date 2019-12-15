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
import datetime
from django.utils import timezone
from django.core.paginator import Paginator
from .utils import checkBan, bumpThread, incrementPostCount
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator




# Create your views here.

banned_ips = []



class IndexView(View):
    template_name = 'obiadekchan/index.html'
    def get(self, request, *args, **kwargs):
        q2 = Thread.objects.all().prefetch_related('thread_ans').order_by('-thread_pos')
        paginator = Paginator(q2, 10)
        page = request.GET.get('page')
        q3 = paginator.get_page(page)
        context = {'q2': q3, 'form': addThreadForm()}
        return render(request, 'obiadekchan/index.html', context)

    def post(self, request, *args, **kwargs):
        form = addThreadForm(request.POST, request.FILES)
        if request.method == 'POST':
            if 'post_thread' in request.POST:
                t_c_object = Misc.objects.first()
                if t_c_object is None:
                    t_c_object = Misc.objects.create(thread_count=0,post_count=0)
                if form.is_valid():
                    from django.db.models import Max, Min
                    from ipware import get_client_ip
                    result = Thread.objects.all().aggregate(Max('thread_pos'))
                    xpkej = form.save(commit=False)
                    xpkej.thread_pos = bumpThread(result)
                    ip_address = get_client_ip(request)
                    xpkej.ip_address = ip_address
                    if checkBan(ip_address):
                        return HttpResponseRedirect(reverse('obiadekchan:banned'))
                    thread_count = t_c_object.thread_count
                    xpkej.count = incrementPostCount(t_c_object)
                    t_c_object.thread_count = thread_count + 1
                    if t_c_object.thread_count > 50:
                        det = Thread.objects.order_by('thread_pos').first()
                        det.delete()
                        t_c_object.thread_count = t_c_object.thread_count - 1
                    t_c_object.save()
                    xpkej.save()
                    return HttpResponseRedirect(reverse('obiadekchan:index'))
                else:
                    q2 = Thread.objects.all().prefetch_related('thread_ans').order_by('-thread_pos')
                    return render(request, self.template_name, {'form':form, 'q2': q2})
            elif 'report_thread' in request.POST:
                if 'rep_choice' in request.POST:
                    thread = Thread.objects.get(pk=request.POST['rep_choice'])
                    thread.rep = False
                    thread.rep_res = request.POST.get('r_reason')
                    thread.save()
                    return HttpResponseRedirect(reverse('obiadekchan:index'))
                elif 'a_rep_choice' in request.POST:
                    answer = Answer.objects.get(pk=request.POST['a_rep_choice'])
                    answer.rep = False
                    answer.rep_res = request.POST.get('r_reason')
                    answer.save()
                    return HttpResponseRedirect(reverse('obiadekchan:index'))  
            elif 'report_answer' in request.POST:
                answer = Answer.objects.get(pk=request.POST['report_answer'])
                answer.rep = False
                answer.rep_res = request.POST.get('r_reason')
                answer.save()
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
            if checkBan(ip_address):
                return HttpResponseRedirect(reverse('obiadekchan:banned'))
            result = Thread.objects.all().aggregate(Max('thread_pos'))
            mail = request.POST.get('op_email')
            if mail.lower() == 'sage':
                thread.thread_pos = thread.thread_pos
            else:
                thread.thread_pos = bumpThread(result)
            t_c_object = Misc.objects.first()
            t_form.count = incrementPostCount(t_c_object)
            thread.save()
            t_form.save()
            if mail.lower() == 'noko':
                return HttpResponseRedirect(reverse('obiadekchan:index'))            
            return HttpResponseRedirect(self.request.path_info)




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
        context = {'threads': Thread.objects.all().filter(rep=False),
                   'answers':Answer.objects.all().filter(rep=False), 'banned': Banned.objects.all()}
        return render(request, template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            from ipware import get_client_ip
            if 'del_thread' in request.POST:
                thread = Thread.objects.get(pk=request.POST['del_thread'])
                thread.delete()
                t_c_object = Misc.objects.first()
                t_c_object.thread_count = t_c_object.thread_count - 1
                t_c_object.save()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'ban_ip' in request.POST:
                thread = Thread.objects.get(pk=request.POST['ban_ip'])
                ip_address = thread.ip_address
                b_reason = request.POST.get('b_reason')
                b_length = request.POST.get('b_length')
                content = thread.thread_body
                ban = Banned.objects.create(ip_ad=ip_address, reason=b_reason, length=b_length, post_content=content)
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
                content = answer.answer_body
                ban = Banned.objects.create(ip_ad=ip_address, reason=b_reason, length=b_length, post_content=content)
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'unban' in request.POST:
                ban = Banned.objects.get(pk=request.POST['unban'])
                ban.delete()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'del_thread_report' in request.POST:
                thread = Thread.objects.get(pk=request.POST['del_thread_report'])
                thread.rep = True
                thread.rep_reason = None
                thread.save()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))
            elif 'del_answer_report' in request.POST:
                answer = Answer.objects.get(pk=request.POST['del_answer_report'])
                answer.rep = True
                answer.rep_reason = None
                answer.save()
                return HttpResponseRedirect(reverse('obiadekchan:mode'))


class CatalogView(View):

    def get(self, request, *args, **kwargs):
        threads = Thread.objects.all().order_by('-thread_pos')
        context = {'threads': threads}
        return render(request, 'obiadekchan/catalog.html', context) 





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