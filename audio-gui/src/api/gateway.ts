import axios from "axios";

export const baseURL: String = import.meta.env.VITE_API_URL;

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});


