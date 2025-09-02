package com.example.audiouploadservice.service;

import com.example.audiouploadservice.exceptions.MediaDownloadException;
import com.example.audiouploadservice.exceptions.MediaUploadException;
import com.example.audiouploadservice.exceptions.ServerErrorException;
import com.example.audiouploadservice.kafka.producer.MediaEventProducer;
import com.example.audiouploadservice.model.MediaFile;
import com.example.audiouploadservice.repository.MediaFileRepository;
import com.example.audiouploadservice.utils.VideoUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

@Service
public class MediaStorageService {
    private static final String UPLOAD_ERROR_MESSAGE = "Failed to upload audio file!";
    private static final Set<String> VIDEO_FILE_EXTENSIONS = Set.of(".mp4", ".mov", ".avi", ".wmv", ".webm", ".flv", ".mkv");

    private static final Logger log = LoggerFactory.getLogger(MediaStorageService.class);

    private final MediaFileRepository repository;
    private final S3Client s3Client;
    private final MediaEventProducer mediaEventProducer;

    @Value("${minio.bucket-name}")
    private String minioBucketName;

    @Value("${resources-folder}")
    private String resourcesFolder;

    public MediaStorageService(
            MediaFileRepository repository,
            S3Client s3Client,
            MediaEventProducer mediaEventProducer
    ) {
        this.repository = repository;
        this.s3Client = s3Client;
        this.mediaEventProducer = mediaEventProducer;
    }

    public UUID storeFile(MultipartFile mediaMultipartFile) {
        validateAudioFile(mediaMultipartFile);
        if (Objects.isNull(mediaMultipartFile.getOriginalFilename())) {
            log.error("File name cannot be null!");
            throw new MediaUploadException("File name cannot be null!");
        }
        if (isVideoFile(mediaMultipartFile.getOriginalFilename())) {
            return handleVideoFile(mediaMultipartFile);
        }
        return handleAudioFile(mediaMultipartFile);
    }

    private UUID handleVideoFile(MultipartFile mediaMultipartFile) {
        log.info("Entered handleVideoFile function.");
        UUID fileId = UUID.randomUUID();
        // save video locally
        var videoFileName = generateStorageVideoFileName(fileId, mediaMultipartFile.getOriginalFilename());
        var videoLocalFileName = String.format("%s/%s", resourcesFolder, videoFileName);
        saveVideo(mediaMultipartFile, videoLocalFileName);
        var videoFile = new File(videoLocalFileName);
        // convert video to audio and save it locally
        var audioFileName = generateMp3StorageFileName(fileId);
        var audioLocalFileName = String.format("%s/%s", resourcesFolder, audioFileName);
        var audioFile = new File(audioLocalFileName);
        VideoUtils.convertToAudio(videoFile, audioFile);
        // upload the audio file to s3
        uploadToStorage(audioFile);
        // notify kafka processor that the file was uploaded
        notifyUploadComplete(fileId, audioFileName, LocalDateTime.now());
        // save the file metadata to the database
        saveToDatabase(fileId, mediaMultipartFile.getOriginalFilename(), "video", videoLocalFileName, videoFileName, LocalDateTime.now());
        // upload the video to the storage also
        uploadToStorage(videoFile);
        log.info("Video uploaded with ID: {}", fileId);
        return fileId;
    }

    private UUID handleAudioFile(MultipartFile mediaMultipartFile) {
        log.info("Entered handleAudioFile function.");
        UUID fileId = UUID.randomUUID();
        var audioFileName = generateAudioStorageFileName(fileId, mediaMultipartFile.getOriginalFilename());
        //upload in MinIO
        uploadToStorage(mediaMultipartFile, audioFileName);
        //notify kafka
        notifyUploadComplete(fileId, audioFileName, LocalDateTime.now());
        // save the audio file locally + db
        var audioLocalFileName = String.format("%s/%s", resourcesFolder, audioFileName);
        var audioFile = new File(audioLocalFileName);
        try {
            mediaMultipartFile.transferTo(audioFile);
            saveToDatabase(fileId, mediaMultipartFile.getOriginalFilename(), "audio", audioLocalFileName, audioFileName, LocalDateTime.now());
        } catch (IOException e) {
            log.error("Error while trying to save the audio file locally: ", e);
        }
        return fileId;
    }

    private boolean isVideoFile(String fileName) {
        String extension = fileName.substring(fileName.lastIndexOf('.'));
        return VIDEO_FILE_EXTENSIONS.contains(extension);
    }

    private void validateAudioFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new MediaUploadException("Media file cannot be empty!");
        }
    }

    private String generateStorageVideoFileName(UUID fileId, String originalFilename) {
        String extension = originalFilename.substring(originalFilename.lastIndexOf('.'));
        return fileId + "-video" + extension;
    }

    private String generateAudioStorageFileName(UUID fileId, String originalFilename) {
        String extension = originalFilename.substring(originalFilename.lastIndexOf('.'));
        return fileId + "-audio" + extension;
    }

    private String generateMp3StorageFileName(UUID fileId) {
        return fileId + "-audio" + ".mp3";
    }

    private void saveVideo(MultipartFile multipartFile, String fileName) {
        try {
            multipartFile.transferTo(new File(fileName));
        } catch (Exception e) {
            log.error(e.getMessage());
        }
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

    private void uploadToStorage(File file) {
        try {
            PutObjectRequest request = PutObjectRequest.builder()
                    .bucket(minioBucketName)
                    .key(file.getName())
                    .contentType(file.getName())
                    .build();
            s3Client.putObject(request, RequestBody.fromFile(file));
        } catch (Exception e) {
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

    private void saveToDatabase(UUID fileId, String originalFileName, String fileType, String filePath, String storageKey, LocalDateTime uploadTime) {
        repository.save(new MediaFile(fileId, originalFileName, getFileExtension(originalFileName), fileType, filePath, storageKey, uploadTime));
    }

    private void notifyUploadComplete(UUID fileId, String fileName, LocalDateTime uploadTime) {
        mediaEventProducer.publishUploadEvent(fileId, fileName, uploadTime);
    }

    public Pair<byte[], MediaFile> getMediaById(UUID id) {
        var audioFile = repository.findById(id);
        if (audioFile.isEmpty())
            throw new MediaDownloadException("File not found.");
        try {
            GetObjectRequest getRequest = GetObjectRequest.builder()
                    .bucket(minioBucketName)
                    .key(audioFile.get().getStorageKey())
                    .build();
            ResponseBytes<GetObjectResponse> objectBytes = s3Client.getObjectAsBytes(getRequest);
            return Pair.of(objectBytes.asByteArray(), audioFile.get());
        } catch (NoSuchKeyException e) {
            throw new MediaDownloadException("File not found.");
        } catch (Exception e) {
            throw new ServerErrorException("Error occurred while downloading the file " + audioFile.get().getStorageKey() + ".");
        }
    }
}