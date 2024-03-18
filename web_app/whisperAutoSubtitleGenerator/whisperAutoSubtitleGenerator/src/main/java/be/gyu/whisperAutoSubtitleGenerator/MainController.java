package be.gyu.whisperAutoSubtitleGenerator;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.servlet.ModelAndView;

import jakarta.servlet.http.HttpServletRequest;

@Controller
public class MainController{
  @GetMapping("/")
  public String getIndex(){
    return "index";
  }
  
  @GetMapping("/download")
  public String getDownload(HttpServletRequest request) {
    System.out.println("영상 요청 : "+request.getParameter("url"));
    return "download";
  }
}