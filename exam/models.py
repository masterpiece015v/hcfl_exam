from django.db import models
from datetime import datetime

# Create your models here.

class User( models.Model ):
    user_id = models.CharField(max_length=40)
    password = models.CharField(max_length=40)
    user_name = models.CharField(max_length=40)
    super_user = models.BooleanField(default=False)

class Question( models.Model ):
    kind = models.CharField( max_length=20 )
    grade = models.CharField( max_length=20 )
    round = models.IntegerField()
    question_no = models.IntegerField()
    answer = models.CharField( max_length=40 )
    file_path = models.CharField( max_length=200,blank=True,null=True )

class Test( models.Model ):
    test_id = models.IntegerField(default=0)
    seq_no = models.IntegerField(default=0)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    answers = models.CharField(max_length=40,blank=True,null=True)
    update = models.DateTimeField(default=datetime.now)
