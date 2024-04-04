package be.gyu.whisperAutoSubtitleGenerator;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class WhisperAutoSubtitleGeneratorApplication {

	public static void main(String[] args) {
		SpringApplication.run(WhisperAutoSubtitleGeneratorApplication.class, args);
		System.out.println("서버 시작됨.");
	}

}
