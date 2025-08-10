import { useState } from "react";
import { uploadAudioFile } from "../api/upload";
import { useNavigate } from "react-router-dom";
import {useBlobStore} from "../stores/blobStore";
import MediaPlayer from "../components/MediaPlayer";
import Transcript from "../components/Transcripts";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [blobUrl, setBlobUrl] = useState<string | undefined>();
    const [currentTime, setCurrentTime] = useState(0);
    const [videoId, setVideoId] = useState<string | undefined>();
    const navigate = useNavigate();

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);

        try {
            const blobUrl = URL.createObjectURL(file);
            setBlobUrl(blobUrl)
            const id = await uploadAudioFile(file);
            setVideoId(id)
        } catch (err) {
            alert("Eroare la încărcare fișier");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 max-w-xl mx-auto">
            <h1 className="text-2xl font-bold mb-4">Încarcă un fișier audio</h1>

            <input
                type="file"
                accept="audio/*,video/*,.mkv"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="mb-4"
            />

            <button
                onClick={handleUpload}
                disabled={!file || loading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50"
            >
                {loading ? "Se încarcă..." : "Încarcă"}
            </button>

            {blobUrl && (
                <div className="mt-4 space-y-4">
                    <MediaPlayer url={blobUrl} onProgress={setCurrentTime}/>
                </div>
            )}

            {videoId && (
                <Transcript currentTime={currentTime} id={videoId}/>
            )}
        </div>
    );
}
