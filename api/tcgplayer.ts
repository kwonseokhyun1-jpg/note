const TCGPLAYER_ORIGIN = 'https://infinite-api.tcgplayer.com'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
  'Access-Control-Allow-Headers': 'Accept',
}

function buildUpstreamUrl(request: Request): string | null {
  const url = new URL(request.url)
  const path = url.searchParams.get('path')?.trim()
  if (!path) return null

  const params = new URLSearchParams()
  for (const [key, value] of url.searchParams.entries()) {
    if (key === 'path') continue
    params.append(key, value)
  }

  const qs = params.toString()
  return `${TCGPLAYER_ORIGIN}/${path}${qs ? `?${qs}` : ''}`
}

export default async function handler(request: Request): Promise<Response> {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: CORS })
  }

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    return Response.json(
      { error: { message: 'Method not allowed' } },
      { status: 405, headers: { ...CORS, Allow: 'GET, HEAD' } },
    )
  }

  const upstreamUrl = buildUpstreamUrl(request)
  if (!upstreamUrl) {
    return Response.json(
      { error: { message: 'Missing TCGPlayer API path.' } },
      { status: 400, headers: CORS },
    )
  }

  try {
    const upstream = await fetch(upstreamUrl, {
      method: request.method,
      headers: {
        Accept: 'application/json',
        Origin: 'https://www.tcgplayer.com',
        Referer: 'https://www.tcgplayer.com/',
        'User-Agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      },
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
      { error: { message: 'Could not reach TCGPlayer API.' } },
      { status: 502, headers: CORS },
    )
  }
}
