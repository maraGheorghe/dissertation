package com.example.audiouploadservice.service;

import com.example.audiouploadservice.exceptions.MediaDownloadException;
import com.example.audiouploadservice.exceptions.MediaUploadException;
import com.example.audiouploadservice.exceptions.ServerErrorException;
import com.example.audiouploadservice.kafka.producer.MediaEventProducer;
import com.example.audiouploadservice.model.MediaFile;
import com.example.audiouploadservice.repository.MediaFileRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.util.Pair;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.s3.model.NoSuchKeyException;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.Objects;
import java.util.UUID;

@Service
public class MediaStorageService {
    private static final String AUDIO_FILE_EXTENSION = ".wav";
    private static final String UPLOAD_ERROR_MESSAGE = "Failed to upload audio file!";

    private final MediaFileRepository repository;
    private final S3Client s3Client;
    private final MediaEventProducer mediaEventProducer;

    @Value("${minio.bucket-name}")
    private String minioBucketName;

    public MediaStorageService(
            MediaFileRepository repository,
            S3Client s3Client,
            MediaEventProducer mediaEventProducer
    ) {
        this.repository = repository;
        this.s3Client = s3Client;
        this.mediaEventProducer = mediaEventProducer;
    }

    public UUID storeFile(MultipartFile audioFile) {
        validateAudioFile(audioFile);

        UUID fileId = UUID.randomUUID();
        String storageFileName = generateStorageFileName(fileId, Objects.requireNonNull(audioFile.getOriginalFilename()));
        LocalDateTime uploadTime = LocalDateTime.now();

        uploadToStorage(audioFile, storageFileName);
        saveToDatabase(fileId, audioFile.getOriginalFilename(), uploadTime);
        notifyUploadComplete(fileId, storageFileName, uploadTime);

        return fileId;
    }

    private void validateAudioFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new MediaUploadException("Media file cannot be empty!");
        }
    }

    private String generateStorageFileName(UUID fileId, String originalFilename) {
        String extension = originalFilename.substring(originalFilename.lastIndexOf('.'));
        return fileId + extension;
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
            throw new MediaUploadException(UPLOAD_ERROR_MESSAGE, e);
        }
    }

    private String getFileExtension(String filename) {
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex == -1) {
            throw new MediaUploadException("File must have an extension");
        }
        return filename.substring(lastDotIndex);
    }

    private void saveToDatabase(UUID fileId, String originalFileName, LocalDateTime uploadTime) {
        repository.save(new MediaFile(fileId, originalFileName, getFileExtension(originalFileName), uploadTime));
    }

    private void notifyUploadComplete(UUID fileId, String fileName, LocalDateTime uploadTime) {
        mediaEventProducer.publishUploadEvent(fileId, fileName, uploadTime);
    }

    public Pair<byte[], String> getAudioById(UUID id) {
        var audioFile = repository.findById(id);
        if (audioFile.isEmpty())
            throw new MediaDownloadException("File not found.");
        var fileName = audioFile.get().getId() + audioFile.get().getFileExtension();
        try {
            GetObjectRequest getRequest = GetObjectRequest.builder()
                    .bucket(minioBucketName)
                    .key(fileName)
                    .build();
            ResponseBytes<GetObjectResponse> objectBytes = s3Client.getObjectAsBytes(getRequest);
            return Pair.of(objectBytes.asByteArray(), audioFile.get().getFileExtension());
        } catch (NoSuchKeyException e) {
            throw new MediaDownloadException("File not found.");
        } catch (Exception e) {
            throw new ServerErrorException("Error occurred while downloading the file " + fileName + ".");
        }
    }
}