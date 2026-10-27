
export const analyzeURL = async (input) => {
  if (!input || !input.trim()) return null;

  let url = input.trim();

  // Remove surrounding quotes and common Markdown brackets
  url = url.replace(/^[\s"'([{]+|[\s"')\]}]+$/g, "");

  // Extract URL from pasted text, if present
  const match = url.match(/https?:\/\/[^\s]+/i);
  if (match) {
    url = match[0];
  }

  // Add HTTPS if protocol is missing
  if (!/^https?:\/\//i.test(url)) {
    url = `https://${url}`;
  }

  try {
    const response = await fetch("http://127.0.0.1:5000/api/scan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Scan request failed.");
    }

    // Convert Flask response to the format expected by the React UI
    return {
      ...data,
      confidence: data.confidence ?? null,
      latency: data.latency ?? null,
      features: (data.reasons || []).map((reason) => ({
        name: "Detection Finding",
        detail: reason,
        weight: "",
      })),
    };
  } catch (error) {
    console.error("Backend scan error:", error);

    return {
      score: 0,
      status: "ERROR",
      features: [
        {
          name: "Backend Connection",
          detail:
            "Could not connect to Flask. Check that the backend is running.",
          weight: "",
        },
      ],
      error: error.message,
    };
  }
};
