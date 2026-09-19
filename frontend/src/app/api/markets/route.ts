import { NextResponse } from "next/server";
import { getMarketFeed } from "@/lib/markets";

/**
 * Cotações agro server-side. Cacheia a resposta em 5 min para não espancar
 * as fontes externas; a util getMarketFeed ainda tem cache por processo.
 */
export const revalidate = 300;

export async function GET() {
  try {
    const feed = await getMarketFeed();
    return NextResponse.json(feed, {
      headers: { "cache-control": "public, max-age=300, stale-while-revalidate=600" },
    });
  } catch {
    return NextResponse.json(
      { items: [], fetchedAt: new Date().toISOString(), degraded: true },
      { status: 503 },
    );
  }
}