package com.example.audiouploadservice.kafka.producer;

import com.example.audiouploadservice.model.AudioFile;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class AudioEventProducer {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public AudioEventProducer(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void publishUploadEvent(UUID id, String storageKey, LocalDateTime uploadedAt) {
        AudioFile audioFile = new AudioFile(id, storageKey, uploadedAt);
        kafkaTemplate.send("audio-uploaded", audioFile);
    }
}

