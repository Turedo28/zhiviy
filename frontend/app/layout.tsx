import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HealthTrack — Твоє здоров'я. Одна платформа.",
  description: "Відстежуй харчування, сон, відновлення та тренування з AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uk">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
