from django.shortcuts import render
from .forms import UserForm,LoginForm
from .models import User,Question,Test
from django.db.models import Max,Q
#from openpyxl import Workbook
from django.conf import settings
import os,json


# Create your views here.

def index( request ):
    params = {
        'form':LoginForm(),
    }
    #ログイン
    if request.method == 'POST':
        user = User.objects.filter(user_id=request.POST['user_id'],password=request.POST['password'])
        # ログイン成功
        if user.count() > 0:
            request.session['user_id'] = request.POST['user_id']
            request.session['super_user'] = user.first().super_user

            question = Question.objects.distinct().values('kind')
            print( question )
            params = {
                'question':question,
                'super_user':request.session['super_user'],
            }

            return render(request , 'exam/select_menu.html',params)
        else:
            params['message'] = 'ログイン失敗'
    
    return render( request,'exam/index.html',params )

def select_menu( request ):
    question = Question.objects.distinct().values('kind')
    print( question )
    params = {
        'question':question,
        'super_user':request.session['super_user'],
    }

    return render(request , 'exam/select_menu.html',params)

def new_user( request ):
    params ={
        'form':UserForm(),
    }

    #作成ボタン
    if request.method == 'POST':
        #user_idの重複チェック
        uc = User.objects.filter(user_id=request.POST['user_id'])
        if uc.count() > 0:
            params = {
                'form':UserForm(request.POST),
                'message':'user_idが重複しています',
            }
            return render( request,'exam/new_user.html',params )
        obj = User()
        user = UserForm(request.POST,instance=obj)
        user.save()
        params = {
            'form':LoginForm()
        }
        return render(request,'exam/index.html',params)

    return render( request,'exam/new_user.html',params )

def select_grade( request , kind ):
    question = Question.objects.filter(kind=kind).distinct().values('grade')
    print( question )
    params = {
        'kind':kind,
        'question':question
    }

    return render( request , 'exam/select_grade.html',params)

def question( request , no ):
    if request.method == 'POST':
        user = User.objects.filter(user_id=request.session['user_id']).first()
        kind = request.POST['kind']
        grade = request.POST['grade']
        num = request.POST['num']

        question = Question.objects.filter(kind=kind,grade=grade)
        q_id_list = [que.id for que in question]
        print( q_id_list )

        test_id_max = Test.objects.aggregate(Max('test_id'))
        print(test_id_max['test_id__max'] )
        if test_id_max['test_id__max'] == None:
            test_id = 1
        else:
            test_id = test_id_max['test_id__max'] + 1
    return render( request , 'exam/question.html')

def question_update( request ):
    if request.method == 'POST':
        data = request.POST['data']
        json_data = json.loads( data )
        
        #削除
        id_list = [q[0] for q in json_data]
        q = Question.objects.filter(~Q(id__in=id_list)).delete()

        #更新
        print( id_list )
        for item in json_data:
            if item[0] != None:
                q = Question.objects.get(id=item[0])
                #存在するので更新
                q.kind = item[1]
                q.grade = item[2]
                q.round = item[3]
                q.question_no = item[4]
                q.answer = item[5]
                q.file_path = item[6]
                q.save()
            else:
                #存在しないので追加
                q = Question(kind=item[1],grade=item[2],round=item[3],question_no=item[4],answer=item[5],file_path=item[6])
                q.save()
        
        
        #print( q[0].id )

        #print( json_data )
        question = Question.objects.all()
        params = {
            'data' : question,
        }
        return render( request,'exam/question_update.html',params )

    question = Question.objects.all()
    params = {
        'data' : question,
    }
    
    return render( request,'exam/question_update.html',params )