import { useEffect, useState } from "react";

type Segment = {
    start: number;
    end: number;
    speaker: string;
    text: string;
};

interface TranscriptProps {
    currentTime: number;
    segments: Segment[];
    isLoading: boolean;
    isDone: boolean;
    summaryData: string | null;
    isSummaryLoading: boolean;
    onSummarize: () => void;
}

export default function Transcript({ currentTime, segments, isLoading, isDone, summaryData, isSummaryLoading, onSummarize }: TranscriptProps) {
    const [activeTab, setActiveTab] = useState<'transcript' | 'summary'>('transcript');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [format, setFormat] = useState<'txt' | 'sub'>('txt');

    useEffect(() => {
        if (activeTab === 'summary' && !summaryData && !isSummaryLoading) {
            onSummarize();
        }
    }, [activeTab]);

    const isVideoAheadOfTranscript = () => {
        if (segments.length === 0) return false;
        const lastSegment = segments[segments.length - 1];
        return currentTime > lastSegment.end && !isDone;
    };

    const downloadTranscript = () => {
        let transcriptContent = "";

        if (format === "txt") {
            transcriptContent = segments
                .map(segment => `[${segment.start} - ${segment.end}]: ${segment.text}`)
                .join("\n");
        } else if (format === "sub") {
            transcriptContent = segments
                .map((segment, index) => {
                    const start = new Date(segment.start * 1000).toISOString().substr(11, 12).replace(".", ",");
                    const end = new Date(segment.end * 1000).toISOString().substr(11, 12).replace(".", ",");
                    return `${index + 1}\n${start} --> ${end}\n${segment.text}\n`;
                })
                .join("\n");
        }

        const blob = new Blob([transcriptContent], { type: "text/plain" });
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.download = `transcript.${format}`;
        link.click();

        URL.revokeObjectURL(url); // Clean up the object URL
        setIsModalOpen(false); // Close modal after download
    };

    if (isLoading) {
        return (
            <div className="mt-8 w-full max-w-4xl mx-auto">
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/30 p-8">
                    <div className="flex flex-col items-center justify-center space-y-4">
                        <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent"></div>
                        <h3 className="text-xl font-semibold text-gray-700">Processing transcript...</h3>
                        <p className="text-gray-500 text-center">
                            We're analyzing your audio and generating the transcript. This may take a few minutes.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    if (segments.length === 0) {
        return (
            <div className="mt-8 w-full max-w-4xl mx-auto">
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/30 p-8">
                    <div className="text-center">
                        <div className="text-4xl mb-4">🎵</div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2">No transcript available</h3>
                        <p className="text-gray-500">The transcript is still being processed or no speech was detected.</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <>
            <div className="p-2 relative transcript-container">
                <div className="flex justify-between items-end mb-6 border-b border-gray-200">
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-all mb-2"
                    >
                        Download
                    </button>

                    <div className="flex gap-4">
                        <button
                            onClick={() => setActiveTab('transcript')}
                            className={`pb-3 px-1 font-medium transition-colors ${
                                activeTab === 'transcript'
                                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                                    : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            Transcript
                        </button>
                        <button
                            onClick={() => setActiveTab('summary')}
                            className={`pb-3 px-1 font-medium transition-colors relative ${
                                activeTab === 'summary'
                                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                                    : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            Summary
                            {isSummaryLoading && (
                                <div className="absolute -right-6 top-0">
                                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-indigo-500 border-t-transparent"></div>
                                </div>
                            )}
                        </button>
                    </div>
                </div>

                {activeTab === 'transcript' && (
                    <div>
                        {isVideoAheadOfTranscript() && (
                            <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                                <div className="flex items-center gap-3">
                                    <div className="animate-pulse w-3 h-3 bg-amber-500 rounded-full"></div>
                                    <p className="text-amber-700 text-sm">
                                        The transcript is still being generated for this part of the audio...
                                    </p>
                                </div>
                            </div>
                        )}
                        <div className="text-lg leading-relaxed text-gray-800 space-y-1">
                            {segments.map((segment, segmentIndex) => {
                                const isActive = currentTime >= segment.start && currentTime <= segment.end;

                                return (
                                    <span
                                        key={segmentIndex}
                                        className={`inline transition-all duration-300 ${
                                            isActive
                                                ? "font-bold text-indigo-900 bg-indigo-100 px-1 py-0.5 rounded"
                                                : "text-gray-700"
                                        }`}
                                    >
                                        {segment.text}
                                        {segmentIndex < segments.length - 1 && " "}
                                    </span>
                                );
                            })}
                        </div>

                        {!isDone && (
                            <div className="mt-6 pt-4 border-t border-gray-200">
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <div className="animate-pulse w-2 h-2 bg-indigo-500 rounded-full"></div>
                                    <span>Transcript is still being processed...</span>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'summary' && (
                    <div>
                        {summaryData && (
                            <div
                                className="prose prose-lg max-w-none markup-content"
                                dangerouslySetInnerHTML={{
                                    __html: summaryData
                                        .replace(/\n/g, '<br>')
                                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                                        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
                                        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                                        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                                        .replace(/^- (.*$)/gm, '<ul><li>$1</li></ul>')
                                        .replace(/^\d+\. (.*$)/gm, '<ol><li>$1</li></ol>')
                                        .replace(/<\/ul>\s*<ul>/g, '')
                                        .replace(/<\/ol>\s*<ol>/g, '')
                                }}
                            />
                        )}
                    </div>
                )}
            </div>

            {/* Modal for selecting file format */}
            {isModalOpen && (
                <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                    <div
                        className="bg-white rounded-2xl p-8 max-w-md w-full mx-auto max-h-[90vh] overflow-y-auto"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Modal Header */}
                        <h2 className="text-xl font-semibold mb-6 text-center">Select Download Format</h2>

                        {/* Modal Body */}
                        <div className="flex flex-col gap-4">
                            <label className="flex items-center cursor-pointer">
                                <input
                                    type="radio"
                                    name="format"
                                    value="txt"
                                    checked={format === "txt"}
                                    onChange={(e) => setFormat(e.target.value as 'txt' | 'sub')}
                                    className="mr-3"
                                />
                                <div>
                                    <div className="font-medium">TXT</div>
                                    <div className="text-sm text-gray-500">Plain text format with timestamps</div>
                                </div>
                            </label>
                            <label className="flex items-center cursor-pointer">
                                <input
                                    type="radio"
                                    name="format"
                                    value="sub"
                                    checked={format === "sub"}
                                    onChange={(e) => setFormat(e.target.value as 'txt' | 'sub')}
                                    className="mr-3"
                                />
                                <div>
                                    <div className="font-medium">SUB</div>
                                    <div className="text-sm text-gray-500">Subtitle format for video players</div>
                                </div>
                            </label>
                        </div>

                        {/* Modal Footer */}
                        <div className="mt-8 flex justify-between">
                            <button
                                onClick={() => setIsModalOpen(false)}
                                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={downloadTranscript}
                                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
                            >
                                Download
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}