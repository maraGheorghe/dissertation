import React, { useState, useEffect } from "react";
import { uploadAudioFile } from "../api/upload";
import MediaPlayer from "../components/MediaPlayer";
import Transcript from "../components/Transcripts";
import Subtitle from "../components/Subtitle";
import { getTranscriptById } from "../api/transcript";
import { getSummaryById } from "../api/summary";

type TranscriptData = {
    id: string;
    status: string;
    done: boolean;
    language: string;
    segments: Segment[];
    updated_at: string;
};

type Segment = {
    start: number;
    end: number;
    speaker: string;
    text: string;
};

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [blobUrl, setBlobUrl] = useState<string | undefined>();
    const [currentTime, setCurrentTime] = useState(0);
    const [videoId, setVideoId] = useState<string | undefined>();
    const [showUpload, setShowUpload] = useState(false);
    const [transcriptData, setTranscriptData] = useState<TranscriptData | null>(null);
    const [isTranscriptLoading, setIsTranscriptLoading] = useState(false);
    const [summaryData, setSummaryData] = useState<string | null>(null);
    const [isSummaryLoading, setIsSummaryLoading] = useState(false);

    // Fetch transcript data when videoId changes
    useEffect(() => {
        if (!videoId) return;

        let timeoutId: number;
        setIsTranscriptLoading(true);

        const fetchTranscript = async () => {
            try {
                console.log("Fetching transcript...");
                const data = await getTranscriptById(videoId);
                const transcript = data as TranscriptData;

                setTranscriptData(transcript);

                if (transcript.segments.length > 0) {
                    setIsTranscriptLoading(false);
                }

                if (!transcript.done) {
                    timeoutId = setTimeout(fetchTranscript, 3000);
                }
            } catch (error) {
                timeoutId = setTimeout(fetchTranscript, 5000);
            }
        };

        fetchTranscript();

        return () => clearTimeout(timeoutId);
    }, [videoId]);

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);

        try {
            const blobUrl = URL.createObjectURL(file);
            setBlobUrl(blobUrl);
            const id = await uploadAudioFile(file);
            setVideoId(id);
            setShowUpload(false); // Hide upload section after successful upload
            setLoading(true);
        } catch (err) {
            alert("Error loading the file");
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0] ?? null;
        setFile(selectedFile);
        // Reset previous states when a new file is selected
        setCurrentTime(0);
        setTranscriptData(null);
        setIsTranscriptLoading(false);
    };

    const handleNewFile = () => {
        setCurrentTime(0);
        setTranscriptData(null);
        setIsTranscriptLoading(false);
        setShowUpload(true);
    };

    const handleSummarize = async () => {
        if (!videoId || isSummaryLoading) return;

        setIsSummaryLoading(true);
        let timeoutId: number;

        const fetchSummary = async () => {
            try {
                const data = await getSummaryById(videoId);
                console.log("AAAA");
                console.log(data);
                setSummaryData(data.text);
                setIsSummaryLoading(false);
            } catch (error) {
                console.error("Summary fetch failed:", error);
                timeoutId = setTimeout(fetchSummary, 5000);
            }
        };

        await fetchSummary();
        return () => clearTimeout(timeoutId);
    };

    // If no video is loaded yet, show the upload interface
    if (!blobUrl) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="w-full max-w-2xl mx-auto p-6">
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/30 p-8">
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-6 text-center">
                            Upload Video/Audio File
                        </h1>

                        {/* File Upload Area */}
                        <div className="mb-6">
                            <div className="relative">
                                <input
                                    type="file"
                                    accept="audio/*,video/*,.mkv"
                                    onChange={handleFileChange}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    disabled={loading}
                                />
                                <div
                                    className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
                                        file ? "border-indigo-300 bg-indigo-50" : "border-gray-300 hover:border-indigo-400 hover:bg-gray-50"
                                    } ${loading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                                >
                                    <div className="text-6xl mb-4">{file ? "🎵" : "📁"}</div>
                                    {file ? (
                                        <div>
                                            <p className="text-indigo-600 font-medium text-lg">{file.name}</p>
                                            <p className="text-sm text-gray-500 mt-2">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                                        </div>
                                    ) : (
                                        <div>
                                            <p className="text-gray-600 text-lg mb-2">Click to select a file</p>
                                            <p className="text-sm text-gray-500">Video and audio files supported</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Upload Button */}
                        <button
                            onClick={handleUpload}
                            disabled={!file || loading}
                            className={`w-full py-4 px-6 rounded-xl font-medium text-lg transition-all duration-200 ${
                                !file || loading
                                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                                    : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                            }`}
                        >
                            {loading ? (
                                <div className="flex items-center justify-center gap-3">
                                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-400 border-t-transparent"></div>
                                    Loading...
                                </div>
                            ) : (
                                "Load file"
                            )}
                        </button>

                        {/* Status Messages */}
                        {loading && (
                            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                <div className="flex items-center gap-3">
                                    <div className="animate-pulse w-3 h-3 bg-blue-500 rounded-full"></div>
                                    <p className="text-blue-700 text-sm">Processing your file... This may take a few minutes.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    // Main interface when video is loaded
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            {/* Header with Load New File button */}
            <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-sm border-b border-white/30 shadow-sm">
                <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                       TransLingua
                    </h1>
                    <button
                        onClick={handleNewFile}
                        className="px-4 py-2 bg-white/60 hover:bg-white/80 border border-gray-200 rounded-lg text-gray-600 hover:text-gray-800 transition-all duration-200 text-sm font-medium"
                    >
                        Load New File
                    </button>
                </div>
            </div>

            {/* Main content: video on the left, transcript on the right */}
            <div className="w-full max-w-6xl mx-auto px-6 pt-8 pb-12">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left: player and live subtitles */}
                    <div className="lg:col-span-7">
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/30 p-6 h-full">
                            <MediaPlayer url={blobUrl} onProgress={setCurrentTime} />

                            {(videoId || loading) && (
                                <Subtitle
                                    currentTime={currentTime}
                                    segments={transcriptData?.segments || []}
                                    isLoading={loading ? loading : isTranscriptLoading}
                                />
                            )}
                        </div>
                    </div>

                    {/* Right: transcript (sticky and scrollable on large screens) */}
                    {(videoId || loading) && (
                        <div className="lg:col-span-5">
                            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/30 p-6 h-full lg:sticky lg:top-24 max-h-[calc(100vh-8rem)] overflow-y-auto">
                                <Transcript
                                    currentTime={currentTime}
                                    segments={transcriptData?.segments || []}
                                    isLoading={isTranscriptLoading}
                                    isDone={transcriptData?.done || false}
                                    isSummaryLoading={isSummaryLoading}
                                    onSummarize={handleSummarize}
                                    summaryData={summaryData}
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Upload Modal */}
            {showUpload && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-6">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold text-gray-800">Load New File</h2>
                            <button onClick={() => setShowUpload(false)} className="text-gray-400 hover:text-gray-600 text-xl">
                                ×
                            </button>
                        </div>

                        <div className="mb-6">
                            <div className="relative">
                                <input
                                    type="file"
                                    accept="audio/*,video/*,.mkv"
                                    onChange={handleFileChange}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                />
                                <div
                                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
                                        file ? "border-indigo-300 bg-indigo-50" : "border-gray-300 hover:border-indigo-400 hover:bg-gray-50"
                                    } cursor-pointer`}
                                >
                                    <div className="text-4xl mb-3">{file ? "🎵" : "📁"}</div>
                                    {file ? (
                                        <div>
                                            <p className="text-indigo-600 font-medium">{file.name}</p>
                                            <p className="text-xs text-gray-500 mt-1">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                                        </div>
                                    ) : (
                                        <p className="text-gray-600">Click to select a file</p>
                                    )}
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={handleUpload}
                            disabled={!file || loading}
                            className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
                                !file || loading
                                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                                    : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white"
                            }`}
                        >
                            {loading ? "Processing..." : "Upload File"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}