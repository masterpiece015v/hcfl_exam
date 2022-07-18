from django.shortcuts import render
from .forms import UserForm,LoginForm
from .models import User,Question,Test
from django.db.models import Max,Q
#from openpyxl import Workbook
from django.conf import settings
import os,json,random,string


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

def question( request ):
    if request.method == 'POST':
        user = User.objects.filter(user_id=request.session['user_id']).first()
        if 'kind' in request.POST:
            kind = request.POST['kind']
            grade = request.POST['grade']
            num = request.POST['num']

            question = Question.objects.filter(kind=kind,grade=grade)
            q_id_list = [que.id for que in question]
            #print( q_id_list )
            #print( random.sample(range(len(q_id_list)),int(num)))
            test_id_max = Test.objects.aggregate(Max('test_id'))
            #print(test_id_max['test_id__max'] )
            test_id_list = [q_id_list[i] for i in random.sample(range(len(q_id_list)),int(num))]
            print( test_id_list )
            if test_id_max['test_id__max'] == None:
                test_id = 1
            else:
                test_id = test_id_max['test_id__max'] + 1
            seq = 1
            for i in test_id_list:
                q = Question.objects.get(id=i)
                t = Test(
                test_id = test_id,
                seq_no = seq,
                user = user,
                question = q,
                )
                t.save()
                seq += 1

            test = Test.objects.filter(test_id=test_id,seq_no=1).first()
            params = {
                'test':test,
                'test_id':test_id,
                'no': 1,
                'num' : num,
            }
            return render( request , 'exam/question.html',params )
        else:
        
            test_id = request.POST['test_id']
            no = request.POST['no']
            test = Test.objects.filter(test_id=test_id,seq_no=no).first()
            params = {
                'test':test,
                'test_id':test_id,
                'no': no,
                'num' : num,
            }

            return render( request , 'exam/question.html',params )
    return render( request , 'exam/index.html' )
    
def question_update( request ):
    if request.method == 'POST':
        if 'data' in request.POST:
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

        
        else:
            #print( request.FILES )
            f = request.FILES['file']
            file_name = getrndstr(8)+'.png'
            filepath = os.path.join( settings.MEDIA_ROOT , 'exam', file_name )

            with open(os.path.join( filepath ),'wb+') as dest:
                for chunk in f.chunks( f ):
                    dest.write( chunk )
            
            id = request.POST["id"]
            
            q = Question.objects.get( id= id)
            q.file_name = file_name
            q.save()

            question = Question.objects.all()
            params = {
                'data' : question,
            }

            return render( request,'exam/question_update.html',params)
    else:
        question = Question.objects.all()
        params = {
            'data' : question,
        }
        
        return render( request,'exam/question_update.html',params )

def getrndstr(n):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)

"""
def upload_file( reqeust ):
    if request.method == 'POST':
        form = UploadFileForm( request.POST,request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            with open() as dest:
                for chunk in f.chunks()
                    dest.write( chunk )
            return render()
    else:
        form= UploadFileForm()
        return render( request,'exam/upload.html',{'form':form}) 
"""