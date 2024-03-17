<%@ page language="java" contentType="text/html; charset=utf-8" pageEncoding="utf-8" %>
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    input, button{
      padding:10px;
    }
    input[type="text"]{
      width:250px;
    }
  </style>
  <script src="/js/jquery-3.7.1.min.js"></script>
  <script>
    $(document).ready(function(){
      $('#submit').click(function(){
        let inputUrl=$('#videoLink').val();

        // if(/^(!?http|https):\/\//.test(inputUrl)){
        //   alert("입력하신 값이 URL이 아닙니다. 올바른 URL을 입력해주세요.");
        // }else{
        //   alert(inputUrl);
        // }

        // 전송 폼 생성
        let form=$('<form>');
        form.attr('action','/download').attr('method','get');
        form.append($('<input>').attr('type','hidden').attr('name','url').val(inputUrl));

        $('body').append(form);
        console.log(form);
        form.submit();
      });
    });
  </script>
</head>
<body>
  <input type="text" id="videoLink" name="video_link" placeholder="번역할 YouTube 주소를 입력해주세요" required>
  <button id="submit">번역 시작</button>
</body>
</html>