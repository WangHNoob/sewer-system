"use client";

import { useState, useEffect } from "react";

interface LLMPreset {
  name: string;
  provider: string;
  model_name: string;
  base_url: string;
}

export default function SettingsPage() {
  const [presets, setPresets] = useState<LLMPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>("");
  const [apiKey, setApiKey] = useState("");
  const [temperature, setTemperature] = useState(0.1);
  const [maxTokens, setMaxTokens] = useState(4096);
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetch("http://localhost:8080/api/config/llm/presets")
      .then((r) => r.json())
      .then(setPresets)
      .catch(console.error);
  }, []);

  const handleSave = async () => {
    const preset = presets.find((p) => p.model_name === selectedPreset);
    if (!preset) return;

    try {
      const res = await fetch("http://localhost:8080/api/config/llm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider: preset.provider,
          model_name: preset.model_name,
          api_key: apiKey || null,
          base_url: preset.base_url,
          temperature,
          max_tokens: maxTokens,
        }),
      });
      const data = await res.json();
      setStatus(`配置已保存: ${data.model}`);
    } catch (err) {
      setStatus("保存失败");
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">模型配置</h1>

      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">LLM 模型</label>
          <select
            value={selectedPreset}
            onChange={(e) => setSelectedPreset(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">请选择模型</option>
            {presets.map((p) => (
              <option key={p.model_name} value={p.model_name}>
                {p.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="输入 API Key（云端模型需要）"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Temperature ({temperature})
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Max Tokens ({maxTokens})
            </label>
            <input
              type="number"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <button onClick={handleSave} className="btn-primary w-full">
          保存配置
        </button>

        {status && (
          <p className="text-sm text-center text-green-600">{status}</p>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-2">模型说明</h2>
        <div className="text-sm text-gray-500 space-y-2">
          <p>
            <strong>云端模式</strong>：使用通义千问 VL API 或 GPT-4o，需要 API
            Key。图像经 base64 编码传输至云端。
          </p>
          <p>
            <strong>本地模式</strong>：使用本地 vLLM 部署的 Qwen3-VL-8B，数据不出本机，适合敏感工程数据。
          </p>
          <p className="text-xs text-gray-400 mt-2">
            注意：本地模式需要先启动 vLLM 服务（默认端口 8000）。
          </p>
        </div>
      </div>
    </div>
  );
}
