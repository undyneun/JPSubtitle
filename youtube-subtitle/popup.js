var hasFile = false
var apiKey;
var serverIP = env.serverIP;

const getTab = () => {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0) {
        resolve(tabs[0]);
      } else {
        reject('No active tab found');
      }
    });
  });
};

document.addEventListener('DOMContentLoaded', async () => {
  // 保存已輸入的 apiKey 到輸入框
  const apiKeyInput = document.getElementById('apiKey');
  apiKeyInput.value = localStorage.getItem('openaiApiKey');
  apiKey = apiKeyInput.value;
  
  apiKeyInput.addEventListener('input', () => { 
    localStorage.setItem('openaiApiKey', apiKeyInput.value) 
    apiKey = localStorage.getItem('openaiApiKey');
  })

  // 如果不是 YouTube 影片頁面，顯示提示訊息並隱藏按鈕
  const tab = await getTab()
  if (tab.url.includes("youtube.com/watch")) { return }
  document.getElementById('splitButton').style.display = 'none';
  document.getElementById('notEffective').style.display = 'block';
});


document.getElementById('splitButton').addEventListener('click', async () => {
  const tab = await getTab()
  chrome.scripting.insertCSS({
    target: { tabId: tab.id }, files: ['styles.css']
  }, () => {
    chrome.scripting.executeScript({ 
      target: { tabId: tab.id },
      args: [serverIP, apiKey, hasFile],
      function: (serverIP, apiKey, hasFile) => applyCustomLayout(serverIP, apiKey, hasFile)
    });
  });
  setTimeout(()=>{ hasFile = false }, 1000)
});


document.getElementById('submit').addEventListener('click', async () => {
  const apiKey = document.getElementById('apiKey').value;
  const file = document.getElementById("subtitleFile").files[0];
  const formData = new FormData();
  formData.append('file', file);
  formData.append('apiKey', apiKey);

  if (file) {
    hasFile = true;
    try {
      const response = await fetch(`${serverIP}/parse`, { method: 'POST', body: formData })
      const json = await response.json()
      sendData(json, "subtitleJson")
      const tab = await getTab()
      chrome.scripting.executeScript({ target: { tabId: tab.id },
        function: () => fillSubtitleContainer()
      });
    } catch (error) {
      console.error('上傳文件時出錯:', error)
    }
  }
})

const sendData = async (data, name) => {
  const tab = await getTab();
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    args: [data, name],
    func: (data, name) => { window[name] = data }
  });
};