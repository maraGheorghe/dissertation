package com.example.audiouploadservice.controller;

import com.example.audiouploadservice.service.AudioStorageService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;

@CrossOrigin
@RestController
@RequestMapping("/api/audio")
public class AudioController {

    private final AudioStorageService audioStorageService;

    public AudioController(AudioStorageService audioStorageService) {
        this.audioStorageService = audioStorageService;
    }

    @PostMapping("/upload")
    public ResponseEntity<String> uploadAudio(@RequestParam("file") MultipartFile file) {
        UUID fileId = audioStorageService.storeFile(file);
        return ResponseEntity.ok("Audio uploaded with ID: " + fileId);
    }
}
