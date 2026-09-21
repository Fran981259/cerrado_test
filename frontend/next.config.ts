import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // O executor CLI do TypeScript perde stdout neste ambiente Node 22, fazendo
  // o Next falhar ao interpretar `tsc --showConfig`. O compilador via API é o
  // caminho padrão e estável para TypeScript 5.x.
  experimental: {
    useTypeScriptCli: false,
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "picsum.photos" },
      { protocol: "https", hostname: "**.picsum.photos" },
      { protocol: "https", hostname: "**.midiamax.com.br" },
      { protocol: "https", hostname: "**.campograndenews.com.br" },
      { protocol: "https", hostname: "**.correiodoestado.com.br" },
      { protocol: "https", hostname: "**.capitalnews.com.br" },
      { protocol: "https", hostname: "**" },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://portal_cerrado:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
