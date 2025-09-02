export async function uploadAudioFile(file: File): Promise<string> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`http://192.168.1.22:8081/api/audio/upload`, {
        method: "POST",
        body: formData,
    });

    console.log(res)
    console.log(res.ok)
    if (!res.ok) throw new Error("Upload failed");

    const text = await res.text();
    const id = text.split(" ").pop()?.trim();
    return id!;
}
