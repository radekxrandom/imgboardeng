from django import forms
from django.db import models
from .models import Thread, Answer

class addThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['op_email','thread_title','thread_body','image']

class addAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['op_email','answer_title','answer_body','image']