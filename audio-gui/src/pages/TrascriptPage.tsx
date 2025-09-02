import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { getTranscriptById } from "../api/transcript";
import MediaPlayer from "../components/MediaPlayer";
import { useBlobStore } from "../stores/blobStore";

type Segment = {
    start: number;
    end: number;
    speaker: string;
    text: string;
};

export default function TranscriptPage() {
    const { id } = useParams();
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [segments, setSegments] = useState<Segment[]>([]);
    const [currentTime, setCurrentTime] = useState(0);
    const [audioUrl, setAudioUrl] = useState("");
    const blobUrlRef = useRef<string | undefined>(undefined);
    const activeSegmentRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        getTranscriptById(id!).then(setSegments);
    }, [id]);


    useEffect(() => {
        if (!blobUrlRef.current) {
            blobUrlRef.current = useBlobStore.getState().getBlobUrl(id!);
            console.log("Entered here where the url is: ", blobUrlRef.current)
        }

        const finalUrl = blobUrlRef.current || `http://localhost:8081/api/audio/${id}`;
        setAudioUrl(finalUrl);

    }, [id]);


    // Track audio time
    useEffect(() => {
        const interval = setInterval(() => {
            if (audioRef.current) {
                setCurrentTime(audioRef.current.currentTime);
            }
        }, 100);
        return () => clearInterval(interval);
    }, []);

    // Auto-scroll to active segment
    useEffect(() => {
        if (activeSegmentRef.current) {
            activeSegmentRef.current.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
        }
    }, [currentTime]);

    console.log(`http://localhost:8081/api/audio/${id}`)
    return (
        <div className="p-6 max-w-5xl mx-auto">
            <h1 className="text-3xl font-semibold mb-4 text-gray-800">Transcript</h1>

            <MediaPlayer
                url={audioUrl}
                onProgress={(seconds) => {
                       setCurrentTime(seconds)
                }}
            />

            <div className="max-h-[70vh] overflow-y-auto pr-2 space-y-3">
            {segments.map((seg, idx) => {
                    const isActive = currentTime >= seg.start && currentTime <= seg.end;

                    return (
                        <div
                            key={idx}
                            ref={isActive ? activeSegmentRef : null}
                            className={`transition-all p-3 rounded-md border shadow-sm ${
                                isActive
                                    ? "bg-blue-50 border-blue-300 font-semibold"
                                    : "bg-white"
                            }`}
                        >
                            <div className="text-sm text-gray-500 mb-1">
                                {seg.speaker !== "unknown" ? `🗣 ${seg.speaker}` : "🗣 Vorbitor"}
                                <span className="ml-2 text-xs text-gray-400">
                  ({seg.start.toFixed(1)}s – {seg.end.toFixed(1)}s)
                </span>
                            </div>
                            <p>{seg.text}</p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}