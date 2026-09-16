import { NextResponse } from "next/server";

export async function GET() {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://portal_cerrado:8000";
    const apiKey = process.env.PUBLISH_API_KEY || "sua_chave_secreta_aqui";
    const res = await fetch(`${backendUrl}/api/editorial/review`, {
      headers: { "X-API-Key": apiKey },
      cache: "no-store",
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
