import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Resume from "./Resume";

const mockData = {
  name: "Jane Smith",
  email: "jane@example.com",
  phone: "+1-555-5678",
  location: "New York, NY",
  summary: "A passionate developer.",
  experience: [
    {
      company: "Startup Inc",
      title: "Full Stack Developer",
      start_date: "2021-03-01",
      end_date: null,
      description: ["Built web applications", "Led frontend team"],
    },
  ],
  education: [
    {
      institution: "Stanford University",
      degree: "BS",
      field_of_study: "Computer Engineering",
      graduation_date: "2021-06-15",
      gpa: 3.9,
    },
  ],
  skills: [
    { category: "Languages", items: ["Python", "TypeScript"] },
  ],
  projects: [
    {
      name: "Open Source Lib",
      description: "A useful library",
      technologies: ["Python"],
      url: "https://github.com/jane/lib",
    },
  ],
  certifications: ["Google Cloud Certified"],
};

describe("Resume Component", () => {
  it("renders the name", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText("Jane Smith")).toBeDefined();
  });

  it("renders contact information", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText("jane@example.com")).toBeDefined();
    expect(screen.getByText("+1-555-5678")).toBeDefined();
    expect(screen.getByText("New York, NY")).toBeDefined();
  });

  it("renders the summary", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText("A passionate developer.")).toBeDefined();
  });

  it("renders section titles", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText("Professional Summary")).toBeDefined();
    expect(screen.getByText("Experience")).toBeDefined();
    expect(screen.getByText("Education")).toBeDefined();
    expect(screen.getByText("Skills")).toBeDefined();
    expect(screen.getByText("Projects")).toBeDefined();
    expect(screen.getByText("Certifications")).toBeDefined();
  });

  it("renders experience details", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText("Startup Inc")).toBeDefined();
    expect(screen.getByText("Full Stack Developer")).toBeDefined();
    expect(screen.getByText("Built web applications")).toBeDefined();
    expect(screen.getByText("Led frontend team")).toBeDefined();
  });

  it("renders education details", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText("Stanford University")).toBeDefined();
    expect(screen.getByText(/BS in Computer Engineering/)).toBeDefined();
    expect(screen.getByText(/GPA: 3.90/)).toBeDefined();
  });

  it("renders skills", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText(/Python, TypeScript/)).toBeDefined();
  });

  it("renders projects with links", () => {
    render(<Resume data={mockData} />);
    const link = screen.getByText("Open Source Lib");
    expect(link.closest("a")).toHaveAttribute(
      "href",
      "https://github.com/jane/lib",
    );
  });

  it("renders certifications", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText("Google Cloud Certified")).toBeDefined();
  });

  it("renders tech tags for projects", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText("Python")).toBeDefined();
  });

  it("renders Present for current positions", () => {
    render(<Resume data={mockData} />);
    expect(screen.getByText(/Present/)).toBeDefined();
  });

  it("shows empty state when no data", () => {
    render(<Resume data={null} />);
    expect(screen.getByText("No resume data available.")).toBeDefined();
  });
});

describe("Resume Component - Edge Cases", () => {
  it("renders with minimal data", () => {
    const minimalData = {
      name: "John",
      email: "john@test.com",
      summary: "Hello",
    };
    render(<Resume data={minimalData} />);
    expect(screen.getByText("John")).toBeDefined();
  });

  it("hides experience section when empty", () => {
    const data = {
      ...mockData,
      experience: [],
    };
    render(<Resume data={data} />);
    expect(screen.queryByText("Experience")).toBeNull();
  });
});
