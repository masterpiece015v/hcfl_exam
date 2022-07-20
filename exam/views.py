from django.shortcuts import render
from .forms import UserForm,LoginForm
from .models import User,Question,Test
from django.db.models import Max,Q
#from openpyxl import Workbook
from django.conf import settings
import os,json,random,string
from django.http.response import JsonResponse

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
    group = User.objects.distinct().values('group_name')
    print( question )
    params = {
        'kind':kind,
        'question':question,
        'group':group,
        'super_user':request.session['super_user']
    }

    return render( request , 'exam/select_grade.html',params)

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
                'file_name':test.question.file_name,
                'test_id':test_id,
                'no': 1,
                'num' : num,
            }
            return render( request , 'exam/question.html',params )
        else:
            #次へボタンなどが押されたとき
            test_id = request.POST['test_id']
            state = request.POST['state']
            print( state )
            no = int( request.POST['no'] )
            num = request.POST['num']
            if 'ans' in request.POST:
                ans = request.POST['ans']
                test = Test.objects.filter(test_id=test_id,seq_no=no).first()
                test.answers = ans
                test.save()

                #print( ans )
            if( state == 'next'):
                no += 1
                test = Test.objects.filter(test_id=test_id,seq_no=no).first()
            elif(state == 'back'):
                no -= 1
                test = Test.objects.filter(test_id=test_id,seq_no=no).first()
            else:
                #endが押されたとき
                print( test_id )
                test = Test.objects.filter( test_id=test_id )
                result = []
                score = 0
                for item in test:
                    dict = {}
                    dict["question"] = item.question
                    dict["answers"] = item.answers
                    if item.question.answer == item.answers:
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

            
            num = request.POST['num']
            
            params = {
                'file_name':test.question.file_name ,
                'test_id':test_id,
                'no': no,
                'num' : num,
                'answers':test.answers,
            }
            print( test.answers )

            return JsonResponse( params )
            #return render( request , 'exam/question.html',params )
    return render( request , 'exam/index.html' )
    
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

def question_print( request ):
    if request.method == 'POST':
        kind = request.POST['kind']
        request.session['kind'] = kind
        grade = request.POST['grade']
        num = request.POST['num']
        question = Question.objects.filter(kind=kind,grade=grade)
        q_id_list = [que.id for que in question]
        test_id_max = Test.objects.aggregate(Max('test_id'))
        test_id_list = [q_id_list[i] for i in random.sample(range(len(q_id_list)),int(num))]
        user = User.objects.filter(user_id=request.session["user_id"]).first()

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

        test = Test.objects.filter(test_id=test_id)
        params = {
            'test':test,
            'test_id':test_id,
            'kind':kind,
        }
        return render( request , 'exam/question_print.html',params )

def getrndstr(n):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)

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

# 解答のアップロード
class AnswerUpload():
    # ページの表示
    def answerupload( request ):

        securecheck( request )
        u_admin = request.session['u_admin']
        # アップするファイルのパス
        o_id = request.session['o_id']
        media_path = os.path.join(settings.STATIC_ROOT,"jg","answer",o_id)

        if request.method != 'POST':
            answerimage = AnswerImage.objects.all()
            #リストの再取得
            filelist = []
            for file in answerimage:
                filelist.append( file )
            return render(request, 'jg/answerupload.html', {"filelist": filelist,'u_admin':u_admin})

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
                org_id, test_id, user_id, answerlist = get_answer_list(filepath)

                print( "%s,%s,%s"%(org_id,test_id,user_id) )
                print( answerlist )

                # 登録チェック
                check_answer = ResultTest.objects.filter( t_id=test_id,u_id=user_id )

                # すでにテストID＋ユーザIDが存在する場合
                if len( check_answer ) >= 1:
                    dict = {'t_id':test_id,'u_id':user_id,'exists':1}
                    list.append( dict )
                else:
                    # 解答をResultTestTempに登録する
                    date = datetime.datetime.now()
                    cnt = 0
                    for answer in answerlist:
                        if cnt < 80:
                            if answer[1] == "未回答" or answer[1] == "複数回答":
                                add_rt = ResultTestTemp(t_id=test_id, t_num=code4(answer[0]), r_answer='', r_date=date, u_id=user_id)
                            else:
                                add_rt = ResultTestTemp(t_id=test_id,t_num=code4(answer[0]),r_answer=answer[1],r_date=date,u_id=user_id)
                            add_rt.save()
                        cnt = cnt + 1
                    dict = {'t_id':test_id,'u_id':user_id,'exists':0}
                    list.append( dict )
            return render(request, 'jg/answerupload.html' , { 'list':list ,'u_admin':u_admin})

        elif 'del' in request.POST:
            image = request.POST['del']
            AnswerImage.objects.filter(image=image).delete()
            os.remove( os.path.join( media_path , image ))

            # リストの再取得
            answerimage = AnswerImage.objects.all()
            filelist = []
            for file in answerimage:
                filelist.append( file )

            return render( request, 'jg/answerupload.html' , { "filelist" : filelist ,'u_admin':u_admin})

    # insert
    def ajax_answerinsert( request):
        c_dic = byteToDic(request.body)
        o_id = request.session['o_id']
        print( c_dic )
        old_t_id = c_dic['old_t_id']
        old_u_id = c_dic['old_u_id']
        new_t_id = c_dic['new_t_id']
        new_u_id = c_dic['new_u_id']
        answerlist = c_dic['answerlist']

        media_path = os.path.join(settings.STATIC_ROOT, "exam", "answer", o_id)

        # 登録チェック
        check_answer = ResultTest.objects.filter(t_id=new_t_id, u_id=new_u_id)

        # すでにテストID＋ユーザIDが存在する場合
        if len(check_answer) >= 1:
            for i, a in enumerate(answerlist):
                result = ResultTest.objects.filter(t_id=new_t_id, u_id=new_u_id, t_num=code4(i + 1))
                result.update(r_answer=a[1])
            return HttpResponseJson({'message': '更新しました。'})
        else:
            # 解答をResultTestに登録する
            date = datetime.datetime.now()
            # テスト数を取得
            num = LittleTest.objects.filter(o_id=o_id, t_id=new_t_id).count()

            cnt = 0
            for answer in answerlist:
                if cnt < num:
                    if answer[1] == "未回答" or answer[1] == "複数回答":
                        add_rt = ResultTest(t_id=new_t_id, t_num=code4(answer[0]), r_answer='',r_date=date,u_id=new_u_id)
                    else:
                        add_rt = ResultTest(t_id=new_t_id, t_num=code4(answer[0]), r_answer=answer[1], r_date=date,u_id=new_u_id)
                    add_rt.save()
                cnt = cnt + 1

            # ResultTestTempのデータを削除する
            ResultTestTemp.objects.filter(t_id=old_t_id,u_id=old_u_id).delete()

            # ファイルを削除する
            #filelist = glob.glob(media_path + '/*')

            #for file in filelist:
                #print(os.path.join(media_path, file))
                # os.remove( os.path.join(media_path, file ) )
        c_dic['message'] = "追加できました。"
        return HttpResponseJson(c_dic)

    # すべて追加
    def ajax_answerallinsert(request):
        c_dic = byteToDic(request.body)
        o_id = request.session['o_id']

        list = c_dic['list']
        dict = {'list':[]}

        for l in list:
            # 登録チェック
            t_id = l['t_id']
            u_id = l['u_id']
            check_answer = ResultTest.objects.filter(t_id=t_id, u_id=u_id).distinct()

            # すでにテストID＋ユーザIDが存在する場合
            if len(check_answer) >= 1:
                dic = {'t_id':t_id , 'u_id':u_id}
                dict['list'].append( dic )

            else:
                # 解答をResultTestに登録する
                # date = datetime.datetime.now()
                # テスト数を取得
                num = LittleTest.objects.filter(o_id=o_id, t_id=t_id).count()

                cnt = 0
                resulttesttemp = ResultTestTemp.objects.filter(t_id=t_id,u_id=u_id).valuse()
                #answer = []
                for r in resulttesttemp:
                    if cnt < num:
                        add_rt = ResultTest(t_id=r['t_id'], t_num=r['t_id'], r_answer=r['r_answer'], r_date=r['r_date'],u_id=r['u_id'])
                        add_rt.save()
                    cnt = cnt + 1

                #ResultTestTempのデータを削除する
                ResultTestTemp.objects.filter(t_id=t_id, u_id=u_id).delete()
                dic = {'t_id': t_id, 'u_id': u_id}
                dict['list'].append(dic)

        return HttpResponseJson( dict )

    # upload
    def ajax_answerupload( request ):

        c_dic = byteToDic(request.body)
        o_id = request.session['o_id']

        old_t_id = c_dic['old_t_id']
        old_u_id = c_dic['old_u_id']
        new_t_id = c_dic['new_t_id']
        new_u_id = c_dic['new_u_id']
        answerlist = c_dic['answerlist']

        media_path = os.path.join(settings.STATIC_ROOT,"exam","answer",o_id)

        # 新しいidと古いidが違えば、古いidのほうを消す
        if new_t_id != old_t_id or new_u_id != old_u_id:
            ResultTest.objects.filter(t_id=old_t_id,u_id=old_u_id).delete()

        # 登録チェック
        check_answer = ResultTest.objects.filter(t_id=new_t_id, u_id=new_u_id)

        # すでにテストID＋ユーザIDが存在する場合は元のデータを更新
        if len(check_answer) >= 1:
            for i,a in enumerate( answerlist ):
                result=ResultTest.objects.filter(t_id=new_t_id,u_id=new_u_id,t_num=code4(i+1))
                result.update(r_answer=a[1])

            return HttpResponseJson( {'message':'更新しました。'})
        else:
        #ない場合は追加する
            # 解答をResultTestに登録する
            date = datetime.datetime.now()

            # テスト数を取得
            num = LittleTest.objects.filter(o_id=o_id, t_id=new_t_id).count()

            cnt = 0
            for answer in answerlist:
                if cnt < num:
                    if answer[1] == "未回答" or answer[1] == "複数回答":
                        add_rt = ResultTest(t_id=new_t_id, t_num=code4(answer[0]), r_answer='', r_date=date, u_id=new_u_id)
                    else:
                        add_rt = ResultTest(t_id=new_t_id, t_num=code4(answer[0]), r_answer=answer[1], r_date=date,u_id=new_u_id)
                    add_rt.save()
                cnt = cnt + 1
        c_dic['message'] = "登録できました。"
        return HttpResponseJson( c_dic )

    # t_idとu_idからテストの結果を取得する
    def ajax_getanswerlist(request):
        c_dic = byteToDic(request.body)
        o_id = request.session['o_id']

        t_id = c_dic['t_id']
        u_id = c_dic['u_id']
        ex = c_dic['ex']

        if ex == '未':
            resulttest = ResultTestTemp.objects.filter(t_id=t_id,u_id=u_id).values('t_num','r_answer')
        else:
            resulttest = ResultTest.objects.filter(t_id=t_id, u_id=u_id).values('t_num', 'r_answer')

        result = {'t_id':t_id,'u_id':u_id,'answerlist':[]}

        for r in resulttest:
            dict={'t_num':r['t_num'],'r_answer':r['r_answer']}
            result['answerlist'].append( dict )

        return HttpResponseJson( result )

#解答用紙印刷
class AnswerSheetPrint():
    # ページの表示
    def answersheetprint( request ):
        o_id = request.session['o_id']
        # URLにテストIDが含まれる場合
        if 't_id' in request.GET:
            t_id = request.GET.get('t_id')
            test = LittleTest.objects.filter(o_id=o_id, t_id=t_id)
            user = User.objects.filter(o_id=o_id)

            t_list = []
            for t in test:
                dic = {}
                dic['t_num'] = t.t_num
                dic['q_id'] = t.q_id
                t_list.append(dic)

            u_list = []
            for u in user:
                dic = {}
                dic['u_id'] = u.u_id
                dic['u_name'] = u.u_name
                u_list.append(dic)

            list = {'t_list': t_list, 'u_list': u_list, 'o_id': o_id}

            test = LittleTest.objects.filter(o_id=o_id).values('t_id', 't_date').distinct()
            t_list = []
            for t in test:
                dic = {}
                dic['t_id'] = t['t_id']
                dic['t_date'] = t['t_date']
                t_list.append(dic)

            u_groups = User.objects.filter(o_id=o_id).values('u_group').distinct()
            return render(request, 'jg/answersheetprint.html', {'test': t_list, 'u_groups':u_groups,'u_admin': request.session['u_admin'] , 't_id':t_id , 'list':list })

        #URLにテストIDを含まない場合（初めてアクセス）
        test = LittleTest.objects.filter(o_id=o_id).values('t_id','t_date').distinct()
        list = []
        for t in test:
            dic = {}
            dic['t_id'] = t['t_id']
            dic['t_date'] = t['t_date']
            list.append( dic )
        u_groups = User.objects.filter(o_id=o_id).values('u_group').distinct()

        return render( request, 'jg/answersheetprint.html',{'test':list,'u_groups':u_groups,'u_admin':request.session['u_admin'] })

    # ajax
    def ajax_answersheetprint( request ):
        t_id = byteToDic( request.body )['t_id']
        u_group = byteToDic( request.body)['u_group']
        o_id = request.session['o_id']

        test = LittleTest.objects.filter(o_id=o_id,t_id=t_id)
        user = User.objects.filter(o_id=o_id,u_group=u_group)

        t_list = []
        for t in test:
            dic = {}
            dic['t_num'] = t.t_num
            dic['q_id'] = t.q_id
            t_list.append( dic )

        u_list = []
        for u in user:
            dic = {}
            dic['u_id'] = u.u_id
            dic['u_name'] = u.u_name
            u_list.append( dic )

        list = {'t_list':t_list,'u_list':u_list , 'o_id':o_id }
        #print( list )
        return HttpResponseJson( list )
