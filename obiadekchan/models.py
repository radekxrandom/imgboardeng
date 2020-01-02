from django.db import models
import os
# Create your models here.
def file_name(instance, filename):
    org_name, file_ext = os.path.splitext(filename)
    #new_naem = 'img_' + str(instance.id)
    instance.rep_reason = org_name + file_ext
    return 'chanImgs/{naem}{ext}'.format(naem = org_name, ext= file_ext) 

class Post(models.Model):
    thread_pos = models.IntegerField(default=1)
    # pub_date = models.DateTimeField(auto_now_add=True)
    op_email = models.CharField(null=True, max_length=20, blank=True)
    post_title = models.CharField(null=True, max_length=20, blank=True)
    post_body = models.TextField()
    ip_address = models.GenericIPAddressField(protocol='IPv4')
    image = models.ImageField(upload_to=file_name, blank=True, null=True)
    rep = models.BooleanField(blank=True, default=True)
    rep_reason = models.CharField(null=True, blank=True, max_length=20)
    banned = models.BooleanField(blank=True, default=True)
    count = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    rep_res = models.CharField(
        null=True, blank=True, default='No reason provided', max_length=200)
    password = models.CharField(max_length=20, null=True, blank=True)
    replies = models.ManyToManyField(
        'self', blank=True, related_name='threadd')
    is_thread = models.BooleanField()
    is_op = models.BooleanField(null=True, blank=True)
    is_mode = models.BooleanField(null=True, blank=True)
   # edited = models.DateTimeField(auto_now=True,blank=True,null=True)

    def extension(self):
        name, extension = os.path.splitext(self.image.name)
        if extension.lower() == '.gif':
            return True
        else:
            return False


class Banned(models.Model):
    ip_ad = models.CharField(null=True, max_length=20)
    length = models.DateTimeField()
    reason = models.CharField(null=True,max_length=100)
    post_content = models.TextField(null=True,blank=True)

class Misc(models.Model):
    thread_count = models.IntegerField()
    # post_count = models.IntegerField()



