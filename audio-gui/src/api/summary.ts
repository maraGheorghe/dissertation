export const getSummaryById = async (id: string) => {
    const response = await fetch(`http://localhost:8082/api/summary/${id}`);
    if (!response.ok) {
        throw new Error('Failed to fetch summary');
    }
    return response.json();
};