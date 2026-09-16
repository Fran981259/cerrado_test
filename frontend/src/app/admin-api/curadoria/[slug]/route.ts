import { NextResponse } from "next/server";

export async function PUT(request: Request, { params }: { params: Promise<{ slug: string }> }) {
  try {
    const { slug } = await params;
    const body = await request.json();
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://portal_cerrado:8000";
    const apiKey = process.env.PUBLISH_API_KEY || "sua_chave_secreta_aqui";
    const res = await fetch(`${backendUrl}/api/editorial/review/${slug}`, {
      method: "PUT",
      headers: { 
        "Content-Type": "application/json",
        "X-API-Key": apiKey
      },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
