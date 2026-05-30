import { useState, useEffect, useCallback } from "react";
import {
  fetchProjects,
  createProject,
  updateProject,
  deleteProject,
  fetchTags,
} from "../services/api";
import "./ProjectManager.css";

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const currentYear = new Date().getFullYear();
const YEARS = Array.from({ length: 20 }, (_, i) => currentYear - i);

function emptyForm() {
  return {
    title: "",
    personal_title: "",
    start_month: 1,
    start_year: currentYear,
    end_month: null,
    end_year: null,
    technologies: [],
    frameworks: [],
    languages: [],
    bullet_points: [""],
    tags: [],
  };
}

function ProjectManager({ onBack }) {
  const [projects, setProjects] = useState([]);
  const [editing, setEditing] = useState(null); // null = list, "new" = create, number = edit
  const [form, setForm] = useState(emptyForm());
  const [tagInput, setTagInput] = useState("");
  const [techInput, setTechInput] = useState("");
  const [frameworkInput, setFrameworkInput] = useState("");
  const [languageInput, setLanguageInput] = useState("");
  const [allTags, setAllTags] = useState([]);
  const [saving, setSaving] = useState(false);
  const [quickAdd, setQuickAdd] = useState(null); // { projectId, category }

  const loadProjects = useCallback(async () => {
    try {
      const data = await fetchProjects();
      setProjects(data);
    } catch (err) {
      console.error("Failed to load projects:", err);
    }
  }, []);

  const loadTags = useCallback(async () => {
    try {
      const data = await fetchTags();
      setAllTags(data);
    } catch (err) {
      console.error("Failed to load tags:", err);
    }
  }, []);

  useEffect(() => {
    loadProjects();
    loadTags();
  }, [loadProjects, loadTags]);

  function startNew() {
    setForm(emptyForm());
    setEditing("new");
  }

  function startEdit(project) {
    setForm({
      title: project.title,
      personal_title: project.personal_title || "",
      start_month: project.start_month,
      start_year: project.start_year,
      end_month: project.end_month,
      end_year: project.end_year,
      technologies: [...(project.technologies || [])],
      frameworks: [...(project.frameworks || [])],
      languages: [...(project.languages || [])],
      bullet_points:
        project.bullet_points.length > 0 ? [...project.bullet_points] : [""],
      tags: [...project.tags],
    });
    setEditing(project.id);
  }

  function cancel() {
    setEditing(null);
    setForm(emptyForm());
  }

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function addBulletPoint() {
    setForm((prev) => ({ ...prev, bullet_points: [...prev.bullet_points, ""] }));
  }

  function removeBulletPoint(index) {
    setForm((prev) => ({
      ...prev,
      bullet_points: prev.bullet_points.filter((_, i) => i !== index),
    }));
  }

  function updateBulletPoint(index, value) {
    setForm((prev) => {
      const bp = [...prev.bullet_points];
      bp[index] = value;
      return { ...prev, bullet_points: bp };
    });
  }

  function addTag(tagName) {
    const name = tagName.trim();
    if (!name || form.tags.includes(name)) return;
    setForm((prev) => ({ ...prev, tags: [...prev.tags, name] }));
    setTagInput("");
  }

  function removeTag(tagName) {
    setForm((prev) => ({
      ...prev,
      tags: prev.tags.filter((t) => t !== tagName),
    }));
  }

  function addTechItem(field, input, setInput) {
    const name = input.trim();
    if (!name || form[field].includes(name)) return;
    setForm((prev) => ({ ...prev, [field]: [...prev[field], name] }));
    setInput("");
  }

  function removeTechItem(field, name) {
    setForm((prev) => ({
      ...prev,
      [field]: prev[field].filter((t) => t !== name),
    }));
  }

  async function handleSave() {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      const payload = {
        ...form,
        bullet_points: form.bullet_points.filter((b) => b.trim()),
        end_month: form.end_month || null,
        end_year: form.end_year || null,
      };
      if (editing === "new") {
        await createProject(payload);
      } else {
        await updateProject(editing, payload);
      }
      await loadProjects();
      await loadTags();
      cancel();
    } catch (err) {
      console.error("Failed to save project:", err);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this project?")) return;
    try {
      await deleteProject(id);
      await loadProjects();
      if (editing === id) cancel();
    } catch (err) {
      console.error("Failed to delete project:", err);
    }
  }

  function formatDate(p) {
    const start = `${MONTHS[p.start_month - 1]} ${p.start_year}`;
    if (p.end_month && p.end_year) {
      return `${start} – ${MONTHS[p.end_month - 1]} ${p.end_year}`;
    }
    return start;
  }

  async function handleQuickAdd(projectId, category, value) {
    const name = value.trim();
    if (!name) return;
    try {
      const project = projects.find((p) => p.id === projectId);
      if (!project) return;
      const updated = { [category]: [...(project[category] || []), name] };
      await updateProject(projectId, updated);
      setQuickAdd(null);
      await loadProjects();
    } catch (err) {
      console.error("Failed to add item:", err);
    }
  }

  // Renders a category section with inline quick-add input
  function renderCategory(proj, field, label, tagClass) {
    const items = proj[field];
    const isOpen = quickAdd && quickAdd.projectId === proj.id && quickAdd.category === field;
    return (
      <div className="pm-category-section" key={field}>
        <div className="pm-category-header">
          <span className="pm-category-label">{label}</span>
          <button
            className="pm-add-inline-btn"
            onClick={() =>
              setQuickAdd(
                isOpen ? null : { projectId: proj.id, category: field, value: "" },
              )
            }
            title={`Add ${label.toLowerCase()}`}
          >
            +
          </button>
        </div>
        {items && items.length > 0 && (
          <div className="pm-tech-list">
            {items.map((t, i) => (
              <span key={i} className={`pm-tech-tag ${tagClass}`}>{t}</span>
            ))}
          </div>
        )}
        {isOpen && (
          <div className="pm-quick-add-row">
            <input
              className="pm-input pm-input-sm"
              type="text"
              placeholder={`New ${label.toLowerCase().slice(0, -1)}...`}
              autoFocus
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleQuickAdd(proj.id, field, e.target.value);
                }
                if (e.key === "Escape") {
                  setQuickAdd(null);
                }
              }}
              onBlur={(e) => {
                // Small delay to allow Add button click to register
                setTimeout(() => setQuickAdd(null), 200);
              }}
            />
            <button
              className="pm-btn pm-btn-sm pm-btn-primary"
              onClick={(e) => {
                const input = e.target.closest(".pm-quick-add-row")?.querySelector("input");
                if (input) handleQuickAdd(proj.id, field, input.value);
              }}
            >
              Add
            </button>
            <button className="pm-btn pm-btn-sm" onClick={() => setQuickAdd(null)}>
              Cancel
            </button>
          </div>
        )}
      </div>
    );
  }

  // ── List View ──
  if (!editing) {
    return (
      <div className="pm-container">
        <div className="pm-header">
          <h2 className="pm-title">Projects</h2>
          <div className="pm-header-actions">
            <button className="pm-btn pm-btn-secondary" onClick={onBack}>
              ← Back to Resume
            </button>
            <button className="pm-btn pm-btn-primary" onClick={startNew}>
              + New Project
            </button>
          </div>
        </div>

        {projects.length === 0 && (
          <div className="pm-empty">
            <p>No projects yet. Click &quot;+ New Project&quot; to add one.</p>
          </div>
        )}

        <div className="pm-list">
          {projects.map((proj) => (
            <div key={proj.id} className="pm-card">
              <div className="pm-card-header">
                <div>
                  <h3 className="pm-card-title">{proj.title}</h3>
                  {proj.personal_title && (
                    <p className="pm-card-role">{proj.personal_title}</p>
                  )}
                  <span className="pm-card-date">{formatDate(proj)}</span>
                </div>
                <div className="pm-card-actions">
                  <button
                    className="pm-btn pm-btn-sm"
                    onClick={() => startEdit(proj)}
                  >
                    Edit
                  </button>
                  <button
                    className="pm-btn pm-btn-sm pm-btn-danger"
                    onClick={() => handleDelete(proj.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>

              {renderCategory(proj, "languages", "Languages", "pm-lang-tag")}
              {renderCategory(proj, "frameworks", "Frameworks", "pm-framework-tag")}
              {renderCategory(proj, "technologies", "Technologies", "pm-tech-only-tag")}

              {proj.tags.length > 0 && (
                <div className="pm-tag-list">
                  {proj.tags.map((t, i) => (
                    <span key={i} className="pm-tag">{t}</span>
                  ))}
                </div>
              )}

              {proj.bullet_points.length > 0 && (
                <ol className="pm-bullets">
                  {proj.bullet_points.map((bp, i) => (
                    <li key={i}>{bp}</li>
                  ))}
                </ol>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── Edit / Create Form ──
  return (
    <div className="pm-container">
      <div className="pm-header">
        <h2 className="pm-title">
          {editing === "new" ? "New Project" : "Edit Project"}
        </h2>
        <button className="pm-btn pm-btn-secondary" onClick={cancel}>
          ← Cancel
        </button>
      </div>

      <div className="pm-form">
        {/* Title */}
        <div className="pm-field">
          <label className="pm-label">Project Title *</label>
          <input
            className="pm-input"
            type="text"
            placeholder="e.g. Resume Website"
            value={form.title}
            onChange={(e) => updateField("title", e.target.value)}
          />
        </div>

        {/* Personal Title / Role */}
        <div className="pm-field">
          <label className="pm-label">Your Role</label>
          <input
            className="pm-input"
            type="text"
            placeholder="e.g. Student, Independent Project, Developer"
            value={form.personal_title}
            onChange={(e) => updateField("personal_title", e.target.value)}
          />
        </div>

        {/* Date */}
        <div className="pm-row">
          <div className="pm-field">
            <label className="pm-label">Start Month</label>
            <select
              className="pm-input"
              value={form.start_month}
              onChange={(e) => updateField("start_month", Number(e.target.value))}
            >
              {MONTHS.map((m, i) => (
                <option key={i} value={i + 1}>{m}</option>
              ))}
            </select>
          </div>
          <div className="pm-field">
            <label className="pm-label">Start Year</label>
            <select
              className="pm-input"
              value={form.start_year}
              onChange={(e) => updateField("start_year", Number(e.target.value))}
            >
              {YEARS.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
          <div className="pm-field">
            <label className="pm-label">End Month</label>
            <select
              className="pm-input"
              value={form.end_month || ""}
              onChange={(e) =>
                updateField(
                  "end_month",
                  e.target.value ? Number(e.target.value) : null,
                )
              }
            >
              <option value="">Present</option>
              {MONTHS.map((m, i) => (
                <option key={i} value={i + 1}>{m}</option>
              ))}
            </select>
          </div>
          <div className="pm-field">
            <label className="pm-label">End Year</label>
            <select
              className="pm-input"
              value={form.end_year || ""}
              onChange={(e) =>
                updateField(
                  "end_year",
                  e.target.value ? Number(e.target.value) : null,
                )
              }
            >
              <option value="">Present</option>
              {YEARS.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Languages */}
        <div className="pm-field">
          <label className="pm-label">Languages</label>
          <div className="pm-tag-input-row">
            <input
              className="pm-input"
              type="text"
              placeholder="e.g. Python"
              value={languageInput}
              onChange={(e) => setLanguageInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addTechItem("languages", languageInput, setLanguageInput);
                }
              }}
            />
            <button
              className="pm-btn pm-btn-sm pm-btn-primary"
              onClick={() => addTechItem("languages", languageInput, setLanguageInput)}
            >
              Add
            </button>
          </div>
          <div className="pm-tag-chips">
            {form.languages.map((t, i) => (
              <span key={i} className="pm-chip pm-chip-lang">
                {t}
                <button
                  className="pm-chip-remove"
                  onClick={() => removeTechItem("languages", t)}
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Frameworks */}
        <div className="pm-field">
          <label className="pm-label">Frameworks</label>
          <div className="pm-tag-input-row">
            <input
              className="pm-input"
              type="text"
              placeholder="e.g. React"
              value={frameworkInput}
              onChange={(e) => setFrameworkInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addTechItem("frameworks", frameworkInput, setFrameworkInput);
                }
              }}
            />
            <button
              className="pm-btn pm-btn-sm pm-btn-primary"
              onClick={() => addTechItem("frameworks", frameworkInput, setFrameworkInput)}
            >
              Add
            </button>
          </div>
          <div className="pm-tag-chips">
            {form.frameworks.map((t, i) => (
              <span key={i} className="pm-chip pm-chip-framework">
                {t}
                <button
                  className="pm-chip-remove"
                  onClick={() => removeTechItem("frameworks", t)}
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Technologies */}
        <div className="pm-field">
          <label className="pm-label">Technologies</label>
          <div className="pm-tag-input-row">
            <input
              className="pm-input"
              type="text"
              placeholder="e.g. Docker"
              value={techInput}
              onChange={(e) => setTechInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addTechItem("technologies", techInput, setTechInput);
                }
              }}
            />
            <button
              className="pm-btn pm-btn-sm pm-btn-primary"
              onClick={() => addTechItem("technologies", techInput, setTechInput)}
            >
              Add
            </button>
          </div>
          <div className="pm-tag-chips">
            {form.technologies.map((t, i) => (
              <span key={i} className="pm-chip pm-chip-tech">
                {t}
                <button
                  className="pm-chip-remove"
                  onClick={() => removeTechItem("technologies", t)}
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Tags */}
        <div className="pm-field">
          <label className="pm-label">Tags</label>
          <div className="pm-tag-input-row">
            <input
              className="pm-input"
              type="text"
              placeholder="e.g. Machine Learning"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addTag(tagInput);
                }
              }}
              list="tag-suggestions"
            />
            <datalist id="tag-suggestions">
              {allTags
                .filter((t) => !form.tags.includes(t))
                .map((t, i) => (
                  <option key={i} value={t} />
                ))}
            </datalist>
            <button
              className="pm-btn pm-btn-sm pm-btn-primary"
              onClick={() => addTag(tagInput)}
            >
              Add
            </button>
          </div>
          <div className="pm-tag-chips">
            {form.tags.map((t, i) => (
              <span key={i} className="pm-chip pm-chip-tag">
                {t}
                <button
                  className="pm-chip-remove"
                  onClick={() => removeTag(t)}
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Bullet Points */}
        <div className="pm-field">
          <label className="pm-label">Bullet Points</label>
          {form.bullet_points.map((bp, i) => (
            <div key={i} className="pm-bp-row">
              <span className="pm-bp-number">{i + 1}.</span>
              <input
                className="pm-input"
                type="text"
                placeholder={`Bullet point ${i + 1}`}
                value={bp}
                onChange={(e) => updateBulletPoint(i, e.target.value)}
              />
              <button
                className="pm-btn pm-btn-sm pm-btn-danger"
                onClick={() => removeBulletPoint(i)}
                disabled={form.bullet_points.length <= 1}
              >
                &times;
              </button>
            </div>
          ))}
          <button
            className="pm-btn pm-btn-sm pm-btn-secondary"
            onClick={addBulletPoint}
          >
            + Add bullet point
          </button>
        </div>

        {/* Save */}
        <div className="pm-form-actions">
          <button
            className="pm-btn pm-btn-primary pm-btn-lg"
            onClick={handleSave}
            disabled={!form.title.trim() || saving}
          >
            {saving ? "Saving..." : "Save Project"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProjectManager;
