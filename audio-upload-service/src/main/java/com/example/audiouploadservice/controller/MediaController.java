package com.example.audiouploadservice.controller;

import com.example.audiouploadservice.exceptions.MediaDownloadException;
import com.example.audiouploadservice.exceptions.ServerErrorException;
import com.example.audiouploadservice.service.MediaStorageService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;

@CrossOrigin(
        origins = "http://localhost:5173",
        allowedHeaders = "*",
        methods = {RequestMethod.POST, RequestMethod.GET, RequestMethod.OPTIONS}
)
@RestController
@RequestMapping("/api/audio")
public class MediaController {

    private final MediaStorageService audioStorageService;
    private static final Logger log = LoggerFactory.getLogger(MediaController.class);

    public MediaController(MediaStorageService audioStorageService) {
        this.audioStorageService = audioStorageService;
    }

    @PostMapping("/upload")
    public ResponseEntity<String> uploadMedia(@RequestParam("file") MultipartFile file) {
        log.info("Entered uploadMedia function.");
        UUID fileId = audioStorageService.storeFile(file);
        log.info("Media uploaded with ID: {}", fileId);
        return ResponseEntity.ok("Audio uploaded with ID: " + fileId);
    }

    @GetMapping("/{id}")
    public ResponseEntity<byte[]> getMediaById(@PathVariable UUID id) {
        log.info("Search the file with the id {}", id);
        var fileByteArrayAndExtension = audioStorageService.getAudioById(id);
        var fileType = List.of("wav", "mp3", "m4a").contains(fileByteArrayAndExtension.getSecond()) ? "audio" : "video";
        return ResponseEntity.ok()
                .contentType(MediaType.valueOf(fileType + "/" + fileByteArrayAndExtension.getSecond()))
                .body(fileByteArrayAndExtension.getFirst());
    }
}
