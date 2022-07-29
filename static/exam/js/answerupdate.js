$(function(){
    //4桁のコードを作る
    function getcode4( code ){
        if(code < 10){
            return '000' + String(code);
        }else if(code < 100){
            return '00' + String(code);
        }else if(code < 1000){
            return '0' + String(code);
        }else{
            return String(code);
        }
    }

    //排他的でランダムな値を取得する
    function* getrandom( max ){
        
        var ary = new Array( max );

        for(var i = 0 ; i < max ; i++ ){
                   
            var r = Math.floor( Math.random() * max + 1);
        
            while( ary[r] == 1 ){
                r = Math.floor( Math.random() * max + 1);
            }
            ary[r] = 1;
            yield r;
        }
    }

    //JSONオブジェクトを文字列に変える
    function getJsonStr(json){
        return JSON.stringify(json);
    }

    //CSRF Tokenを取得する
    function getCSRFToken(){
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        return csrftoken;
    }

    //問題番号を取得するajax
    function ajax_getuid(child_class, query ){
        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_au_getuid/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( query ),
        }).done( (data) => {
            //$('#question').children().remove();
            $( child_class ).children().remove();

            for( var i = 0 , len=data['users'].length; i<len;++i){
                //全クリア

                //追加
                //Object.keys(data).forEach( function( key ){
                $option = $('<option>').val( data['users'][i]['u_id'] ).text( data['users'][i]['u_name'] );
                //alert( data['t_id'][i] );
                $( child_class ).append( $option );
                //});
            }

        }).fail( (data)=>{
            alert( data );
        }).always( (data) => {
        });
    }

    //問題番号を取得するajax
    function ajax_gettid(child_class, query ){
        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_au_gettid/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( query ),
        }).done( (data) => {
            //$('#question').children().remove();
            $( child_class ).children().remove();
            for( var i = 0 , len=data.length; i<len;++i){
                //全クリア

                //追加
                //Object.keys(data).forEach( function( key ){
                $option = $('<option>').val( data[i] ).text( data[i] );
                //alert( data['t_id'][i] );
                $( child_class ).append( $option );
                //});
             }

        }).fail( (data)=>{
            alert( data );
        }).always( (data) => {
        });
    }

    //結果を取得する
    function ajax_getresult(child_class, query ){
        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_au_getresult/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( query ),
        }).done( (data) => {
            $('#resultdata').children().remove();
            console.log( data );
            for( var i = 0 ; i < data.length ; i++ ){
                $tr = $('<tr>');
                $td = $('<td>');
                $input1 = $('<input>').attr('type','text').val(data[i].t_num).text(data[i].t_num);
                $td.append( $input1 );
                $tr.append( $td );
                $td = $('<td>');
                $input1 = $('<input>').attr('type','text').val(data[i].r_answer).text(data[i].r_answer);
                $td.append( $input1 );
                $tr.append( $td );
                $('#resultdata').append( $tr );
            }
            for( var i = data.length +1 ; i < data.length + 21 ; i++ ){
                
                if( i < 10 ){
                    t_num = "000" + i;
                }else{
                    t_num = "00" + i;
                }

                $tr = $('<tr>');
                $td = $('<td>');
                $input1 = $('<input>').attr('type','text').val(t_num).text(t_num);
                $td.append( $input1 );
                $tr.append( $td );
                $td = $('<td>');
                $input1 = $('<input>').attr('type','text');
                $td.append( $input1 );
                $tr.append( $td );
                $('#resultdata').append( $tr );                
            }

        }).fail( (data)=>{
            alert( data );
        }).always( (data) => {
        });
    }

    //問題番号を取得するajax
    function ajax_update(child_class, query ){
        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_au_update/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( query ),
        }).done( (data) => {
            alert( data['message'])

        }).fail( (data)=>{
            alert( data );
        }).always( (data) => {
        });
    }

    //グループ名の変更
    $("#u_group").on('click',function(){
        var json = {'u_group':$("#u_group").val() };
        ajax_gettid( '#lst_tid' , json );
        ajax_getuid( '#u_id', json );
    });

    //テストのリストをクリック
    $('#lst_tid').on('click',function(){
      
        if( $('#u_id').val() != null ){
            var json = {'u_id' : $('#u_id').val() , 't_id':$('#lst_tid').val()};
            ajax_getresult( '#resultdata' , json );
        }

    });
    //
    $('#u_id').on('click',function(){
        if( $('#lst_tid').val() != null){
            var json = {'u_id' : $('#u_id').val() , 't_id':$('#lst_tid').val()};
            ajax_getresult( '#resultdata' , json );
        }
    });

    //更新ボタン
    $('#update').on('click',function(){

        var json = {};
        t_id = $('#lst_tid').val();
        u_id = $('#u_id').val();

        json['t_id'] = t_id;
        json['u_id'] = u_id;
        ans_list = [];
        $resultdata = $("#resultdata input");
        $resultdata.each(function(index,element){
            if( index % 2 == 0 ){
                dic = {};
                dic['t_num'] = $(element).val();
            }else{
                dic['r_answer'] = $(element).val();
                ans_list.push( dic );
            }
        });
        json['list'] = ans_list;

        ajax_update( '', json );

        console.log( json );
    });
});