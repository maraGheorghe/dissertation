import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import TranscriptPage from "./pages/TrascriptPage.js";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<UploadPage />} />
                <Route path="/transcript/:id" element={<TranscriptPage />} />
            </Routes>
        </Router>
    );
}

export default App;
