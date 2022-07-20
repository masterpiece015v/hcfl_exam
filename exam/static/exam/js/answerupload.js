$(function(){
    //ファイルを変更したときの処理
    $(document).on('change', ':file', function() {
        var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
        input.parent().parent().next(':text').val(label);
    });

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

    //JSONオブジェクトを文字列に変える
    function getJsonStr(json){
        return JSON.stringify(json);
    }

    //CSRF Tokenを取得する
    function getCSRFToken(){
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        return csrftoken;
    }

    //更新ボタン
    $("#btn_upload").on('click',function(){
        //ユーザのidを送信する
        var items = [];
        var flg = 0;
        $("#answer_table tr").each(function(i){
            //var item = [$(this).cells(0) ,$(this).eq(2).text()];
            //items.push( item );
            var item = [];
            $(this).children().each(function(i){
                if( i == 0 ){

                    item.push( $(this).text() );
                    //console.log( $(this).text() );
                }else{
                    item.push( $(this).children('input').val() );
                    //console.log( $(this).children('input').val());
                }
            });
            items.push( item );
        });
        var id = $('#select_id').val();
        var old_t_id = id.split('_')[0];
        var old_u_id = id.split('_')[1];

        var json = {'old_t_id':old_t_id,'old_u_id':old_u_id,'new_t_id':$('#t_id').val(),'new_u_id':$("#u_id").val() , 'answerlist':items };

        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_answerupload/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( json ),
        }).done( (data) => {

            $('#answer_table').children().remove();
            $('#modal-progress').modal('hide');
            alert( '更新完了' );

        }).fail( (data)=>{
            alert( data );
        }).always( (data) => {
        });
    });
    //追加ボタン
    $("#btn_all_insert").on('click',function(){

        var list = [];
        $('#select_id option').each( function(i){

            var t_id = $(this).text().split("_")[0];
            var u_id = $(this).text().split("_")[1];

            dict = {'t_id':t_id,'u_id':u_id};
            list.push( dict );

        });


        var json = { 'list' : list };

        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_answerallinsert/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( json ),
        }).done( (data) => {

            $("#select_id").children().remove();

            for( var i = 0 ; i < data['list'].length ; i++ ){
                $('#select_id').append( $('<option>').val(data['list'][i]['t_id'] + "_" + data['list'][i]['u_id'] + "_済").text(data['list'][i]['t_id'] + "_" + data['list'][i]['u_id'] + "_済") );

            }
            $('#modal-progress').modal('hide');
        }).fail( (data)=>{
            alert( data );
        }).always( (data) => {
        });

    });

    //追加ボタン
    $("#btn_insert").on('click',function(){
        var id = $('#select_id').val();
        var old_t_id = id.split("_")[0];
        var old_u_id = id.split("_")[1];
        var new_t_id = $('#t_id').val();
        var new_u_id = $('#u_id').val();

        //ユーザのidを送信する
        var items = [];
        var flg = 0;
        $("#answer_table tr").each(function(i){
            //var item = [$(this).cells(0) ,$(this).eq(2).text()];
            //items.push( item );
            var item = [];
            $(this).children().each(function(i){
                if( i == 0 ){

                    item.push( $(this).text() );
                    //console.log( $(this).text() );
                }else{
                    item.push( $(this).children('input').val() );
                    //console.log( $(this).children('input').val());
                }
            });
            items.push( item );
        });

        var json = {'old_t_id':old_t_id,'old_u_id':old_u_id,'new_t_id':$('#t_id').val(),'new_u_id':$("#u_id").val() , 'answerlist':items };

        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_answerinsert/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( json ),
        }).done( (data) => {

            //$(child_class).children().remove();
            $('#modal-progress').modal('hide');
            alert( data['message'] );
            $('#select_id option[value=' + id + ']').remove();
            $('#select_id').append($('<option>').val( new_t_id + '_' + new_u_id + '_済' ).text(new_t_id + '_' + new_u_id + '_済') );
        }).fail( (data)=>{
            alert( data );
        }).always( (data) => {
        });

    });

    //リストボックスの変更イベント
    $("#select_id").on('change',function(){

        var id = $(this).val();
        var t_id = id.split("_")[0];
        var u_id = id.split("_")[1];
        var ex = id.split("_")[2];
        var query = {'t_id':t_id,'u_id': u_id ,'ex':ex};

        if( id.split("_")[2] == '未'){
            $('#btn_upload').prop('disabled',true);
            $('#btn_insert').prop('disabled',false);
        }else{
            $('#btn_upload').prop('disabled',false);
            $('#btn_insert').prop('disabled',true);
        }

        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_getanswerlist/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( query ),
        }).done( (data) => {

            $('#answer_table').children().remove();

            $('#t_id').val( data['t_id'] );
            $('#u_id').val( data['u_id'] );

            for(var i = 0 ; i < data['answerlist'].length ; i++ ){
                $tr = $('<tr>');
                $td1 = $('<td>').text(data['answerlist'][i]['t_num']);
                $td2 = $('<td>');
                $td2.append( $('<input>').attr('type','text').val(data['answerlist'][i]['r_answer']) );
                $tr.append( $td1 );
                $tr.append( $td2 );
                $('#answer_table').append( $tr );
                console.log( data['answerlist'][i] );
            }


            $('#modal-progress').modal('hide');


        }).fail( (data)=>{
            alert( data );
        }).always( (data) => {
        });
    });

});