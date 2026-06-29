"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import useWebSocket from "react-use-websocket";

interface Message {
  role: "user" | "ai" | "system";
  content: string;
  timestamp: number;
}

interface DetectionResult {
  detections: Array<{
    class_code: string;
    class_name: string;
    confidence: number;
    bbox_pixels: { x1: number; y1: number; x2: number; y2: number };
    position_description: string;
  }>;
  total_defects: number;
  image_size: { width: number; height: number };
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [detectionResult, setDetectionResult] =
    useState<DetectionResult | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [inputText, setInputText] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [aiStreaming, setAiStreaming] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
    `ws://localhost:8080/api/chat/ws`,
    {
      onOpen: () => console.log("WebSocket connected"),
      shouldReconnect: () => true,
    }
  );

  useEffect(() => {
    if (!lastJsonMessage) return;
    const msg = lastJsonMessage as any;

    switch (msg.type) {
      case "session":
        console.log("Session:", msg.session_id);
        break;
      case "detection_result":
        setDetectionResult(msg.data);
        break;
      case "token":
        setAiStreaming((prev) => prev + msg.data);
        break;
      case "tool_call":
        addMessage("system", `🔧 调用工具: ${msg.data.tool}`);
        break;
      case "tool_result":
        addMessage("system", `📋 工具返回结果`);
        break;
    }
  }, [lastJsonMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, aiStreaming]);

  const addMessage = useCallback(
    (role: Message["role"], content: string) => {
      setMessages((prev) => [...prev, { role, content, timestamp: Date.now() }]);
    },
    []
  );

  const handleSend = () => {
    if (!inputText.trim()) return;
    addMessage("user", inputText);
    sendJsonMessage({ type: "text", content: inputText });
    setInputText("");
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const base64 = (reader.result as string).split(",")[1];
      setUploadedImage(reader.result as string);
      setDetectionResult(null);
      setAiStreaming("");
      setIsProcessing(true);

      const prompt = inputText || "请评估图像中的缺陷";
      addMessage("user", `[上传图像] ${prompt}`);
      sendJsonMessage({
        type: "image",
        image_base64: base64,
        content: prompt,
      });
      setInputText("");
    };
    reader.readAsDataURL(file);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <div className="w-[380px] border-r bg-white p-4 flex flex-col gap-4 overflow-y-auto">
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-primary-400 transition-colors"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
          {uploadedImage ? (
            <div className="relative">
              <img
                src={uploadedImage}
                alt="Uploaded"
                className="w-full rounded-lg"
              />
              {detectionResult && (
                <div className="absolute inset-0">
                  {detectionResult.detections.map((d, i) => (
                    <div
                      key={i}
                      className="absolute border-2 border-red-500 bg-red-500/10 rounded"
                      style={{
                        left: `${(d.bbox_pixels.x1 / detectionResult.image_size.width) * 100}%`,
                        top: `${(d.bbox_pixels.y1 / detectionResult.image_size.height) * 100}%`,
                        width: `${((d.bbox_pixels.x2 - d.bbox_pixels.x1) / detectionResult.image_size.width) * 100}%`,
                        height: `${((d.bbox_pixels.y2 - d.bbox_pixels.y1) / detectionResult.image_size.height) * 100}%`,
                      }}
                    >
                      <span className="absolute -top-5 left-0 text-xs bg-red-500 text-white px-1 rounded">
                        {d.class_name} {Math.round(d.confidence * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="py-8 text-gray-400">
              <div className="text-3xl mb-2">📷</div>
              <p className="text-sm">点击上传 CCTV 检测图像</p>
            </div>
          )}
        </div>

        {detectionResult && (
          <div className="card">
            <h3 className="font-medium text-sm mb-2">
              检测结果 ({detectionResult.total_defects} 处缺陷)
            </h3>
            <div className="space-y-2">
              {detectionResult.detections.map((d, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="font-medium">{d.class_name}</span>
                  <span className="text-gray-400">
                    {Math.round(d.confidence * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === "user"
                    ? "bg-primary-600 text-white"
                    : msg.role === "system"
                      ? "bg-gray-100 text-gray-500 text-sm"
                      : "bg-gray-100 text-gray-900"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {aiStreaming && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg px-4 py-2 bg-gray-100 text-gray-900">
                {aiStreaming}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入消息，或上传图像后自动分析..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              onClick={handleSend}
              disabled={!inputText.trim()}
              className="btn-primary"
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
