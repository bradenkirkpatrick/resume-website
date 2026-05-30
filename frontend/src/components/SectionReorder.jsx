import { useState, useEffect } from "react";
import { fetchSectionOrder, updateSectionOrder } from "../services/api";
import "./SectionReorder.css";

const SECTION_LABELS = {
  summary: "Professional Summary",
  experience: "Experience",
  education: "Education",
  skills: "Skills",
  projects: "Projects",
  certifications: "Certifications",
};

function SectionReorder({ onDone }) {
  const [sections, setSections] = useState([]);
  const [saving, setSaving] = useState(false);
  const [dragIndex, setDragIndex] = useState(null);

  useEffect(() => {
    fetchSectionOrder()
      .then(setSections)
      .catch(console.error);
  }, []);

  function moveUp(index) {
    if (index === 0) return;
    setSections((prev) => {
      const arr = [...prev];
      [arr[index - 1], arr[index]] = [arr[index], arr[index - 1]];
      return arr;
    });
  }

  function moveDown(index) {
    if (index === sections.length - 1) return;
    setSections((prev) => {
      const arr = [...prev];
      [arr[index], arr[index + 1]] = [arr[index + 1], arr[index]];
      return arr;
    });
  }

  function handleDragStart(index) {
    setDragIndex(index);
  }

  function handleDragOver(e, index) {
    e.preventDefault();
    if (dragIndex === null || dragIndex === index) return;
    setSections((prev) => {
      const arr = [...prev];
      const [moved] = arr.splice(dragIndex, 1);
      arr.splice(index, 0, moved);
      return arr;
    });
    setDragIndex(index);
  }

  function handleDragEnd() {
    setDragIndex(null);
  }

  async function handleSave() {
    setSaving(true);
    try {
      await updateSectionOrder(sections);
      onDone();
    } catch (err) {
      console.error("Failed to save section order:", err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="sr-container">
      <div className="sr-header">
        <h2 className="sr-title">Customize Section Order</h2>
        <p className="sr-subtitle">
          Drag and drop sections to reorder them on your resume.
        </p>
      </div>

      <div className="sr-list">
        {sections.map((id, i) => (
          <div
            key={id}
            className={`sr-item ${dragIndex === i ? "sr-dragging" : ""}`}
            draggable
            onDragStart={() => handleDragStart(i)}
            onDragOver={(e) => handleDragOver(e, i)}
            onDragEnd={handleDragEnd}
          >
            <span className="sr-grip">⠿</span>
            <span className="sr-number">{i + 1}</span>
            <span className="sr-name">{SECTION_LABELS[id] || id}</span>
            <div className="sr-arrows">
              <button
                className="sr-arrow"
                onClick={(e) => { e.stopPropagation(); moveUp(i); }}
                disabled={i === 0}
                aria-label="Move up"
              >
                ▲
              </button>
              <button
                className="sr-arrow"
                onClick={(e) => { e.stopPropagation(); moveDown(i); }}
                disabled={i === sections.length - 1}
                aria-label="Move down"
              >
                ▼
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="sr-actions">
        <button className="pm-btn pm-btn-secondary" onClick={onDone}>
          Cancel
        </button>
        <button
          className="pm-btn pm-btn-primary pm-btn-lg"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? "Saving..." : "Save Order"}
        </button>
      </div>
    </div>
  );
}

export default SectionReorder;
