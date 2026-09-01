export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if ((request.method === "GET" || request.method === "HEAD") && /^\/papers\/?$/.test(url.pathname)) {
      return env.ASSETS.fetch(
        new Request(new URL("/papers/index.html", url), request),
      );
    }

    if (request.method === "GET" && /^\/macos\/?$/.test(url.pathname)) {
      return env.ASSETS.fetch(
        new Request(new URL("/macos/index.html", url), request),
      );
    }

    const response = await env.ASSETS.fetch(request);
    if (response.status !== 404) return response;

    if (request.method === "GET" && !url.pathname.includes(".")) {
      return env.ASSETS.fetch(new Request(new URL("/index.html", url), request));
    }

    return response;
  },
};
