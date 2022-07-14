from django.shortcuts import render
from .forms import UserForm,LoginForm
from .models import User,Question,Test
from django.db.models import Max

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
            question = Question.objects.distinct().values('kind')
            print( question )
            params = {
                'question':question
            }

            return render(request , 'exam/select_menu.html',params)
        else:
            params['message'] = 'ログイン失敗'
    
    return render( request,'exam/index.html',params )

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