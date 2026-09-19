"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

export function Tracker() {
  const pathname = usePathname();
  const trackedRef = useRef<string | null>(null);

  useEffect(() => {
    // Avoid double tracking in development mode strict mode or same page navigation
    if (trackedRef.current === pathname) return;
    trackedRef.current = pathname;

    const track = async () => {
      try {
        await fetch(`/api/analytics/track`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            path: pathname,
            referrer: document.referrer || "",
          }),
          // fire and forget, don't wait for response
          keepalive: true,
        });
      } catch {
        // Silently fail if tracker is blocked or backend is down
      }
    };

    track();
  }, [pathname]);

  return null; // Invisible component
}
