import type { Metadata } from "next";
import { Zilla_Slab, Inter } from "next/font/google";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import "./globals.css";

const zilla = Zilla_Slab({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-zilla-slab",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
});

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
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://portalcerrado.com.br"),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${zilla.variable} ${inter.variable} h-full`}>
      <body className="min-h-full flex flex-col font-sans antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
