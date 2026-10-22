import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DocuNorm AI | Regulatory Document Audit Platform",
  description: "Privacy-first European compliance and regulatory document intelligence (DORA, LkSG, ZUGFeRD).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full dark">
      <body className="h-full bg-slate-950 text-slate-100 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}