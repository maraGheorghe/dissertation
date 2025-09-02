type Segment = {
    start: number;
    end: number;
    speaker: string;
    text: string;
};

interface SubtitleProps {
    currentTime: number;
    segments: Segment[];
    isLoading: boolean;
}

export default function Subtitle({ currentTime, segments, isLoading }: SubtitleProps) {
    const getCurrentSegment = () => {
        return segments.find(seg => currentTime >= seg.start && currentTime <= seg.end);
    };

    const currentSegment = getCurrentSegment();

    if (isLoading) {
        return (
            <div className="mt-4 py-8 px-6 bg-black/80 backdrop-blur-sm rounded-lg text-center">
                <div className="flex items-center justify-center gap-2 text-white/70">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white/70"></div>
                    <span className="text-sm">Loading subtitles...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="mt-4 min-h-[80px] flex items-center justify-center">
            <div className="py-4 px-6 backdrop-blur-sm rounded-lg shadow-lg max-w-4xl w-full">
                {currentSegment ? (
                    <p className="text-black text-lg font-medium text-center leading-relaxed">
                        {currentSegment.text}
                    </p>
                ) : (
                    <p className="text-white/50 text-center text-sm italic">
                        {segments.length > 0 ? "..." : "No subtitles available"}
                    </p>
                )}
            </div>
        </div>
    );
}