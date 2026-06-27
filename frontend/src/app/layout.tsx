import type { Metadata } from "next";
import { Sora, Noto_Serif_Devanagari } from "next/font/google";
import "./globals.css";

const sora = Sora({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-sora",
  display: "swap",
});

const devanagari = Noto_Serif_Devanagari({
  subsets: ["devanagari"],
  weight: ["600", "700"],
  variable: "--font-devanagari",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Kisan Samman — किसान सम्मान",
  description:
    "Discover government welfare schemes you qualify for — in your language, in under 30 seconds.",
  icons: { icon: "/icon.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sora.variable} ${devanagari.variable}`}>
      <body>{children}</body>
    </html>
  );
}