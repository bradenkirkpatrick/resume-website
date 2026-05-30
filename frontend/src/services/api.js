import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Fetch resume data from the backend API.
 * @returns {Promise<Object>} The resume data object.
 */
export async function fetchResume() {
  const response = await apiClient.get("/resume");
  return response.data;
}

/**
 * Download the resume as a file.
 * Triggers a browser download.
 */
export async function downloadResume() {
  const response = await apiClient.get("/resume/download", {
    responseType: "blob",
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "resume.json");
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

// ── Project Management API ─────────────────────────────────────────────────────

/**
 * Fetch all user-managed projects.
 * @returns {Promise<Array>} List of project objects.
 */
export async function fetchProjects() {
  const response = await apiClient.get("/projects");
  return response.data;
}

/**
 * Get a single project by ID.
 * @param {number} id - Project ID
 * @returns {Promise<Object>} The project object.
 */
export async function fetchProject(id) {
  const response = await apiClient.get(`/projects/${id}`);
  return response.data;
}

/**
 * Create a new project.
 * @param {Object} data - Project data (title, start_month, start_year, end_month, end_year, technologies, bullet_points, tags)
 * @returns {Promise<Object>} The created project.
 */
export async function createProject(data) {
  const response = await apiClient.post("/projects", data);
  return response.data;
}

/**
 * Update an existing project.
 * @param {number} id - Project ID
 * @param {Object} data - Fields to update
 * @returns {Promise<Object>} The updated project.
 */
export async function updateProject(id, data) {
  const response = await apiClient.put(`/projects/${id}`, data);
  return response.data;
}

/**
 * Delete a project.
 * @param {number} id - Project ID
 */
export async function deleteProject(id) {
  await apiClient.delete(`/projects/${id}`);
}

/**
 * Fetch all available tags.
 * @returns {Promise<Array>} List of tag strings.
 */
export async function fetchTags() {
  const response = await apiClient.get("/projects/tags/all");
  return response.data;
}

// ── Section Order API ─────────────────────────────────────────────────────────

/**
 * Fetch the current section display order.
 * @returns {Promise<Array<string>>} Ordered list of section IDs.
 */
export async function fetchSectionOrder() {
  const response = await apiClient.get("/sections/order");
  return response.data;
}

/**
 * Update the section display order.
 * @param {Array<string>} sections - Ordered list of section IDs.
 * @returns {Promise<Array<string>>} The saved order.
 */
export async function updateSectionOrder(sections) {
  const response = await apiClient.put("/sections/order", sections);
  return response.data;
}
