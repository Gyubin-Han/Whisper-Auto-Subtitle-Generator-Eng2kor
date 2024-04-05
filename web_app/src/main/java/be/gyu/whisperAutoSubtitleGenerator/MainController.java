package be.gyu.whisperAutoSubtitleGenerator;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.ModelAndView;

import jakarta.servlet.http.HttpServletRequest;

@Controller
public class MainController{
  @Autowired
  MainService service;

  @GetMapping("/")
  public String getIndex(){
    return "index";
  }

  @PostMapping("/upload")
  @ResponseBody
  public String sendVideo(@RequestParam("video") MultipartFile file){
    return service.videoUpload(file);
  }
  
  @GetMapping("/download")
  public String getDownload(HttpServletRequest request) {
    if(request.getParameter("url")!=null){
      System.out.println("다운로드 요청(유튜브) : "+request.getParameter("url"));
    }else{
      System.out.println("다운로드 요청(업로드) : "+request.getParameter("limited_hash"));
    }

    return "download";
  }
}