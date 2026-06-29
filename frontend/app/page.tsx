import Link from "next/link";

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-20">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          排水管道缺陷智能检测与评估系统
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto">
          融合轻量化目标检测模型与多模态大语言模型，通过"先检测、后评估"的两阶段协同架构，
          实现从视觉定位到语义判断的完整诊断链路。
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Link
          href="/chat"
          className="card hover:border-primary-300 hover:shadow-md transition-all group"
        >
          <div className="text-3xl mb-3">💬</div>
          <h2 className="text-xl font-semibold mb-2 group-hover:text-primary-600">
            问答模式
          </h2>
          <p className="text-gray-500 text-sm">
            交互式单图分析，支持多轮对话、标准知识查询、追问质疑。
            适合疑难缺陷分析、教学演示和标准学习。
          </p>
          <ul className="mt-3 text-xs text-gray-400 space-y-1">
            <li>✓ 实时对话流式推送</li>
            <li>✓ 检测结果可视化叠加</li>
            <li>✓ 标准知识库查询</li>
            <li>✓ 单图评估报告导出</li>
          </ul>
        </Link>

        <Link
          href="/batch"
          className="card hover:border-primary-300 hover:shadow-md transition-all group"
        >
          <div className="text-3xl mb-3">📊</div>
          <h2 className="text-xl font-semibold mb-2 group-hover:text-primary-600">
            批量模式
          </h2>
          <p className="text-gray-500 text-sm">
            多图自动检测→评估→生成综合报告。一键启动，自动流水线执行。
            适合工程项目批量检测和日常巡检。
          </p>
          <ul className="mt-3 text-xs text-gray-400 space-y-1">
            <li>✓ 多图/文件夹/ZIP 上传</li>
            <li>✓ 自动批量检测评估</li>
            <li>✓ 实时进度追踪</li>
            <li>✓ 综合 Word 报告下载</li>
          </ul>
        </Link>
      </div>

      <div className="mt-12 text-center text-sm text-gray-400">
        <p>评估标准：CJJ 181-2012《城镇排水管道检测与评估技术规程》</p>
        <p className="mt-1">
          AI辅助评估定位为辅助决策参考，不替代正式检测成果表
        </p>
      </div>
    </div>
  );
}
