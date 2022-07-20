$(function(){
    //JSONオブジェクトを文字列に変える
    function getJsonStr(json){
        return JSON.stringify(json);
    }
    //CSRF Tokenを取得する
    function getCSRFToken(){
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        return csrftoken;
    }

    $("#u_group,#t_id").on('change',function(){
        query = {'t_id':$("#t_id").val(),'u_group':$("#u_group").val()};
        $.ajaxSetup({
            beforeSend : function(xhr,settings ){
                xhr.setRequestHeader( "X-CSRFToken" , getCSRFToken() );
            }
        });
        $.ajax({
            type:"POST",
            url:"/jg/ajax_answersheetprint/",
            dataType:'json',
            contentType: 'charset=utf-8',
            data: getJsonStr( query ),
        }).done( (data) => {
            $print = $("#print");
            $print.children().remove();
            t_list = data['t_list'];
            u_list = data['u_list'];
            o_id = data['o_id'];
            //ユーザがいなくなるまで繰り返す
            for( var i = 0 ; i < u_list.length ; i = i + 1 ){
                $username = $("<p>").text( "ユーザ名:" + u_list[i]['u_name'] ).attr("class","user-name");
                $print.append( $username );
                $t_tr = $("<tr>").append(
                    $("<td>").append( $("<img>").attr("src","/static/jg/image/omr/marker.png") ).attr("class","marker"),
                    $("<td>").text( '組織ID').attr("colspan","5").attr("class","user"),
                    $("<td>").text( o_id ).attr("colspan","5").attr("class","num-id").attr("class","user"),
                    $("<td>").text( 'テストID' ).attr("colspan","5").attr("class","user"),
                    $("<td>").text( query['t_id']).attr("colspan","5").attr("class","num-id").attr("class","user"),
                );
                $u_tr = $("<tr>").append(
                    $("<td>").append( $("<img>").attr("src","/static/jg/image/omr/marker.png") ).attr("class","marker"),
                    $("<td>").text( 'ユーザID' ).attr("colspan","5").attr("class","user"),
                    $("<td>").text( u_list[i]['u_id'] ).attr("colspan","5").attr("class","num-id").attr("class","user"),
                    $("<td>").attr("colspan","5").attr("class","user"),
                    $("<td>").attr("colspan","5").attr("class","num-id").attr("class","user")
                );
                $table = $("<table>").attr("class","mark-sheet");
                $print.append( 
                    $("<div>").append( 
                        $table.append( $t_tr,$u_tr )
                    )
                );
                    $table.append( 
                        $("<tr>").attr("class","t-head").append(
                            $("<td>").append( $("<img>").attr("src","/static/jg/image/omr/marker.png") ).attr("class","marker"),
                            $("<th>").text("No").attr("class","t-num"),
                            $("<th>").attr("class","t-head").text("ア"),
                            $("<th>").attr("class","t-head").text("イ"),
                            $("<th>").attr("class","t-head").text("ウ"),
                            $("<th>").attr("class","t-head").text("エ"),
                            $("<th>").text("No").attr("class","t-num"),
                            $("<th>").attr("class","t-head").text("ア"),
                            $("<th>").attr("class","t-head").text("イ"),
                            $("<th>").attr("class","t-head").text("ウ"),
                            $("<th>").attr("class","t-head").text("エ"),
                            $("<th>").text("No").attr("class","t-num"),
                            $("<th>").attr("class","t-head").text("ア"),
                            $("<th>").attr("class","t-head").text("イ"),
                            $("<th>").attr("class","t-head").text("ウ"),
                            $("<th>").attr("class","t-head").text("エ"),
                            $("<th>").text("No").attr("class","t-num"),
                            $("<th>").attr("class","t-head").text("ア"),
                            $("<th>").attr("class","t-head").text("イ"),
                            $("<th>").attr("class","t-head").text("ウ"),
                            $("<th>").attr("class","t-head").text("エ"),
                        )
                    );
                    for( var j = 0 ; j < 20 ; j = j + 1 ){
                        if( j < 9 ){
                            $table.append(
                                $("<tr>").append(
                                    $("<td>").append( $("<img>").attr("src","/static/jg/image/omr/marker.png") ).attr("class","marker"),
                                    $("<td>").text('000' + (j+1)).attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('002' + (j+1)).attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('004'+ (j+1)).attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('006' + (j+1)).attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                )
                            );
                        }else if( j == 9 ){
                            $table.append(
                                $("<tr>").append(
                                    $("<td>").append( $("<img>").attr("src","/static/jg/image/omr/marker.png") ).attr("class","marker"),
                                    $("<td>").text('0010').attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('0030').attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('0050').attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('0070').attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                )
                            );
                        }else{
                           $table.append(
                                $("<tr>").append(
                                    $("<td>").append( $("<img>").attr("src","/static/jg/image/omr/marker.png") ).attr("class","marker"),
                                    $("<td>").text('00'+(j+1)).attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('00'+(j+21)).attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('00'+(j+41)).attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text('00'+(j+61)).attr("class","t-num"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                    $("<td>").text("〇").attr("class","maru"),
                                )
                            );
                        }

                    }

                $print.append(
                    $("<div>").attr("style","page-break-after: always")
                );
            }
            $('#modal-progress').modal('hide');
        }).fail( (data)=>{
            alert('fail');
        }).always( (data) => {
        });
    });
});