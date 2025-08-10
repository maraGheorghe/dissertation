import { useEffect, useRef, useState } from "react";
import {useLocation, useParams} from "react-router-dom";
import { getTranscriptById } from "../api/transcript";
import MediaPlayer from "../components/MediaPlayer";
import {baseURL} from "../api/gateway";

type Segment = {
    start: number;
    end: number;
    speaker: string;
    text: string;
};

interface TranscriptProps {
    currentTime: number
    id: string
}

export default function Transcript({currentTime, id} : TranscriptProps) {
    const [segments, setSegments] = useState<Segment[]>([]);
    const activeSegmentRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        let timeoutId: number;

        const fetchTranscript = async () => {
            try {
                const data = await getTranscriptById(id!);
                setSegments(data);
            } catch (error) {
                timeoutId = setTimeout(fetchTranscript, 2000); // Retry after 2 seconds
            }
        };

        fetchTranscript();

        return () => clearTimeout(timeoutId); // Clean up on unmount
    }, [id]);

    useEffect(() => {
        if (activeSegmentRef.current) {
            activeSegmentRef.current.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
        }
    }, [currentTime]);

    return (
        <div className="p-6 max-w-5xl mx-auto">
            <h1 className="text-3xl font-semibold mb-4 text-gray-800">Transcript</h1>

            <div className="max-h-[70vh] overflow-y-auto pr-2 space-y-3">
                {segments && segments.map((seg, idx) => {
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