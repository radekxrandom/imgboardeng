from django.db import models

# Create your models here.

class Post(models.Model):
    thread_pos = models.IntegerField(default=1)
    #pub_date = models.DateTimeField(auto_now_add=True)
    op_email = models.CharField(null=True,max_length=20,blank=True)
    post_title = models.CharField(null=True,max_length=20,blank=True)
    post_body = models.TextField()
    ip_address = models.GenericIPAddressField(protocol='IPv4')
    image = models.ImageField(upload_to='chanImgs/', blank=True, null=True)
    rep = models.BooleanField(blank=True, default=True)
    rep_reason = models.CharField(null=True, blank=True, max_length=20)
    banned = models.BooleanField(blank=True, default=True)
    count = models.IntegerField(null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True,null=True)
    rep_res = models.CharField(null=True, blank=True, default='No reason provided', max_length=200)
    password = models.CharField(max_length=20,null=True,blank=True)
    replies = models.ManyToManyField('self', blank=True, related_name='threadd')
    is_thread = models.BooleanField()


class Thread(models.Model):
    thread_pos = models.IntegerField(default=1)
    pub_date = models.DateTimeField(auto_now_add=True)
    op_email = models.CharField(null=True,max_length=20,blank=True)
    thread_title = models.CharField(null=True,max_length=20,blank=True)
    thread_body = models.TextField()
    ip_address = models.GenericIPAddressField(protocol='IPv4')
    image = models.ImageField(upload_to='chanImgs/', blank=True, null=True)
    rep = models.BooleanField(blank=True, default=True)
    rep_reason = models.CharField(null=True, blank=True, max_length=20)
    banned = models.BooleanField(blank=True, default=True)
    count = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    rep_res = models.CharField(null=True, blank=True, default='No reason provided', max_length=200)
    password = models.CharField(max_length=20,null=True,blank=True)

class Answer(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True)
    op_email = models.CharField(null=True,max_length=20,blank=True)
    answer_title = models.CharField(null=True,max_length=20,blank=True)
    answer_body = models.TextField()
    ip_address = models.GenericIPAddressField(protocol='IPv4')
    image = models.ImageField(upload_to='chanImgs/', blank=True, null=True)
    Thread = models.ForeignKey(Thread, on_delete=models.CASCADE,blank=True,
                               related_name='thread_ans')
    rep = models.BooleanField(blank=True, default=True)
    rep_reason = models.CharField(null=True, blank=True, max_length=20)
    banned = models.BooleanField(blank=True, default=True)
    count = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True, blank=True)
    rep_res = models.CharField(null=True, blank=True, default='No reason provided', max_length=200)
    password = models.CharField(max_length=20,null=True,blank=True)


class Banned(models.Model):
    ip_ad = models.CharField(null=True, max_length=20)
    length = models.DateTimeField()
    reason = models.CharField(null=True,max_length=100)
    post_content = models.TextField(null=True,blank=True)

class Misc(models.Model):
    thread_count = models.IntegerField()
    #post_count = models.IntegerField()
