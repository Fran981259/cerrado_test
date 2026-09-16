import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
