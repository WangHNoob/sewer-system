import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "PipeAI - 排水管道缺陷智能检测与评估系统",
  description: "端到端的排水管道缺陷智能诊断平台",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/" className="font-bold text-lg text-primary-700">
                PipeAI
              </Link>
              <div className="flex gap-1">
                <Link
                  href="/chat"
                  className="px-3 py-1.5 rounded-md text-sm hover:bg-gray-100 transition-colors"
                >
                  问答模式
                </Link>
                <Link
                  href="/batch"
                  className="px-3 py-1.5 rounded-md text-sm hover:bg-gray-100 transition-colors"
                >
                  批量模式
                </Link>
              </div>
            </div>
            <Link
              href="/settings"
              className="px-3 py-1.5 rounded-md text-sm text-gray-500 hover:bg-gray-100 transition-colors"
            >
              模型配置
            </Link>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
