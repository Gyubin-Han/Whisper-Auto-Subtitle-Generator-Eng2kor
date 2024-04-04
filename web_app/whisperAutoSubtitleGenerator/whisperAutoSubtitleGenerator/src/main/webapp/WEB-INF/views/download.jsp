<%@ page language="java" contentType="text/html; charset=utf-8" pageEncoding="utf-8" %>
<%@ taglib prefix="cr" uri="http://java.sun.com/jsp/jstl/core" %>
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    video{
      width:80%;
    }
  </style>
  <script src="/js/jquery-3.7.1.min.js"></script>
  <script>
    $(document).ready(function(){
        <cr:if test="${!empty param.url}">
        // 영상에 대한 처리
        $.ajax({
          url:'/api/v1/youtube?link=${param.url}',   // 추후 변경 필요
          type:'get',
          xhrFields:{
            responseType:'blob'
          },
          success:function(data){
            let videoUrl=URL.createObjectURL(data);
            let videoPlayer=$('<video controls controlsList="nodownload">');
            let videoDownloadButton=$('<button>');
            
            videoPlayer.attr('src',videoUrl);

            videoDownloadButton.text('영상 다운로드');
            videoDownloadButton.click(function(){
              let videoDownloadLink=$('<a>');
              videoDownloadLink.attr('href',videoUrl);
              videoDownloadLink.attr('download','video.mp4');
              videoDownloadLink.css('display','none');

              $('body').append(videoDownloadLink);
              videoDownloadLink[0].click();
              videoDownloadLink.remove();
            });
              
            videoDownloadButton
            $('#videoDownload').html('영상 다운로드가 완료되었습니다.&nbsp').append(videoDownloadButton).append(videoPlayer);

            subtitleRequest();
          },
          error:function(xhr,status,error){
            alert('영상 다운로드 중 오류 발생!\n'+error);
            $('#videoDownload').html('<i>영상 다운로드 중 오류가 발생했습니다...</i>');
            $('#subtitleDownload').html('</i>자막 추출 중 오류가 발생했습니다...</i>');
          }
        });
        </cr:if>
        <cr:if test="${!empty param.limited_hash}">
        subtitleRequest();
        </cr:if>
      });

    // 자막에 대한 처리
    function subtitleRequest(){
      $('#subtitleDownload').html('<strong>자막을 생성하고 있습니다... 잠시만 기다려주세요...</strong>');
      $.ajax({
        <cr:if test="${!empty param.url}"> url: '/api/v1/youtube/subtitle_download?link=${param.url}', </cr:if>
        <cr:if test="${!empty param.limited_hash}"> url: '/api/v1/upload/subtitle_download?limited_hash=${param.limited_hash}', </cr:if>   // 추후 변경 필요
        type: 'get',
        xhrFields: {
          responseType: 'blob'
        },
        success: function (data) {
          let subtitleUrl = URL.createObjectURL(data);
          let subtitleButton = $('<button>');

          subtitleButton.text('자막 파일 다운로드');
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

          $('#subtitleDownload').html('자막 생성이 완료되었습니다.&nbsp').append(subtitleButton);
        },
        error: function (xhr, status, error) {
          alert('자막 다운로드 중 오류 발생!\n' + error);
          $('#subtitleDownload').html('<i>자막 추출 중 오류가 발생했습니다...</i>');
        }
      });
    }
  </script>
</head>
<body>
  동영상 :
  <div id="videoDownload">
    <cr:if test="${!empty param.url}"> <strong>동영상을 다운로드하고 있습니다... 잠시만 기다려 주세요...</strong> </cr:if>
    <cr:if test="${!empty param.limited_hash}"> 동영상을 업로드한 경우, 다운로드 기능은 제공되지 않습니다. </cr:if>
  </div>
  <br>

  자막 :
  <div id="subtitleDownload">
    자막 생성을 준비하고 있습니다...
  </div>
 
</body>
</html>
