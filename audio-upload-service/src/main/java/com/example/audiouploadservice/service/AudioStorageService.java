package com.example.audiouploadservice.service;

import com.example.audiouploadservice.kafka.producer.AudioEventProducer;
import com.example.audiouploadservice.model.AudioFile;
import com.example.audiouploadservice.repository.AudioFileRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class AudioStorageService {
    private static final String AUDIO_FILE_EXTENSION = ".wav";
    private static final String UPLOAD_ERROR_MESSAGE = "Failed to upload audio file!";

    private final AudioFileRepository repository;
    private final S3Client s3Client;
    private final AudioEventProducer audioEventProducer;

    @Value("${minio.bucket-name}")
    private String minioBucketName;

    public AudioStorageService(
            AudioFileRepository repository,
            S3Client s3Client,
            AudioEventProducer audioEventProducer
    ) {
        this.repository = repository;
        this.s3Client = s3Client;
        this.audioEventProducer = audioEventProducer;
    }

    public UUID storeFile(MultipartFile audioFile) {
        validateAudioFile(audioFile);

        UUID fileId = UUID.randomUUID();
        String storageFileName = generateStorageFileName(fileId);
        LocalDateTime uploadTime = LocalDateTime.now();

        uploadToStorage(audioFile, storageFileName);
        saveToDatabase(fileId, audioFile.getOriginalFilename(), uploadTime);
        notifyUploadComplete(fileId, storageFileName, uploadTime);

        return fileId;
    }

    private void validateAudioFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new AudioUploadException("Audio file cannot be empty!");
        }
    }

    private String generateStorageFileName(UUID fileId) {
        return fileId + AUDIO_FILE_EXTENSION;
    }

    private void uploadToStorage(MultipartFile file, String fileName) {
        try {
            PutObjectRequest request = PutObjectRequest.builder()
                    .bucket(minioBucketName)
                    .key(fileName)
                    .contentType(file.getContentType())
                    .build();

            s3Client.putObject(request, RequestBody.fromBytes(file.getBytes()));
        } catch (IOException e) {
            throw new AudioUploadException(UPLOAD_ERROR_MESSAGE, e);
        }
    }

    private void saveToDatabase(UUID fileId, String originalFileName, LocalDateTime uploadTime) {
        repository.save(new AudioFile(fileId, originalFileName, uploadTime));
    }

    private void notifyUploadComplete(UUID fileId, String fileName, LocalDateTime uploadTime) {
        audioEventProducer.publishUploadEvent(fileId, fileName, uploadTime);
    }

    public static class AudioUploadException extends RuntimeException {
        public AudioUploadException(String message) {
            super(message);
        }

        public AudioUploadException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
