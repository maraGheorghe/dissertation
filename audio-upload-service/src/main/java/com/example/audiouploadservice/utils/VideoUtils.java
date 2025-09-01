package com.example.audiouploadservice.utils;
import com.example.audiouploadservice.exceptions.MediaUploadException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.charset.StandardCharsets;

import java.util.Arrays;
import java.util.List;


public class VideoUtils {

    private static final Logger log = LoggerFactory.getLogger(VideoUtils.class);

    public static void convertToAudio(File in, File out) {
       try {
           convertToAudioWithExceptions(in, out);
       } catch (Exception e) {
           throw new MediaUploadException(e.getMessage());
       }
    }
    public static void convertToAudioWithExceptions(File in, File out) throws IOException, InterruptedException {
            List<String> cmd = Arrays.asList(
                    "ffmpeg",
                    "-y",
                    "-i", in.getAbsolutePath(),
                    "-vn",
                    "-acodec", "libmp3lame",
                    "-q:a", "2",
                    "-preset", "ultrafast",
                    out.getAbsolutePath()
            );
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.redirectErrorStream(true);
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
    }

}
