const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const axios = require("axios");

const app = express();
const server = http.createServer(app);

// 创建 WebSocket 服务器
const wss = new WebSocket.Server({ server });

app.use(express.json());

let clients = [];

// WebSocket 连接管理
wss.on("connection", (ws) => {
  clients.push(ws);

  ws.on("close", () => {
    clients = clients.filter((client) => client !== ws);
  });
});

// 发送天气警告事件
app.post("/events/weather_alert", (req, res) => {
  const { alert_type, location } = req.body;
  console.log(`Weather alert received: ${alert_type} for ${location}`);
  
  // 模拟安全巡检结果
  const safetyStatus = "OK"; // 假设巡检结果为OK

  clients.forEach(client => {
    client.send(JSON.stringify({
      type: "safety_monitor",
      payload: { status: safetyStatus, location },
    }));
  });

  res.json({ status: "Weather alert sent" });
});

// 生成城市报告
app.post('/generate-report', async (req, res) => {
  const { weatherAlert, safetyStatus, location, trafficCondition } = req.body;
  const reportData = { weatherAlert, safetyStatus, location, trafficCondition };

  try {
    const report = await generateReportWithDeepSeek(reportData);  // 调用 DeepSeek API
    res.json({ report });  // 返回生成的报告
  } catch (error) {
    res.status(500).send('Error generating report');
  }
});

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

// 启动服务器
server.listen(3002, () => {
  console.log("Server is listening on port 3002");
});
