import { baseURL} from "./gateway";

export async function getTranscriptById(id: string) {
    const res = await fetch(`http://localhost:8082/api/transcript/${id}`);
    if (!res.ok) throw new Error("Transcript fetch failed");
    return res.json();
}