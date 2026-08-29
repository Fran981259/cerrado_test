import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import "./globals.css";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800", "900"],
  variable: "--font-montserrat",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Atualiza Brasil — Notícias de Mato Grosso do Sul",
    template: "%s | Atualiza Brasil",
  },
  description: "Portal de notícias de Mato Grosso do Sul. Política, economia, segurança, agronegócio e tecnologia com atualização 24 horas.",
  keywords: ["notícias", "Mato Grosso do Sul", "Campo Grande", "MS", "política", "economia"],
  authors: [{ name: "Atualiza Brasil" }],
  openGraph: {
    type: "website",
    locale: "pt_BR",
    siteName: "Atualiza Brasil",
    title: "Atualiza Brasil — Notícias de MS",
    description: "Portal de notícias de Mato Grosso do Sul com atualização 24h.",
  },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://atualizabrasil.news"),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${montserrat.variable} h-full`}>
      <body className="min-h-full flex flex-col bg-[#f8f9fa] antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
