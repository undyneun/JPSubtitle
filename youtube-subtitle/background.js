var hasLoaded = false;

chrome.webNavigation.onCommitted.addListener(details => {
  if (details.frameId !== 0) return;
  if (details.transitionType === "reload") hasLoaded = false;
  fn(details);
});

chrome.webNavigation.onHistoryStateUpdated.addListener(details => {
  if (details.frameId !== 0) return;
  fn(details)
});

const fn = (details) => {
  if (!hasLoaded && details.url.includes("youtube.com/watch")) {
    chrome.scripting.executeScript({ target: { tabId: details.tabId }, files: ['content.js'] });
    hasLoaded = true
  }
}