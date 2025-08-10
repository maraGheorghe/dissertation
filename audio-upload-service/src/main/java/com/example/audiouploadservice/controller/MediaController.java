package com.example.audiouploadservice.controller;

import com.example.audiouploadservice.service.MediaStorageService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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

    private final MediaStorageService mediaStorageService;
    private static final Logger log = LoggerFactory.getLogger(MediaController.class);

    public MediaController(MediaStorageService audioStorageService) {
        this.mediaStorageService = audioStorageService;
    }

    @PostMapping("/upload")
    public ResponseEntity<String> uploadMedia(@RequestParam("file") MultipartFile file) {
        log.info("Entered uploadMedia function.");
        UUID fileId = mediaStorageService.storeFile(file);
        log.info("Media uploaded with ID: {}", fileId);
        return ResponseEntity.ok("Audio uploaded with ID: " + fileId);
    }

    @GetMapping("/{id}")
    public ResponseEntity<byte[]> getMediaById(@PathVariable UUID id) {
        log.info("Search the file with the id {}", id);
        var fileByteArrayAndExtension = mediaStorageService.getMediaById(id);
        return ResponseEntity.ok()
                .contentType(MediaType.valueOf(fileByteArrayAndExtension.getSecond().getFileTypeName() + "/" + fileByteArrayAndExtension.getSecond().getFileExtension()))
                .header("Content-Disposition", "attachment; filename=\"" + fileByteArrayAndExtension.getSecond().getOriginalName() + "\"")
                .body(fileByteArrayAndExtension.getFirst());
    }
}
