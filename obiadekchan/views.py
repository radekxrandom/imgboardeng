from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from pathlib import Path
from django.template import loader
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import messages 
from .models import Thread, Answer
from .forms import addThreadForm, addAnswerForm
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required


# Create your views here.

class IndexView(TemplateView):
    template_name = 'obiadekchan/index.html'
    def get(self, request, *args, **kwargs):
        q2 = Thread.objects.all().prefetch_related('thread_ans').order_by('-thread_pos')
        context = {'q2': q2, 'form': addThreadForm()}
        return render(request, 'obiadekchan/index.html', context)
    def post(self, request, *args, **kwargs):
        form = addThreadForm(request.POST, request.FILES)
        if request.method == 'POST':
            if 'post_thread' in request.POST:
                if form.is_valid():
                    from django.db.models import Max
                    from ipware import get_client_ip
                    result = Thread.objects.all().aggregate(Max('thread_pos'))
                    my_list = []
                    for key,value in result.items():
                        my_list.append(value)
                    max_pos = my_list[0]
                    position = max_pos + 1
                    xpkej = form.save(commit=False)
                    xpkej.thread_pos = position
                    xpkej.ip_address = get_client_ip(request)
                    xpkej.save()
                    return HttpResponseRedirect(reverse('obiadekchan:index'))
                else:
                    q2 = Thread.objects.all().prefetch_related('thread_ans').order_by('-thread_pos')
                    return render(request, self.template_name, {'form':form, 'q2': q2})
            elif 'report_thread' in request.POST:
                thread = Thread.objects.get(pk=request.POST['report_thread'])
                thread.rep = False
                thread.save()
                return HttpResponseRedirect(reverse('obiadekchan:index'))
            elif 'delete_thread' in request.POST:
                thread = Thread.objects.get(pk=request.POST['delete_thread'])
                thread.delete()
                return HttpResponseRedirect(reverse('obiadekchan:index'))
            elif 'report_answer' in request.POST:
                answer = Answer.objects.get(pk=request.POST['report_answer'])
                answer.rep = False
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
            result = Thread.objects.all().aggregate(Max('thread_pos'))
            my_list = []
            for key,value in result.items():
                my_list.append(value)
            max_pos = my_list[0]
            position = max_pos + 1
            thread.thread_pos = position
            thread.ip_address = get_client_ip(request)
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

@login_required
def ModeratorView(request):
    template_name = 'obiadekchan/mode.html'
    context = {'threads': Thread.objects.all().filter(rep=True), 'answers':Answer.objects.all().filter(rep=True)}
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
            return HttpResponseRedirect(reverse('obiadekchan:index'))
        else:
            return HttpResponseRedirect(reverse('obiadekchan:login'))
    else:
        return render(request, 'obiadekchan/login.html')

