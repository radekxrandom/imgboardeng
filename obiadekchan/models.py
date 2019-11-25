from django.db import models

# Create your models here.



    
class Thread(models.Model):
    thread_pos = models.IntegerField(default=1)
    pub_date = models.DateTimeField(auto_now_add=True)
    op_email = models.CharField(null=True,max_length=20)
    thread_title = models.CharField(null=True,max_length=20)
    thread_body = models.TextField()
    ip_address = models.GenericIPAddressField(null=True)
    image = models.ImageField(upload_to='chanImgs/', blank=True, null=True)
    rep = models.BooleanField(blank=True, default=True)
    rep_reason = models.CharField(null=True, blank=True, max_length=20)
class Answer(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True)
    op_email = models.CharField(null=True,max_length=20)
    answer_title = models.CharField(null=True,max_length=20)
    answer_body = models.TextField()
    ip_address = models.GenericIPAddressField(null=True)
    image = models.ImageField(upload_to='chanImgs/', blank=True, null=True)
    Thread = models.ForeignKey(Thread, on_delete=models.CASCADE,blank=True,related_name='thread_ans')
    rep = models.BooleanField(blank=True, default=True)
    rep_reason = models.CharField(null=True, blank=True, max_length=20)

