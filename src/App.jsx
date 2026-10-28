import { useState } from "react";

// Local default; on Vercel/Netlify set VITE_API_URL to your deployed backend address
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";
const API_URL = `${API_BASE}/api/scan`;

// The backend sends SAFE / SUSPICIOUS / PHISHING; the UI shows these labels.
const STATUS_LABELS = {
  SAFE: "LOW RISK",
  SUSPICIOUS: "SUSPICIOUS",
  PHISHING: "HIGH RISK",
};

const features = [
  {
    icon: "🛡️",
    title: "Phishing Detection",
    desc: "Check suspicious website URLs with a trained machine-learning model.",
  },
  {
    icon: "🔎",
    title: "URL Analysis",
    desc: "Inspect domain structure, IP addresses, length and suspicious keywords.",
  },
  {
    icon: "📊",
    title: "Scan Dashboard",
    desc: "View your recent scans and their risk assessments.",
  },
];

// Basic input check before sending anything to the backend
function validateURL(value) {
  let url;

  try {
    url = new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`);
  } catch {
    return { error: "Please enter a valid website URL." };
  }

  if (!url.hostname.includes(".") || /\s/.test(value)) {
    return { error: "Please enter a valid domain name." };
  }

  return { url: url.href };
}

// Sends the URL to the Flask backend, which runs the trained ML model
async function analyzeURL(value) {
  const check = validateURL(value);
  if (check.error) return check;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: check.url }),
    });

    const data = await response.json();

    if (!response.ok) {
      return { error: data.error || "Scan failed. Please try again." };
    }

    return {
      url: check.url,
      score: data.score,
      status: STATUS_LABELS[data.status] || data.status,
      reasons: data.reasons || [],
      confidence: data.confidence,
      latency: data.latency,
    };
  } catch {
    return {
      error:
        "Could not connect to the backend. Make sure python app.py is running in the Backend folder.",
    };
  }
}

export default function App() {
  const [page, setPage] = useState("Home");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  async function scanURL(event) {
    event.preventDefault();

    if (!url.trim()) {
      setResult({ error: "Please enter a website URL." });
      return;
    }

    setLoading(true);
    setResult(null);

    const analysis = await analyzeURL(url.trim());

    setLoading(false);
    setResult(analysis);

    if (!analysis.error) {
      setHistory((old) =>
        [
          {
            url: analysis.url,
            score: analysis.score,
            status: analysis.status,
            time: new Date().toLocaleString(),
          },
          ...old,
        ].slice(0, 10)
      );
    }
  }

  function goTo(nextPage) {
    setPage(nextPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="app">
      <nav className="navbar">
        <button className="brand" onClick={() => goTo("Home")}>
          <span className="brand-shield">⬡</span>
          PHISHGUARD <span className="brand-ai">AI</span>
        </button>

        <div className="nav-links">
          {["Home", "Scanner", "Dashboard", "About"].map((item) => (
            <button
              key={item}
              className={page === item ? "nav-link active" : "nav-link"}
              onClick={() => goTo(item)}
            >
              {item}
            </button>
          ))}
        </div>
      </nav>

      <main className="container">
        {page === "Home" && (
          <>
            <section className="hero">
              <div className="eyebrow">✦ AI-INSPIRED WEB SECURITY</div>

              <h1>
                INTELLIGENT
                <br />
                <span className="gradient-text">PHISHING WEBSITE</span>
                <br />
                DETECTION
              </h1>

              <p>
                Analyze suspicious URLs, identify potential warning signs,
                and understand website security risks with PhishGuard AI.
              </p>

              <div className="hero-actions">
                <button className="primary" onClick={() => goTo("Scanner")}>
                  ⌕ Scan a Website →
                </button>
                <button className="secondary" onClick={() => goTo("About")}>
                  Learn More
                </button>
              </div>
            </section>

            <section className="stats">
              <div className="stat">
                <strong>URL</strong>
                <span>Website Analysis</span>
              </div>
              <div className="stat">
                <strong>24/7</strong>
                <span>Scan Whenever Needed</span>
              </div>
              <div className="stat">
                <strong>AI + ML</strong>
                <span>Project Development</span>
              </div>
            </section>

            <section className="section">
              <div className="section-heading">
                <span className="eyebrow">CORE FEATURES</span>
                <h2>Stay Aware. Browse Carefully.</h2>
              </div>

              <div className="feature-grid">
                {features.map((feature) => (
                  <article className="feature-card" key={feature.title}>
                    <div className="feature-icon">{feature.icon}</div>
                    <h3>{feature.title}</h3>
                    <p>{feature.desc}</p>
                  </article>
                ))}
              </div>
            </section>
          </>
        )}

        {page === "Scanner" && (
          <section className="page-section">
            <div className="section-heading">
              <span className="eyebrow">URL SECURITY CHECK</span>
              <h1>Website <span className="gradient-text">Scanner</span></h1>
              <p>Enter a URL to check it with the machine-learning model.</p>
            </div>

            <form className="scanner-card" onSubmit={scanURL}>
              <label htmlFor="website">Website URL</label>
              <input
                id="website"
                type="text"
                placeholder="https://example.com"
                value={url}
                onChange={(event) => {
                  setUrl(event.target.value);
                  setResult(null);
                }}
              />
              <button
                className="primary scan-button"
                type="submit"
                disabled={loading}
              >
                {loading ? "Analyzing..." : "⌕ Analyze Website"}
              </button>

              {result && (
                <div className={`result-card ${result.error ? "error" : ""}`}>
                  {result.error ? (
                    <p>{result.error}</p>
                  ) : (
                    <>
                      <span className="result-label">ANALYSIS RESULT</span>
                      <h2>{result.status}</h2>
                      <p className="result-url">{result.url}</p>
                      <div className="risk-track">
                        <div style={{ width: `${result.score}%` }} />
                      </div>
                      <p>Phishing risk score: {result.score}/100</p>
                      {result.confidence != null && (
                        <p>
                          Model confidence: {result.confidence}%
                          {result.latency != null && ` · Scan time: ${result.latency} ms`}
                        </p>
                      )}
                      <h3>Findings</h3>
                      <ul>
                        {result.reasons.map((reason) => (
                          <li key={reason}>{reason}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              )}

              <p className="disclaimer">
                Results come from a machine-learning model that analyses the
                domain name only. It can make mistakes, and a low score does
                not guarantee that a website is safe.
              </p>
            </form>
          </section>
        )}

        {page === "Dashboard" && (
          <section className="page-section">
            <div className="section-heading">
              <span className="eyebrow">SCAN OVERVIEW</span>
              <h1>Your <span className="gradient-text">Dashboard</span></h1>
              <p>Summary of scans performed during this session.</p>
            </div>

            <div className="stats">
              <div className="stat">
                <strong>{history.length}</strong>
                <span>Total Scans</span>
              </div>
              <div className="stat">
                <strong>
                  {history.filter((item) => item.status === "HIGH RISK").length}
                </strong>
                <span>High Risk Results</span>
              </div>
              <div className="stat">
                <strong>
                  {history.filter((item) => item.status === "SUSPICIOUS").length}
                </strong>
                <span>Suspicious Results</span>
              </div>
            </div>

            <div className="history-panel">
              <h2>Recent Scan History</h2>
              {history.length === 0 ? (
                <p className="empty-state">
                  No scans yet. Open Scanner to analyze a URL.
                </p>
              ) : (
                history.map((item, index) => (
                  <div className="history-item" key={`${item.url}-${index}`}>
                    <div>
                      <strong>{item.url}</strong>
                      <p>{item.time}</p>
                    </div>
                    <span className="history-status">{item.status}</span>
                  </div>
                ))
              )}
            </div>
          </section>
        )}

        {page === "About" && (
          <section className="page-section">
            <div className="section-heading">
              <span className="eyebrow">ABOUT THE PROJECT</span>
              <h1>About <span className="gradient-text">PhishGuard AI</span></h1>
              <p>
                An academic cybersecurity project focused on identifying
                suspicious website URLs.
              </p>
            </div>

            <div className="about-grid">
              <article className="feature-card">
                <div className="feature-icon">🎯</div>
                <h3>Objective</h3>
                <p>
                  Help users understand suspicious URL patterns and improve
                  awareness of phishing-related risks.
                </p>
              </article>
              <article className="feature-card">
                <div className="feature-icon">⚙️</div>
                <h3>Current Implementation</h3>
                <p>
                  React interface connected to a Flask backend. A Gradient
                  Boosting model trained with scikit-learn scores each domain
                  name using features such as length, hyphens, digits,
                  subdomains and suspicious keywords.
                </p>
              </article>
            </div>

            <div className="tech-panel">
              <h2>Technology Stack</h2>
              <div className="tags">
                {["React", "JavaScript", "Vite", "CSS", "Python", "Flask", "scikit-learn", "Machine Learning"].map((tech) => (
                  <span className="tag" key={tech}>{tech}</span>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <div className="footer-brand">⬡ PHISHGUARD AI</div>
        <p>Intelligent Phishing Website Detection</p>
        <p>Academic project demonstration · Not a guarantee of website safety</p>
      </footer>
    </div>
  );
}