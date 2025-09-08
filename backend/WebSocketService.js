const WebSocket = require('ws');
const axios = require('axios');

// 创建 WebSocket 服务器
const wss = new WebSocket.Server({ port: 3002 }); // 确保使用端口 3002
let clients = [];

// WebSocket 连接管理
wss.on('connection', (ws) => {
  clients.push(ws);

  // 接收到消息时的处理逻辑
  ws.on('message', async (message) => {
    console.log(`Received: ${message}`);

    // 解析消息并根据类型处理不同的逻辑
    const data = JSON.parse(message);

    // 处理不同类型的事件
    if (data.type === 'weather_alert') {
      // Weather alert received, trigger safety check
      await triggerSafetyInspection(ws, data.payload);
    } else if (data.type === 'safety_monitor') {
      // Safety monitor result, decide fire response
      handleSafetyMonitorResult(ws, data.payload);
    } else if (data.type === 'fire_response') {
      // Fire response sent
      handleFireResponse(ws, data.payload);
    }
  });

  ws.on('close', () => {
    clients = clients.filter(client => client !== ws);
  });
});

// 触发安全巡检
async function triggerSafetyInspection(ws, alertData) {
  // 模拟安全巡检逻辑，返回巡检结果
  const result = {
    status: 'OK', // 或者是 Warning, Incident
    location: alertData.location,
  };

  // 发送巡检任务给下游智能体
  ws.send(JSON.stringify({
    type: 'safety_monitor',
    payload: result,
  }));

  // 输出天气告警和巡检任务处理结果
  console.log(`Weather alert received for ${alertData.location}`);
  console.log(`Safety inspection result for ${alertData.location}: ${result.status}`);

  // 生成城市报告
  generateCityReport(ws, result);
}

// 处理安全巡检结果
function handleSafetyMonitorResult(ws, safetyData) {
  let fireResponse;

  switch (safetyData.status) {
    case 'OK':
      fireResponse = { level: 'low', units: 2 };
      break;
    case 'Warning':
      fireResponse = { level: 'medium', units: 5 };
      break;
    case 'Incident':
      fireResponse = { level: 'high', units: 10 };
      break;
    default:
      fireResponse = { level: 'unknown', units: 0 };
  }

  // 发送消防响应
  ws.send(JSON.stringify({
    type: 'fire_response',
    payload: fireResponse,
  }));

  console.log(`Fire response dispatched: ${JSON.stringify(fireResponse)}`);
}

// 处理消防响应
function handleFireResponse(ws, fireData) {
  console.log(`Fire response sent: ${JSON.stringify(fireData)}`);

  // 生成城市分析报告
  generateCityReport(ws, fireData);
}

// 生成城市报告
async function generateCityReport(ws, fireData) {
  const reportData = {
    timestamp: new Date().toISOString(),
    fire_level: fireData.level,
    units_dispatched: fireData.units,
  };

  // 生成报告并调用 DeepSeek API
  try {
    const report = await generateReportWithDeepSeek(reportData);
    ws.send(JSON.stringify({
      type: 'city_report',
      payload: { report },
    }));
    console.log(`City report generated: ${report}`);
  } catch (error) {
    console.error("Error generating city report:", error);
  }
}

// 调用 DeepSeek API 生成报告
async function generateReportWithDeepSeek(reportData) {
  const deepSeekAPI = 'https://api.deepseek.com/v1/chat/completions';  // DeepSeek API 地址
  const deepSeekAPIKey = 'sk-0d28f0a94ab746bbb8ed83ec74698e4d';  // 替换为你的 DeepSeek API 密钥

  try {
    const response = await axios.post(deepSeekAPI, {
      messages: [
        {
          role: "system",
          content: `You are an assistant that helps generate city analysis reports. Here's the data: ${JSON.stringify(reportData)}`
        }
      ],
      model: "deepseek-chat",  // 假设 DeepSeek 使用该模型（可以根据实际调整）
    }, {
      headers: {
        'Authorization': `Bearer ${deepSeekAPIKey}`,
        'Content-Type': 'application/json',
      }
    });

    // 返回生成的报告内容
    return response.data.choices[0].message.content;
  } catch (error) {
    console.error("Error generating report with DeepSeek:", error);
    throw new Error("Failed to generate report.");
  }
}

module.exports = { wss };  // 导出 WebSocket 服务器，以便在其他文件中引用
