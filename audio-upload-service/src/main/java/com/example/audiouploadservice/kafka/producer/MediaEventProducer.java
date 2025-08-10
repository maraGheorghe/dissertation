package com.example.audiouploadservice.kafka.producer;

import com.example.audiouploadservice.model.MediaFile;
import com.example.audiouploadservice.utils.VideoUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class MediaEventProducer {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private static final Logger log = LoggerFactory.getLogger(VideoUtils.class);

    public MediaEventProducer(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void publishUploadEvent(UUID id, String storageKey, LocalDateTime uploadedAt) {
        log.info("Sending media upload event for file with id: {}", id);
        MediaFile mediaFile = new MediaFile(id, storageKey, null, null, null, null, uploadedAt);
        kafkaTemplate.send("audio-uploaded", mediaFile);
    }
}
