import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import { useEffect, useMemo } from "react";

// Leaflet's default marker icons rely on webpack asset URLs that Vite doesn't
// wire up automatically — fix by pointing directly at the CDN copies.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// One distinct color per day (cycles if > 6 days).
const DAY_COLORS = ["#e63946", "#2196f3", "#4caf50", "#ff9800", "#9c27b0", "#00bcd4"];

function dayColor(dayIndex) {
  return DAY_COLORS[dayIndex % DAY_COLORS.length];
}

// Inner component: fits map bounds whenever stops change.
function BoundsFitter({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 0) {
      map.fitBounds(L.latLngBounds(positions), { padding: [40, 40] });
    }
  }, [map, positions]);
  return null;
}

export default function ItineraryMap({ plan }) {
  const days = plan?.days ?? [];
  const hasStops = days.some((d) => d.stops?.length > 0);

  // Flat list of [lat, lng] for bounds fitting.
  const allPositions = useMemo(
    () => days.flatMap((d) => (d.stops ?? []).map((s) => [s.lat, s.lng])),
    [days],
  );

  if (!hasStops) {
    return (
      <div style={{ padding: "16px", color: "#9ca3af", textAlign: "center" }}>
        Map will appear here once your itinerary is ready.
      </div>
    );
  }

  // Default center before BoundsFitter runs — first stop.
  const firstStop = days[0].stops[0];
  const defaultCenter = [firstStop.lat, firstStop.lng];

  return (
    <MapContainer
      center={defaultCenter}
      zoom={13}
      style={{ height: 420, width: "100%" }}
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <BoundsFitter positions={allPositions} />

      {days.map((day, di) => {
        const stops = day.stops ?? [];
        const color = dayColor(di);
        const polyline = stops.map((s) => [s.lat, s.lng]);

        return (
          <span key={day.day}>
            {stops.map((stop) => (
              <Marker key={stop.id} position={[stop.lat, stop.lng]}>
                <Popup>
                  <strong>{stop.name}</strong>
                  <br />
                  Day {day.day}
                  {stop.arrival && (
                    <>
                      <br />
                      {stop.arrival} – {stop.depart}
                    </>
                  )}
                  {stop.leg_to_next && (
                    <>
                      <br />
                      {Math.round(stop.leg_to_next.minutes)} min to next stop
                    </>
                  )}
                </Popup>
              </Marker>
            ))}

            {polyline.length > 1 && (
              <Polyline positions={polyline} color={color} weight={3} opacity={0.8} />
            )}
          </span>
        );
      })}
    </MapContainer>
  );
}
