package com.example.audiouploadservice.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "audio_file")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AudioFile {

    @Id
    private UUID id;

    private String originalName;
    private LocalDateTime uploadTime;
}
