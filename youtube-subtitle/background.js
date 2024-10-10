chrome.webNavigation.onCommitted.addListener((details) => {
    if (!details.url.includes("youtube.com/watch")) { return; }
    if (details.frameId === 0) {
      chrome.scripting.executeScript({ target: { tabId: details.tabId }, files: ['content.js'] });
    }
});
  