package be.gyu.whisperAutoSubtitleGenerator;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.servlet.ModelAndView;

@Controller
public class MainController{
  // ===== TEST ===== //
  @GetMapping("/test")
  public String getTestPage(){
    return "test";
  }
  
  @GetMapping("/")
  public String getIndex(){
    return "index";
  }
  
  @GetMapping("/download")
  public String getDownload() {
    return "download";
  }
}