import { create } from 'zustand';

type BlobStore = {
    blobMap: Record<string, string>;
    setBlobUrl: (id: string, url: string) => void;
    getBlobUrl: (id: string) => string | undefined;
    clearBlobUrl: (id: string) => void;
};

export const useBlobStore = create<BlobStore>((set, get) => ({
    blobMap: {},

    setBlobUrl: (id, url) =>
        set((state) => ({
            blobMap: {
                ...state.blobMap,
                [id]: url,
            },
        })),

    getBlobUrl: (id) => get().blobMap[id],

    clearBlobUrl: (id) =>
        set((state) => {
            const { [id]: _, ...rest } = state.blobMap;
            return { blobMap: rest };
        }),
}));
