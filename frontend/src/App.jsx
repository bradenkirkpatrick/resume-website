import { useState, useEffect } from "react";
import Resume from "./components/Resume";
import ProjectManager from "./components/ProjectManager";
import SectionReorder from "./components/SectionReorder";
import { fetchResume, downloadResume, fetchSectionOrder } from "./services/api";
import "./App.css";

function App() {
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [view, setView] = useState("resume"); // "resume" | "projects" | "customize" | "rawdoc"
  const [sectionOrder, setSectionOrder] = useState(null);
  const [rawDoc, setRawDoc] = useState(null);

  async function loadResume() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchResume();
      setResume(data);
    } catch (err) {
      setError("Failed to load resume. Please ensure the backend server is running.");
      console.error("Error loading resume:", err);
    } finally {
      setLoading(false);
    }
  }

  async function loadSectionOrder() {
    try {
      const order = await fetchSectionOrder();
      setSectionOrder(order);
    } catch {
      // Use default order
    }
  }

  useEffect(() => {
    loadResume();
    loadSectionOrder();
  }, []);

  async function handleDownload() {
    try {
      await downloadResume();
    } catch (err) {
      console.error("Error downloading resume:", err);
    }
  }

  async function loadRawDoc() {
    try {
      const resp = await fetch("/api/resume/raw");
      const text = await resp.text();
      setRawDoc(text);
      setView("rawdoc");
    } catch (err) {
      console.error("Error loading raw doc:", err);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">Resume</h1>
          <div className="header-actions">
            {view === "resume" ? (
              <>
                <button
                  className={`nav-btn ${view === "rawdoc" ? "nav-btn-active" : ""}`}
                  onClick={loadRawDoc}
                >
                  Doc View
                </button>
                <button
                  className="nav-btn"
                  onClick={() => setView("customize")}
                >
                  Customize Order
                </button>
                <button
                  className="nav-btn"
                  onClick={() => { setView("resume"); loadSectionOrder(); }}
                >
                  Resume View
                </button>
                <button
                  className="nav-btn"
                  onClick={() => setView("projects")}
                >
                  Manage Projects
                </button>
                <button className="download-btn" onClick={handleDownload}>
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 3a.75.75 0 01.75.75v7.5l2.72-2.72a.75.75 0 111.06 1.06l-4 4a.75.75 0 01-1.06 0l-4-4a.75.75 0 011.06-1.06l2.72 2.72V3.75A.75.75 0 0110 3z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Download Resume
                </button>
              </>
            ) : (
              <button
                className="nav-btn"
                onClick={() => { setView("resume"); loadSectionOrder(); }}
              >
                ← Back to Resume
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        {view === "projects" && (
          <ProjectManager onBack={() => setView("resume")} />
        )}

        {view === "customize" && (
          <SectionReorder onDone={() => { setView("resume"); loadSectionOrder(); }} />
        )}

        {view === "rawdoc" && rawDoc && (
          <div className="raw-doc-container">
            <h2 className="raw-doc-title">Google Doc Content</h2>
            <p className="raw-doc-subtitle">
              This is the raw text from your Google Doc. Edits made there appear here on refresh.
            </p>
            <pre className="raw-doc-content">{rawDoc}</pre>
          </div>
        )}

        {view === "resume" && loading && (
          <div className="loading-container">
            <div className="loading-spinner" />
            <p>Loading resume...</p>
          </div>
        )}

        {view === "resume" && error && (
          <div className="error-container">
            <p className="error-message">{error}</p>
            <button className="retry-btn" onClick={loadResume}>
              Retry
            </button>
          </div>
        )}

        {view === "resume" && !loading && !error && resume && (
          <Resume data={resume} sectionOrder={sectionOrder} />
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI &amp; React</p>
      </footer>
    </div>
  );
}

export default App;
