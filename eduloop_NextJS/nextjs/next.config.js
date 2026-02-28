/** @type {import('next').NextConfig} */
const nextConfig = {
  // /api/* is handled by app/api/[...slug]/route.ts which proxies to FastAPI
  // with a 120s timeout — needed for MiniMax-M2.5 extended thinking calls.
};

module.exports = nextConfig;
