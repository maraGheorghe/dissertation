package com.example.audiouploadservice.controller;

import com.example.audiouploadservice.exceptions.MediaDownloadException;
import com.example.audiouploadservice.exceptions.MediaUploadException;
import com.example.audiouploadservice.exceptions.ServerErrorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.multipart.MultipartException;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.http.ResponseEntity;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(MultipartException.class)
    public ResponseEntity<String> handleMultipartException(MultipartException ex) {
        log.error("Multipart exception occurred: {}", ex.getMessage(), ex);
        return ResponseEntity
                .badRequest()
                .body("The request must be multipart/form-data and contain an audio file.");
    }

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<String> handleMaxSizeException(MaxUploadSizeExceededException ex) {
        log.error("Max upload size exceeded: {}", ex.getMessage(), ex);
        return ResponseEntity
                .badRequest()
                .body("The uploaded file is too large. Please upload a smaller audio file.");
    }

    @ExceptionHandler(MediaDownloadException.class)
    public ResponseEntity<String> handleMediaDownloadException(MediaDownloadException ex) {
        log.error("Media download exception: {}", ex.getMessage(), ex);
        return ResponseEntity
                .notFound()
                .build();
    }

    @ExceptionHandler(MediaUploadException.class)
    public ResponseEntity<String> handleMediaUploadException(MediaUploadException ex) {
        log.error("Media upload exception: {}", ex.getMessage(), ex);
        return ResponseEntity
                .badRequest()
                .body("Something went wrong with the media upload.");
    }

    @ExceptionHandler(ServerErrorException.class)
    public ResponseEntity<String> handleServerErrorException(ServerErrorException ex) {
        log.error("Server error exception occurred: {}", ex.getMessage(), ex);
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("An unexpected error occurred.");
    }
}