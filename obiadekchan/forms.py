from django import forms
from django.db import models
from .models import Banned, Post
from bootstrap_modal_forms.forms import BSModalForm


class addPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['op_email','post_title','post_body','image']
