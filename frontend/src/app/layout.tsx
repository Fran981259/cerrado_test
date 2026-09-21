import type { Metadata } from "next";
import "@fontsource/inter/latin-400.css";
import "@fontsource/inter/latin-500.css";
import "@fontsource/inter/latin-600.css";
import "@fontsource/zilla-slab/latin-400.css";
import "@fontsource/zilla-slab/latin-500.css";
import "@fontsource/zilla-slab/latin-600.css";
import "@fontsource/zilla-slab/latin-700.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { getPublicSiteUrl } from "@/lib/siteUrl";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Portal Cerrado — Notícias de Mato Grosso do Sul",
    template: "%s | Portal Cerrado",
  },
  description: "Portal de notícias de Mato Grosso do Sul. Política, economia, segurança, agronegócio e tecnologia com atualização 24 horas.",
  keywords: ["notícias", "Mato Grosso do Sul", "Campo Grande", "MS", "política", "economia"],
  authors: [{ name: "Portal Cerrado" }],
  openGraph: {
    type: "website",
    locale: "pt_BR",
    siteName: "Portal Cerrado",
    title: "Portal Cerrado — Notícias de MS",
    description: "Portal de notícias de Mato Grosso do Sul com atualização 24h.",
  },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
  metadataBase: new URL(getPublicSiteUrl()),
};

import { Tracker } from "@/components/Tracker";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="h-full">
      <head>
        <link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-regular-rounded/css/uicons-regular-rounded.css" />
        <link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css" />
      </head>
      <body className="min-h-full flex flex-col font-sans antialiased">
        <Tracker />
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
