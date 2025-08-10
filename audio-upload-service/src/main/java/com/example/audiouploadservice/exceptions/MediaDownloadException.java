package com.example.audiouploadservice.exceptions;

public class MediaDownloadException extends RuntimeException {
    public MediaDownloadException(String message) {
        super(message);
    }

    public MediaDownloadException(String message, Throwable cause) {
        super(message, cause);
    }

}
