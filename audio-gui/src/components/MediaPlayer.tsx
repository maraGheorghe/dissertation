import React, { useRef, useState } from "react"
import ReactPlayer from "react-player"

interface MediaPlayerProps {
    url: string
    onProgress: (seconds: number) => void
}

export default function MediaPlayer({ url, onProgress }: MediaPlayerProps) {
    const [isReady, setIsReady] = useState(false)
    const [playing, setIsPlaying] = useState(false)

    return (
        <div className="w-full max-w-3xl mx-auto mb-6 shadow-md rounded overflow-hidden">
            <ReactPlayer
                src={url}
                playing={playing}
                controls
                width="100%"
                height="auto"
                onReady={() => setIsReady(true)}
                onTimeUpdate={(video) => {
                    onProgress(video.currentTarget.currentTime)
                    setIsPlaying(playing)
                    }
                }
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={() => setIsPlaying(false)}
            />
        </div>
    )
}
