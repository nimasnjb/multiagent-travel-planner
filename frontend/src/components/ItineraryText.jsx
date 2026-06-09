import ReactMarkdown from "react-markdown";

const styles = {
  container: {
    maxWidth: 720,
    margin: "0 auto",
    padding: "16px 24px",
    fontFamily: "sans-serif",
    lineHeight: 1.6,
  },
  empty: {
    padding: "16px 24px",
    color: "#9ca3af",
    textAlign: "center",
  },
};

export default function ItineraryText({ plan }) {
  const narrative = plan?.narrative;

  if (!narrative) {
    return (
      <div style={styles.empty}>
        Itinerary narrative will appear here once your trip is planned.
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <ReactMarkdown>{narrative}</ReactMarkdown>
    </div>
  );
}
