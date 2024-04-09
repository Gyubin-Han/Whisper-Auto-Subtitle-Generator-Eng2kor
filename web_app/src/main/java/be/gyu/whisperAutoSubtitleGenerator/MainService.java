package be.gyu.whisperAutoSubtitleGenerator;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

@Service("main")
public class MainService {
  private final String videoFilePath="./saveVideo/";
  private final String API_SERVER_URL="https://tools.gyu.be/api/v1/upload";

  // 사용자 업로드 동영상 처리
  public String videoUpload(MultipartFile file){
    System.out.println(file.getOriginalFilename());
    RestTemplate restTemplate=new RestTemplate();
    
    HttpHeaders header=new HttpHeaders();
    header.setContentType(MediaType.MULTIPART_FORM_DATA);

    MultiValueMap<String, Object> body=new LinkedMultiValueMap<>();
    body.add("video",file.getResource());

    HttpEntity<MultiValueMap<String,Object>> requestEntity=new HttpEntity<>(body,header);
    String response=null;
    try{
      response=restTemplate.postForObject(API_SERVER_URL,requestEntity,String.class);

      System.out.println("응답 값(JSON) : "+response);
    }catch(Exception e){
      e.printStackTrace();
    }

    return response;
    // return videoRequestApiServer(file.get)
  }

  // URL 다운로드 동영상 or 사용자 업로드 동영상 -> API 서버 전송
  public String videoRequestApiServer(File file){
    return "";
  }
}
