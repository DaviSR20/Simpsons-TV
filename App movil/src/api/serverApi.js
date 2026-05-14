function trimTrailingSlash(value) {
  return value.replace(/\/+$/, "");
}

export function normalizeBaseUrl(value) {
  if (!value) {
    return "";
  }

  const trimmed = value.trim();
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
    return trimTrailingSlash(trimmed);
  }

  return trimTrailingSlash(`http://${trimmed}`);
}

export function parseQrPayload(payload) {
  const normalized = normalizeBaseUrl(payload);
  const url = new URL(normalized);
  return {
    baseUrl: `${url.protocol}//${url.host}`,
    host: url.hostname,
    port: url.port ? Number(url.port) : 80,
  };
}

async function requestJson(baseUrl, path, { method = "GET", pin, body } = {}) {
  const headers = {};
  if (pin) {
    headers["X-Web-Pin"] = pin;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${trimTrailingSlash(baseUrl)}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await response.text();
  let payload = {};
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = { raw: text };
  }

  if (!response.ok) {
    const message = payload?.error || `HTTP ${response.status}`;
    throw new Error(message);
  }

  return payload;
}

export async function fetchIp(baseUrl) {
  return requestJson(baseUrl, "/ip");
}

export async function authenticate(baseUrl, pin) {
  return requestJson(baseUrl, "/web/auth", {
    method: "POST",
    body: { pin },
  });
}

export async function fetchHealth(baseUrl, pin) {
  return requestJson(baseUrl, "/health", { pin });
}

export async function fetchVideos(baseUrl, pin) {
  return requestJson(baseUrl, "/videos", { pin });
}

export async function fetchNow(baseUrl, pin) {
  return requestJson(baseUrl, "/now", { pin });
}

export async function ledOn(baseUrl, pin) {
  return requestJson(baseUrl, "/led/on", {
    method: "POST",
    pin,
    body: {},
  });
}

export async function ledOff(baseUrl, pin) {
  return requestJson(baseUrl, "/led/off", {
    method: "POST",
    pin,
    body: {},
  });
}

export async function playEpisode(baseUrl, pin, id, directory) {
  return requestJson(baseUrl, "/play", {
    method: "POST",
    pin,
    body: {
      id,
      directory,
    },
  });
}

export async function stopPlayback(baseUrl, pin) {
  return requestJson(baseUrl, "/stop", {
    method: "POST",
    pin,
    body: {},
  });
}

export async function volumeUp(baseUrl, pin) {
  return requestJson(baseUrl, "/volume/up", {
    method: "POST",
    pin,
    body: {},
  });
}

export async function volumeDown(baseUrl, pin) {
  return requestJson(baseUrl, "/volume/down", {
    method: "POST",
    pin,
    body: {},
  });
}
