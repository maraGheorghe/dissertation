package com.example.audiouploadservice.repository;

import com.example.audiouploadservice.model.MediaFile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface MediaFileRepository extends JpaRepository<MediaFile, UUID> {}

