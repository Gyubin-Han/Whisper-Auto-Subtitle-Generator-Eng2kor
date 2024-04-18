<%@ page language="java" contentType="text/html; charset=utf-8" pageEncoding="utf-8" %>
<!DOCTYPE html>
<html>
  <head>
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <style>
      .bcontainer{
        display:flex;
        height: 100%;
        margin:15px;
      }

      .bcontainer>aside{
        flex:3;
        border:1px solid green;
      }
      .bcontainer>article{
        flex:7;
        border:1px solid blue;
      }

      .container-select{
        text-align:center;
      }
      .btn-custom-select{
        background-color:blue;
        color:white;
        font-weight:bold;
        margin:3px;
      }
      .btn-custom-select:hover{
        background-color:lightgreen;
        color:black;
      }
      #container-select-form{
        width:100%;
        padding:10px;
      }
      #container-select-form>textarea{
        width:100%;
        resize:none;
        overflow:hidden;
      }
      #container-select-form>input, #container-select-form>button{
        width:100%;
        margin:10px 0;
      }

      .translateVideo{
        border:1px solid gray;
        margin:10px;
        padding:10px;
        display:flex;
      }
      .translateVideoImage{
        flex:3;
        text-align:center;
        align-self:center;
      }
      .translateVideoInfo{
        flex:7;
        align-self:center;
      }
      img{
        max-width: 230px;
      }
      tr>th, tr>td{
        padding:5px;
      }
    </style>
    <script src="/js/jquery-3.7.1.min.js"></script>
    <script>
      // 초기 접속 시, 번역하려는 동영상이 있는지 표현하는 변수
      //   (true = 동영상 없음)
      let isNoVideo = true;
      // 동영상 목록 번호 - 사용자 기준
      //   (번역 목록 내에서만 사용되는 값)
      let translateNumber=0;

      function resizeTextarea(){
        let textarea = $('#container-select-form>textarea')[0];
        
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
      }
      
      function updateProgressbar(id,value){
        $('#'+id+' .progress-bar').attr('aria-valuenow',value).css('width',value+'%').text(value+'%');
      }

      function statusUrl(id,url){
        $.ajax({
          url: '/api/v1/status?key=' + url,
          type: 'get',
          success: function (response) {
            console.log(response);

            let value=response.value;
            if(!value || value==-1){
              value=0;
            }
            updateProgressbar(id,value);
            let timeoutId=setTimeout(statusUrl,3000,id,url);
            if (response.value >= 100 || response.value==-1) {
              clearTimeout(timeoutId);
            }
          },
          error: function (request, status, e) {
            console.error(e);
          }
        });
      }
      // URL 번역 시작
      function submitUrl(){
        const url=$('textarea[name="url"]')[0];
        console.log(url.value);

        const article=$('article');
        console.log(article);
        if(isNoVideo){
          article.html('');
          isNoVideo=false;
        }

        // 요소 추가
        let number= ++translateNumber;
        let addTranslate=$('<div>').addClass('translateVideo').attr('id',number)
          .append($('<div class="translateVideoImage">')
            .append($('<img>').attr('src','')))
          .append($('<div class="translateVideoInfo">')
            .append($('<table>')
              .append($('<tr>')
                .append($('<th>').text('원본'))
                .append($('<td>').text(url.value)))
              .append($('<tr>')
                .append($('<th>').text('진행도'))
                .append($('<td>').append($('<div class="progress">)').append(
                  $('<div class="progress-bar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">')
                )))
              )
              .append($('<tr>')
                .append($('<th>').text('동영상'))
                .append($('<td>').addClass('translateInfoVideo').text('동영상을 다운로드하고 있습니다.')))
              .append($('<tr>')
                .append($('<th>').text('자막'))
                .append($('<td>').addClass('translateInfoSubtitle').text('자막 생성 전 입니다.')))))
        article.prepend(addTranslate);

        $.ajax({
          url:'/api/v1/youtube?link='+url.value,
          type:'get',
          xhrFields: {
            responseType: 'blob'
          },
          success: function (data) {
            let videoUrl = URL.createObjectURL(data);
            let videoDownloadButton = $('<button>');

            videoDownloadButton.text('동영상 다운로드');
            videoDownloadButton.click(function () {
              let videoDownloadLink = $('<a>');
              videoDownloadLink.attr('href', videoUrl);
              videoDownloadLink.attr('download', 'video.mp4');
              videoDownloadLink.css('display', 'none');

              $('body').append(videoDownloadLink);
              videoDownloadLink[0].click();
              videoDownloadLink.remove();
            });

            $('#'+number+' .translateInfoVideo').html('동영상을 다운로드하였습니다.\ ').append(videoDownloadButton)

            downloadSubtitle(number,true,url.value);
          },
          error:function(request,status,e){
            console.error(status);
            console.error(e);
            $('#'+number+' .translateInfoVideo').html('<i>동영상을 다운로드하는 중에 오류가 발생했습니다...</i>');
          }
        });

        setTimeout(statusUrl,3000,number,url.value);
      }

      // 영상 파일 번역 시작
      function submitFile(){
        const article = $('article');
        console.log(article);
        if (isNoVideo) {
          article.html('');
          isNoVideo = false;
        }

        // 요소 추가
        let number = ++translateNumber;
        let addTranslate = $('<div>').addClass('translateVideo').attr('id', number)
          .append($('<div class="translateVideoImage">')
            .append($('<img>').attr('src', '')))
          .append($('<div class="translateVideoInfo">')
            .append($('<table>')
              .append($('<tr>')
                .append($('<th>').text('원본'))
                .append($('<td>').text('직접 업로드')))
              /*.append($('<tr>')
                .append($('<th>').text('진행도'))
                .addend($('<td>').append($('<div class="progress">)').append(
                    $('<div class="progress-bar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">')
                  )))*/
              .append($('<tr>')
                .append($('<th>').text('동영상'))
                .append($('<td>').addClass('translateInfoVideo').text('직접 업로드한 동영상은 다운로드 기능이 제공되지 않습니다.')))
              .append($('<tr>')
                .append($('<th>').text('자막'))
                .append($('<td>').addClass('translateInfoSubtitle').text('자막을 생성하고 있습니다.')))));
        article.prepend(addTranslate);
        let file = $('#videoFile')[0].files[0];

        let formData = new FormData();
        formData.append('video', file);

        $.ajax({
          url: '/upload',
          type: 'post',
          processData: false,
          contentType: false,
          data: formData,
          success: function (response) {
            console.log(response);

            let responseJson;
            try{
              responseJson=JSON.parse(response);
            }catch(e){
              console.error(e);
              $('#' + number + ' .translateInfoSubtitle').html('<i>자막을 생성하는 중에 오류가 발생했습니다...</i>');
              return;
            }
            console.log(responseJson);

            downloadSubtitle(number,false,responseJson.hash);
          },
          error:function(request,status,e){
            log.error(status);
            log.error(e);
            $('#'+number+' .translateInfoSubtitle').html('<i>자막을 생성하는 중에 오류가 발생했습니다...</i>');
          }
        });
      }

      // 자막 파일 다운로드
      function downloadSubtitle(id,isUrlVideo,requestParamValue){
        $('#'+id+' .translateInfoSubtitle').html('<strong>자막을 생성하고 있습니다... 잠시만 기다려주세요...</strong>');

        let requestUrl;
        if(isUrlVideo){
          requestUrl= '/api/v1/youtube/subtitle_download?link='+requestParamValue;
        }else{
          requestUrl='/api/v1/upload/subtitle_download?limited_hash='+requestParamValue;
        }

        $.ajax({
          url: requestUrl,
          type: 'get',
          xhrFields: {
            responseType: 'blob'
          },
          success: function (data) {
            let subtitleUrl = URL.createObjectURL(data);
            let subtitleButton = $('<button>');

            subtitleButton.text('자막 다운로드');
            subtitleButton.click(function () {
              let downloadLink = $('<a>');

              downloadLink.attr('href', subtitleUrl);
              downloadLink.attr('download', 'video.srt');
              downloadLink.css('display', 'none');

              $('body').append(downloadLink);
              downloadLink[0].click();
              downloadLink.remove();
              URL.revokeObjectURL(subtitleUrl);
            });

            $('#'+id+' .translateInfoSubtitle').html('자막 생성이 완료되었습니다.&nbsp').append(subtitleButton);
          },
          error: function (xhr, status, error) {
            alert('자막 다운로드 중 오류 발생!\n' + error);
            $('#' + id + ' .translateInfoSubtitle').html('<i>자막 추출 중 오류가 발생했습니다...</i>');
          }
        });
      }

      $(document).ready(function(){
        // 동영상 URL로 번역
        $('#select_url').click(function(){
          $('#container-select-form')
            .html('')
            .append($('<textarea name="url" rows=1>').attr('placeholder','번역할 동영상 URL 입력').on('keyup',function(){ resizeTextarea(); }).on('keydown',function(){ resizeTextarea(); }))
            .append($('<button id="submit" class="btn btn-primary">').text('번역 시작').on('click',function(){ submitUrl(); }));
            
            resizeTextarea();
        });

        // 동영상 업로드로 번역
        $('#select_upload').on('click',function(){
          $('#container-select-form')
            .html('')
            .append($('<input type="file" id="videoFile" name="videoFile" accept=".mp4">'))
            .append($('<button id="submit" class="btn btn-primary">').text('번역 시작').on('click',function(){ submitFile(); }));
        });
      });
    </script>
  </head>
  <body>
    <div class="bcontainer">
      <aside>
        <div class="container-select">
          <button id="select_url" class="btn btn-custom-select">URL</button>
          <button id="select_upload" class="btn btn-custom-select">직접 업로드</button>
        </div>
        <div id="container-select-form">
          <div style="text-align:center;">
            번역할 영상을<br>가져올 방법을<br>선택해주세요.
          </div>
        </div>
      </aside>
      <article>
        <div id="noVideo" style="text-align:center; padding:30px;">
          아직 번역 요청된 동영상이 없습니다...<br>
          좌측에서 번역할 동영상 정보를 입력해주세요.
        </div>
      </article>
    </div>
  </body>
</html>