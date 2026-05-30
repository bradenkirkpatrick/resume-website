import "./Resume.css";

function formatDate(dateStr) {
  if (!dateStr) return "Present";
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
  });
}

function ResumeSection({ title, children }) {
  return (
    <section className="resume-section">
      <h2 className="section-title">{title}</h2>
      {children}
    </section>
  );
}

function ExperienceItem({ item }) {
  return (
    <div className="resume-item">
      <div className="item-header">
        <div>
          <h3 className="item-title">{item.title}</h3>
          <p className="item-subtitle">{item.company}</p>
        </div>
        <span className="item-date">
          {formatDate(item.start_date)} – {formatDate(item.end_date)}
        </span>
      </div>
      {item.description && item.description.length > 0 && (
        <ul className="item-description">
          {item.description.map((desc, i) => (
            <li key={i}>{desc}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function EducationItem({ item }) {
  return (
    <div className="resume-item">
      <div className="item-header">
        <div>
          <h3 className="item-title">{item.institution}</h3>
          <p className="item-subtitle">
            {item.degree} in {item.field_of_study}
          </p>
        </div>
        <span className="item-date">{formatDate(item.graduation_date)}</span>
      </div>
      {item.gpa && <p className="item-gpa">GPA: {item.gpa.toFixed(2)}</p>}
    </div>
  );
}

function SkillItem({ item }) {
  return (
    <div className="skill-item">
      <span className="skill-category">{item.category}:</span>
      <span className="skill-items">{item.items.join(", ")}</span>
    </div>
  );
}

function ProjectItem({ item }) {
  return (
    <div className="resume-item">
      <div className="item-header">
        <h3 className="item-title">
          {item.url ? (
            <a href={item.url} target="_blank" rel="noopener noreferrer">
              {item.name}
            </a>
          ) : (
            item.name
          )}
        </h3>
        {item.personal_title && (
          <p className="item-subtitle">{item.personal_title}</p>
        )}
      </div>
      <p className="item-description-text">{item.description}</p>
      {item.technologies && item.technologies.length > 0 && (
        <div className="tech-tags">
          {item.technologies.map((tech, i) => (
            <span key={i} className="tech-tag">
              {tech}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

const SECTION_RENDERERS = {
  summary(data) {
    if (!data.summary) return null;
    return (
      <ResumeSection key="summary" title="Professional Summary">
        <p className="summary-text">{data.summary}</p>
      </ResumeSection>
    );
  },
  experience(data) {
    if (!data.experience?.length) return null;
    return (
      <ResumeSection key="experience" title="Experience">
        {data.experience.map((exp, i) => (
          <ExperienceItem key={i} item={exp} />
        ))}
      </ResumeSection>
    );
  },
  education(data) {
    if (!data.education?.length) return null;
    return (
      <ResumeSection key="education" title="Education">
        {data.education.map((edu, i) => (
          <EducationItem key={i} item={edu} />
        ))}
      </ResumeSection>
    );
  },
  skills(data) {
    if (!data.skills?.length) return null;
    return (
      <ResumeSection key="skills" title="Skills">
        <div className="skills-container">
          {data.skills.map((skill, i) => (
            <SkillItem key={i} item={skill} />
          ))}
        </div>
      </ResumeSection>
    );
  },
  projects(data) {
    if (!data.projects?.length) return null;
    return (
      <ResumeSection key="projects" title="Projects">
        {data.projects.map((proj, i) => (
          <ProjectItem key={i} item={proj} />
        ))}
      </ResumeSection>
    );
  },
  certifications(data) {
    if (!data.certifications?.length) return null;
    return (
      <ResumeSection key="certifications" title="Certifications">
        <ul className="cert-list">
          {data.certifications.map((cert, i) => (
            <li key={i}>{cert}</li>
          ))}
        </ul>
      </ResumeSection>
    );
  },
};

function Resume({ data, sectionOrder }) {
  if (!data) {
    return <div className="resume-empty">No resume data available.</div>;
  }

  const order = sectionOrder && sectionOrder.length > 0
    ? sectionOrder
    : ["summary", "experience", "education", "skills", "projects", "certifications"];

  return (
    <div className="resume">
      {/* Header */}
      <div className="resume-header">
        <h1 className="resume-name">{data.name}</h1>
        <div className="resume-contact">
          {data.email && <span>{data.email}</span>}
          {data.phone && <span>{data.phone}</span>}
          {data.location && <span>{data.location}</span>}
        </div>
      </div>

      {order.map((sectionId) => {
        const renderer = SECTION_RENDERERS[sectionId];
        return renderer ? renderer(data) : null;
      })}
    </div>
  );
}

export default Resume;
