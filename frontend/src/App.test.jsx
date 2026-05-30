import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "./App";

// Mock the API module
vi.mock("./services/api", () => ({
  fetchResume: vi.fn(),
  downloadResume: vi.fn(),
}));

import { fetchResume } from "./services/api";

const mockResumeData = {
  name: "John Doe",
  email: "john@example.com",
  phone: "+1-555-1234",
  location: "San Francisco, CA",
  summary: "Experienced software engineer.",
  experience: [
    {
      company: "Tech Corp",
      title: "Senior Engineer",
      start_date: "2020-01-01",
      end_date: null,
      description: ["Built microservices"],
    },
  ],
  education: [
    {
      institution: "MIT",
      degree: "BS",
      field_of_study: "Computer Science",
      graduation_date: "2018-05-15",
      gpa: 3.8,
    },
  ],
  skills: [
    { category: "Languages", items: ["Python", "JavaScript"] },
  ],
  projects: [
    {
      name: "Awesome Project",
      description: "A great project",
      technologies: ["React", "FastAPI"],
      url: "https://github.com/john/awesome",
    },
  ],
  certifications: ["AWS Certified Developer"],
};

describe("App Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the app title", () => {
    fetchResume.mockResolvedValue(mockResumeData);
    render(<App />);
    expect(screen.getByText("Resume")).toBeDefined();
  });

  it("shows loading state initially", () => {
    fetchResume.mockImplementation(() => new Promise(() => {}));
    render(<App />);
    expect(screen.getByText("Loading resume...")).toBeDefined();
  });

  it("renders resume data after loading", async () => {
    fetchResume.mockResolvedValue(mockResumeData);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeDefined();
    });
  });

  it("renders download button", async () => {
    fetchResume.mockResolvedValue(mockResumeData);
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Download Resume")).toBeDefined();
    });
  });

  it("shows error message on fetch failure", async () => {
    fetchResume.mockRejectedValue(new Error("Network error"));
    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByText(/Failed to load resume/),
      ).toBeDefined();
    });
  });

  it("shows retry button on error", async () => {
    fetchResume.mockRejectedValue(new Error("Network error"));
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Retry")).toBeDefined();
    });
  });

  it("renders footer", () => {
    fetchResume.mockResolvedValue(mockResumeData);
    render(<App />);
    expect(screen.getByText("Powered by FastAPI & React")).toBeDefined();
  });
});
