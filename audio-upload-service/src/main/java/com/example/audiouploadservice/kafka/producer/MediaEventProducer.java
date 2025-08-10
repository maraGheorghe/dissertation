package com.example.audiouploadservice.kafka.producer;

import com.example.audiouploadservice.model.MediaFile;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class MediaEventProducer {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public MediaEventProducer(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void publishUploadEvent(UUID id, String storageKey, LocalDateTime uploadedAt) {
        System.out.println("Hello from here!!");
        System.out.println(kafkaTemplate);
        MediaFile mediaFile = new MediaFile(id, storageKey, null, uploadedAt);
        kafkaTemplate.send("audio-uploaded", mediaFile);
    }
}
