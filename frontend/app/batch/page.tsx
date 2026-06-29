"use client";

import { useState, useRef } from "react";

interface BatchProgress {
  task_id: string;
  status: string;
  total: number;
  processed: number;
  current_image?: string;
  errors: Array<{ image: string; error: string }>;
}

export default function BatchPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState<BatchProgress | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files;
    if (selected) setFiles(Array.from(selected));
  };

  const startBatch = async () => {
    if (files.length === 0) return;
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    formData.append("llm_provider", "cloud");
    setIsRunning(true);

    try {
      const res = await fetch("http://localhost:8080/api/batch/start", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setTaskId(data.task_id);

      intervalRef.current = setInterval(async () => {
        const statusRes = await fetch(
          `http://localhost:8080/api/batch/${data.task_id}/status`
        );
        const status = await statusRes.json();
        setProgress(status);
        if (status.status === "completed" || status.status === "error") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          setIsRunning(false);
        }
      }, 2000);
    } catch (err) {
      console.error("Batch start failed:", err);
      setIsRunning(false);
    }
  };

  const progressPercent =
    progress && progress.total > 0
      ? Math.round((progress.processed / progress.total) * 100)
      : 0;

  const statusLabel: Record<string, string> = {
    pending: "等待中",
    detecting: "检测中",
    evaluating: "评估中",
    generating_report: "生成报告中",
    completed: "已完成",
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">上传图像</h2>
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-400 transition-colors"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          <div className="text-3xl mb-2">📷</div>
          <p className="text-gray-500">
            {files.length > 0
              ? `已选择 ${files.length} 张图像`
              : "点击选择多张图像（支持多选）"}
          </p>
        </div>
        {files.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {files.map((f, i) => (
              <span key={i} className="text-xs bg-gray-100 px-2 py-1 rounded">
                {f.name}
              </span>
            ))}
          </div>
        )}
        <button
          onClick={startBatch}
          disabled={files.length === 0 || isRunning}
          className="btn-primary mt-4 w-full"
        >
          {isRunning ? "处理中..." : "开始批量处理"}
        </button>
      </div>

      {progress && (
        <div className="card space-y-4">
          <h2 className="text-lg font-semibold">处理进度</h2>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-primary-600 h-4 rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className="flex justify-between text-sm text-gray-500">
            <span>
              {progress.processed} / {progress.total} ({progressPercent}%)
            </span>
            <span>{statusLabel[progress.status] || progress.status}</span>
          </div>
          {progress.current_image && (
            <p className="text-sm text-gray-400">
              当前处理: {progress.current_image}
            </p>
          )}
          {progress.errors.length > 0 && (
            <div className="mt-2 p-3 bg-red-50 rounded-lg text-sm text-red-600">
              <p className="font-medium">处理错误:</p>
              {progress.errors.map((e, i) => (
                <p key={i}>
                  {e.image}: {e.error}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {progress?.status === "completed" && taskId && (
        <div className="text-center">
          <a
            href={`http://localhost:8080/api/batch/${taskId}/report`}
            className="btn-primary inline-block"
            download
          >
            下载综合评估报告 (Word)
          </a>
        </div>
      )}
    </div>
  );
}
