const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
}

export default async function handler(request: Request): Promise<Response> {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: CORS })
  }

  if (request.method !== 'POST') {
    return Response.json(
      { error: { message: 'Method not allowed' } },
      { status: 405, headers: { ...CORS, Allow: 'POST' } },
    )
  }

  const key = process.env.GROQ_API_KEY?.trim()
  if (!key) {
    return Response.json(
      { error: { message: 'GROQ_API_KEY is not configured on this deployment.' } },
      { status: 503, headers: CORS },
    )
  }

  const body = await request.text()

  try {
    const upstream = await fetch(GROQ_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${key}`,
      },
      body,
    })

    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: {
        ...CORS,
        'Content-Type': upstream.headers.get('content-type') ?? 'application/json',
      },
    })
  } catch {
    return Response.json(
      { error: { message: 'Could not reach Groq API.' } },
      { status: 502, headers: CORS },
    )
  }
}
