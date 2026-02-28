import { NextRequest, NextResponse } from "next/server";

const BACKEND = "http://localhost:8000";

// 150s — enough for MiniMax-M2.5 batch formatting (parallelised on backend)
const TIMEOUT_MS = 150_000;

async function proxy(req: NextRequest, slug: string[]): Promise<NextResponse> {
  // slug strips the /api/ prefix (that's the route directory), so re-add it
  const path = "/api/" + slug.join("/");
  const search = req.nextUrl.search ?? "";
  const url = BACKEND + path + search;

  try {
    const init: RequestInit = {
      method: req.method,
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    };

    if (req.method !== "GET" && req.method !== "HEAD") {
      init.body = await req.text();
    }

    const upstream = await fetch(url, init);
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    const isTimeout = msg.includes("timeout") || msg.includes("abort");
    return NextResponse.json(
      { error: isTimeout ? "Backend timed out (>120s)" : msg },
      { status: isTimeout ? 504 : 502 },
    );
  }
}

export async function GET(
  req: NextRequest,
  { params }: { params: { slug: string[] } },
) {
  return proxy(req, params.slug);
}

export async function POST(
  req: NextRequest,
  { params }: { params: { slug: string[] } },
) {
  return proxy(req, params.slug);
}
