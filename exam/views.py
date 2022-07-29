from django.shortcuts import render
from .forms import UserForm,LoginForm
from .models import User,Question,Test,Result
from django.db.models import Max,Q
#from openpyxl import Workbook
from django.conf import settings
import os,json,random,string
from django.http.response import JsonResponse
from .markreader import get_answer_list
from django.core import serializers

# Create your views here.

#ログイン
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

#トップのメニュー画面
def select_menu( request ):
    question = Question.objects.distinct().values('kind')
    print( question )
    params = {
        'question':question,
        'super_user':request.session['super_user'],
    }

    return render(request , 'exam/select_menu.html',params)

#ユーザの新規作成
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

#級を選択する画面
def select_grade( request , kind ):
    question = Question.objects.filter(kind=kind).distinct().values('grade')
    group = User.objects.distinct().values('group_name')
    print( question )
    params = {
        'kind':kind,
        'question':question,
        'group':group,
        'super_user':request.session['super_user']
    }

    return render( request , 'exam/select_grade.html',params)

#cbt試験画面
def question( request ):
    if request.method == 'POST':
        user = User.objects.filter(user_id=request.session['user_id']).first()
        #科目の種類が含まれる（初回アクセス時）
        if 'kind' in request.POST:
            kind = request.POST['kind']
            request.session['kind'] = kind
            grade = request.POST['grade']
            num = request.POST['num']
            question = Question.objects.filter(kind=kind,grade=grade)
            q_id_list = [que.id for que in question]
            test_id_max = Test.objects.aggregate(Max('test_id'))
            test_id_list = [q_id_list[i] for i in random.sample(range(len(q_id_list)),int(num))]
            
            # 最大テストidの取得
            if test_id_max['test_id__max'] == None:
                test_id = 1
            else:
                test_id = test_id_max['test_id__max'] + 1
            
            #ランダムなテストを作る
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

            test = Test.objects.filter(test_id=test_id)

            #解答テーブルを作る
            for item in test:
                r = Result(test=item,ans_user=user)
                r.save()

            params = {
                'file_name':test.first().question.file_name,
                'test_id':test_id,
                'no': 1,
                'num' : num,
            }
            return render( request , 'exam/question.html',params )
        else:
            #次へボタンなどが押されたとき
            test_id = request.POST['test_id']
            state = request.POST['state']
            no = int( request.POST['no'] )
            num = request.POST['num']
            user = User.objects.filter(user_id=request.session['user_id']).first()
            
            ret = Result.objects.filter(test__test_id=test_id,test__seq_no=no,ans_user=user).first()
            
            if 'ans' in request.POST:
                ans = request.POST['ans']
                ret.answers = ans
                ret.save()

            if( state == 'next'):
                no += 1
                test = Test.objects.filter(test_id=test_id,seq_no=no).first()
                print(test.question)
            elif(state == 'back'):
                no -= 1
                test = Test.objects.filter(test_id=test_id,seq_no=no).first()
            else:
                #endが押されたとき
                print( test_id )
                ret = Result.objects.filter(test__test_id=test_id,ans_user=user)
                result = []
                score = 0
                for item in ret:
                    dict = {}
                    dict["question"] = item.test.question
                    dict["answers"] = item.answers
                    if item.test.question.answer == item.answers:
                        score+=1
                    result.append( dict )
                params = {
                    'user_name' : User.objects.filter(user_id=request.session['user_id']).first().user_name,
                    'result' : result,
                    'kind':request.session['kind'],
                    'score':score,
                    'num':num,
                }

                print( params )
                return render( request, "exam/parsonal_result.html" , params)
            
            #nextとbackはjson返す
            num = request.POST['num']
            ret = Result.objects.filter(test__test_id=test_id,test__seq_no=no,ans_user=user).first()
            params = {
                'file_name':test.question.file_name ,
                'test_id':test_id,
                'no': no,
                'num' : num,
                'answers':ret.answers,
            }
            print( params )
            return JsonResponse( params )
            #return render( request , 'exam/question.html',params )
    return render( request , 'exam/index.html' )

# 問題を更新する
def question_update( request ):
    if request.method == 'POST':
        if 'data' in request.POST:
            data = request.POST['data']
            json_data = json.loads( data )
            
            #削除
            id_list = [q[0] for q in json_data]
            q = Question.objects.filter(~Q(id__in=id_list))
            for item in q:
                os.remove( os.path.join(settings.MEDIA_ROOT,'exam',item.file_name))
                item.delete()

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

# テストを作って問題を印刷する
def question_print( request ):
    if request.method == 'POST':
        kind = request.POST['kind']
        request.session['kind'] = kind
        grade = request.POST['grade']
        num = request.POST['num']
        group = request.POST['group']
        question = Question.objects.filter(kind=kind,grade=grade)
        q_id_list = [que.id for que in question]
        test_id_max = Test.objects.aggregate(Max('test_id'))
        test_id_list = [q_id_list[i] for i in random.sample(range(len(q_id_list)),int(num))]
        
        #ログインユーザ
        user = User.objects.filter(user_id=request.session["user_id"]).first()

        #ランダムに作る
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
        test = Test.objects.filter(test_id=test_id)
        user = User.objects.filter(group_name=group)
        params = {
            'test':test,
            'test_id':test_id,
            'kind':kind,
            'user':user,
        }

        #resultを作る
        for t in test:
            for u in user:
                r = Result(test=t,ans_user=u)
                r.save()
        return render( request , 'exam/question_print.html',params )

# ランダムな文字列を取得する
def getrndstr(n):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)

# ユーザを表で更新する
def user_update( request ):
    if request.method == 'POST':
        if 'data' in request.POST:
            data = request.POST['data']
            json_data = json.loads( data )
            
            #削除
            id_list = [q[0] for q in json_data]
            u = User.objects.filter(~Q(id__in=id_list))
            for item in u:
                item.delete()

            #更新
            print( id_list )
            for item in json_data:
                if item[0] != None:
                    u = User.objects.get(id=item[0])
                    #存在するので更新
                    u.user_id = item[1]
                    u.password = item[2]
                    u.user_name = item[3]
                    u.group_name = item[4]
                    if item[5] == None:
                        u.super_user = False
                    else:
                        u.super_user = item[5]
                    print( item[5])
                    u.save()
                else:
                    #存在しないので追加
                    print( item[5] )
                    if item[5] == None:
                        u = User(user_id=item[1],password=item[2],user_name=item[3],group_name=item[4],super_user=False)
                    else:
                        u = User(user_id=item[1],password=item[2],user_name=item[3],group_name=item[4],super_user=item[5])
                    u.save()
            
            
            #print( q[0].id )

            #print( json_data )
            user = User.objects.all()
            params = {
                'data' : user,
            }
            return render( request,'exam/user_update.html',params )

        
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
        user = User.objects.all()
        params = {
            'data' : user,
        }
        
        return render( request,'exam/user_update.html',params )

# 解答のアップロードajax
def ajax_answer_upload_imgup( request ):
    # アップするファイルのパス
    media_path = os.path.join(settings.STATIC_ROOT,"exam","image","answer")
    print( request.POST )
    # リクエストにfileが含まれている
    if 'file' in request.FILES:

        upfiles = request.FILES.getlist('file')

        #複数ファイルのアップは拒否
        #if len(upfiles)>1:
        #    return render(request, 'exam/answerupload.html',{"message": "ファイルのアップロードは1つずつにしてください。",'u_admin':u_admin})

        #複数のファイルがアップロードされる
        list = []
        for uf in upfiles:
            files = os.listdir( media_path )
            if len(files)+1 < 10:
                num = "00" + str( len(files)+1 )
            elif len(files)+1 < 100:
                num = "0" + str( len(files)+1)
            else:
                num = str(len(files)+1)
            filename = "answer%s.jpg"%num
            filepath = os.path.join( media_path , filename )
            dest = open( filepath ,'wb+')

            for chunk in uf:
                dest.write( chunk )

            # 画像認識
            group_id, test_id, user_id, answer_list = get_answer_list(filepath)
            
            dic = {'group_id':group_id,'test_id':test_id,'user_id':user_id,'answer_list':answer_list}
            print( "%s,%s,%s"%(group_id,test_id,user_id) )
            print( answer_list )
            list.append( dic )
            # 登録チェック
            #check_answer = ResultTest.objects.filter( t_id=test_id,u_id=user_id )

            # すでにテストID＋ユーザIDが存在する場合
            #if len( check_answer ) >= 1:
            #    dict = {'t_id':test_id,'u_id':user_id,'exists':1}
            #    list.append( dict )
            #else:
                # 解答をResultTestTempに登録する
            #    date = datetime.datetime.now()
            #    cnt = 0
            #    for answer in answerlist:
            #        if cnt < 80:
            #            if answer[1] == "未回答" or answer[1] == "複数回答":
            #                add_rt = ResultTestTemp(t_id=test_id, t_num=code4(answer[0]), r_answer='', r_date=date, u_id=user_id)
            #            else:
            #                add_rt = ResultTestTemp(t_id=test_id,t_num=code4(answer[0]),r_answer=answer[1],r_date=date,u_id=user_id)
            #            add_rt.save()
            #        cnt = cnt + 1
            #    dict = {'t_id':test_id,'u_id':user_id,'exists':0}
            #    list.append( dict )
        return JsonResponse({'list':list})


# 解答のアップロード
def answer_upload( request ):
    return render(request, 'exam/answer_upload.html')

def ajax_answer_update( request ):
    #print( request.POST )
    data = request.POST['data']
    json_data = json.loads( data )

    for item in json_data:
        group_id = item['0']
        test_id = item['1']
        user_id = item['2']
        seq_no = item['3']
        answers = item['4']
        u = User.objects.filter(user_id=user_id).first()
        #userが存在しない
        if u == None:
            return JsonResponse({'data':'error'})
        t = Test.objects.filter(test_id=test_id,user=u,seq_no=seq_no).first()
        if t == None:
            return JsonResponse({'data':'error'})
        
        #未回答でなければ登録
        if answers != '未回答':
            r = Result.objects.filter(test=t,ans_user=u).first()
            if r == None:
                #新規作成
                r2 = Result(test=t,ans_user=u,answers=answers)
                r2.save()
            else:
                r.answers = answers
                r.save()

            print( "{},{},{},{}".format(group_id,test_id,user_id,str(seq_no)) )
    #print( data )
    ret_test = Result.objects.filter(test=t,ans_user=u).values('test__test_id','test__seq_no','ans_user__user_id','question')
    print( ret_test )
    ret_list = []
    for item in ret_test:
        dic = {}
        dic['test_id'] = item['test_id']
        dic['seq_no'] = item['seq_no']
        dic['user_id'] = item['user__user_id']
        dic['question']
    ret_test = serializers.serialize("json", ret_test)
    return JsonResponse({'data':ret_test})