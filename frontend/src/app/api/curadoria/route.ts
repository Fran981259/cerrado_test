import { NextResponse } from "next/server";

export async function GET() {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://portal_cerrado:8000";
    const res = await fetch(`${backendUrl}/api/editorial/review`, {
      headers: { "X-API-Key": "cerrado123" },
      cache: "no-store",
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
