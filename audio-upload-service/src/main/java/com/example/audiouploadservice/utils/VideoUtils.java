package com.example.audiouploadservice.utils;
import com.example.audiouploadservice.exceptions.MediaUploadException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;

import org.springframework.web.multipart.MultipartFile;


public class VideoUtils {

    private static final Logger log = LoggerFactory.getLogger(VideoUtils.class);

    public static void convertToAudio(File in, File out) {
       try {
           convertToAudioWithExceptions(in, out);
       } catch (Exception e) {
           throw new MediaUploadException(e.getMessage());
       }
    }
    public static int convertToAudioWithExceptions(File in, File out) throws IOException, InterruptedException {

            List<String> cmd = Arrays.asList(
                    "ffmpeg",
                    "-y",                          // overwrite output if exists
                    "-i", in.getAbsolutePath(),    // input path
                    "-vn",                         // strip video
                    "-acodec", "libmp3lame",       // MP3 encoder
                    "-q:a", "2",                   // VBR quality (~190 kbps)
                    "-preset", "ultrafast",        // Optimize for speed
                    out.getAbsolutePath()          // output path
            );

            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.redirectErrorStream(true);          // merge stderr into stdout for easier logging
            Process p = pb.start();

            log.info("Started ffmpeg process");
            try (BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8))) {
                String line;
                while ((line = r.readLine()) != null) {
                    log.info(line);
                }
            }
            log.info("Finished ffmpeg process");

            int exit = p.waitFor();
            if (exit != 0) {
                log.error("FFmpeg failed with exit code {}", exit);
                throw new MediaUploadException("FFmpeg failed with exit code " + exit);
            }
            return exit;
    }

}
