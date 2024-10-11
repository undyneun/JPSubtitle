console.log("JPsubtitle已加載");

var serverIP;
var count;
var resizerY;
var nowVocab = '';
var hasMeaning = false;
var originalText = "", CrawlerJson = {}, subtitleData = [], timestampData = [];
var isHalfFull, isResizing = false, isDragging = false;
var openaiApiKey;
var moviePlayer, moviePlayerParent, ytpSizeBtn;
var offsety, startX, startLeft;

// 按鍵
const handle = {
  async dictChange(e) {
    if (['ArrowRight', 'ArrowLeft'].includes(e.key)) {
      if (document.activeElement !== subtitleSearchContainer) return

      e.preventDefault()
      e.stopPropagation();
      if (!hasMeaning) return

      if (e.key === 'ArrowRight' && count < CrawlerJson.length) { count += 1  }
      if (e.key === 'ArrowLeft' && count > 1) { count -= 1  }
      await changeMean(CrawlerJson, count-1)
    }
  },
  pressEsc(e) { 
    if (e.key === 'Escape') handle.clickCloseBtn() 
  },
  clickWhisperBtn(e) {
    subtitleContainer.removeChild(e.currentTarget)
    withLoader(subtitleContainer, async () => {
      try {
        const jpJson = await getTranscription(serverIP, openaiApiKey, window.location.href)
        console.log(jpJson);
        if (jpJson[0]["line"] === "error: error") { 
          window.subtitleJson = [[{"origin": "忙碌中，請稍後再試","normalForm": "","kanji_index": "-1","kanji_reading": "none"}]]
        }
        else {
          const jpString = jpJson.map(dict => dict["line"]).join("\n")
          jpJson.forEach(dict => timestampData.push({ start: dict["start"], end: dict["end"] }))
          console.log(timestampData);
          window.subtitleJson = await getParse(serverIP, jpString)
        }
        fillSubtitleContainer();
      } catch (error) {
        console.error(error)
      }   
    })
  },
  clickResetBtn() {
    cc.replaceChildren();
    timestampData = [];
    subtitleData = [];
    originalText = "";
    subtitleContainer.replaceChildren()
    createWhisperBtn()
  },
  clickCloseBtn() {
    hideContainers() 
    document.removeEventListener('keydown', handle.dictChange, true)
    document.removeEventListener('keydown', handle.pressEsc)
  },
  clickjaOrZhBtn(e) {
    const textDiv = e.currentTarget.querySelector(".JPsubtitle-text")
    const chs = document.querySelectorAll('.JPsubtitle-chinese-subtitle');
    const origs = document.querySelectorAll('.JPsubtitle-original-subtitle');
    if (textDiv.innerText === "中") {
      chs.forEach(ch => { ch.style.fontSize = "15px";  ch.style.color = "rgb(156, 156, 156)" })
      origs.forEach(orig => orig.style.display = "")
      textDiv.innerText = "日中"
    }
    else if (textDiv.innerText === "日中") {
      chs.forEach(ch => ch.style.display = "none")
      textDiv.innerText = "日"
    }
    else {
      chs.forEach(ch => { ch.style.display = ""; ch.style.fontSize = "18px"; ch.style.color = "rgba(255, 255, 255, 0.71)" })
      origs.forEach(orig => orig.style.display = "none")
      textDiv.innerText = "中"
    }
  },
  async clickTranslateBtn() {
    if (subtitleData.length === 0) {return}
    try {
      window.translatedText = await getTranslate(serverIP, openaiApiKey, originalText)
      fillSubtitleContainer();
    } catch (error) {
      console.error(error)
    }   
  },
  resizeMousemove(e) {
    if (!isResizing) return;
    const containerRect = subtitleCombineContainer.getBoundingClientRect();
    const fnDivRect = functionContainer.getBoundingClientRect();
    const minY = fnDivRect.height+175; 
    const maxY = containerRect.height; 
    resizerY = e.clientY - containerRect.top;
    if (resizerY < minY) {resizerY = minY}
    if (resizerY > maxY) {resizerY = maxY}
    handle.windowResize();
  },
  resizeMouseup() {
    isResizing = false;
    subtitleContainer.classList.remove("no-select")
    subtitleSearchContainer.classList.remove("no-select")
    document.removeEventListener('mousemove', handle.resizeMousemove);
    document.removeEventListener('mouseup', handle.resizeMouseup);
  },
  resizeMousedown() {
    isResizing = true;
    subtitleContainer.classList.add("no-select")
    subtitleSearchContainer.classList.add("no-select")
    document.addEventListener('mousemove', handle.resizeMousemove);
    document.addEventListener('mouseup', handle.resizeMouseup);
  },
  windowResize() {
    const containerRect = subtitleCombineContainer.getBoundingClientRect();
    const fnDivRect = functionContainer.getBoundingClientRect();
    resizer.style.top = `${resizerY - 5}px`;
    subtitleContainer.style.height = `${resizerY - 5 - (fnDivRect.height)*2 + 15}px`;
    subtitleSearchContainer.style.height = `${containerRect.height - resizerY - fnDivRect.height + 5}px`;
  },
  ccMousemove(e) {
    if (!isDragging) { return; }
    cc.style.left = `${startLeft + (e.clientX - startX)}px`;
    cc.style.top = `${e.clientY - offsety}px`;
  },
  ccMouseup() {
    isDragging = false;
    cc.style.cursor = 'grab';
  },
  ccMousedown(e) {
    isDragging = true;
    startX = e.clientX;
    startLeft = cc.offsetLeft;
    offsety = e.clientY - cc.getBoundingClientRect().top;
    cc.style.cursor = 'grabbing';
  }
}

// TODO: 先把外觀弄好交比賽資料，字典loader之後再說
// 布局
const layoutContainer = getDiv('custom-layout', 'JPsubtitle-container');
  const videoCombineContainer = getDiv('videocombine-container', 'JPsubtitle-videocombine-container');
    const videoContainer = getDiv('video-container', 'JPsubtitle-video-container');
  const subtitleCombineContainer = getDiv('subtitlecombine-container', 'JPsubtitle-subtitlecombine-container');
    const functionContainer = getDiv('function-container', 'JPsubtitle-function-container');
    const subtitleContainer = getDiv('subtitle-container', 'JPsubtitle-subtitle-container');
    const resizer = getDiv('', 'JPsubtitle-resizer');
    const subtitleSearchContainer = getDiv('subtitlesearch-container', 'JPsubtitle-subtitlesearch-container');
      const meaningWrapper = getDiv('meaning-wrapper', 'JPsubtitle-meaning-wrapper');
        const originalWrapper = getDiv('original-wrapper', 'JPsubtitle-original-wrapper');
          const originalH2 = document.createElement('h2') // clicktoken
        const countResultWrapper = getDiv('countresult-wrapper', 'JPsubtitle-countresult-wrapper');
          const countH3 = document.createElement('h3') // clicktoken, changeMean
        const crawlerResultWrapper = getDiv('crawlerresult-wrapper', 'JPsubtitle-crawlerresult-wrapper');
          const meanExampleWrapper = getDiv('meanExample-wrapper',"JPsubtitle-meanExample-wrapper")
            const meanDiv = getDiv('token-mean', 'JPsubtitle-token-mean'); // clicktoken, changeMean
            const examplesDiv = getDiv('token-examples', 'JPsubtitle-token-examples'); // clicktoken, changeMean

countResultWrapper.appendChild(countH3)
meanExampleWrapper.append(meanDiv, examplesDiv)
crawlerResultWrapper.appendChild(meanExampleWrapper)
originalWrapper.appendChild(originalH2)
meaningWrapper.append(originalWrapper, countResultWrapper, crawlerResultWrapper)
subtitleSearchContainer.tabIndex = "0"
subtitleSearchContainer.appendChild(meaningWrapper)
videoCombineContainer.append(videoContainer);
subtitleCombineContainer.append(functionContainer,subtitleContainer, resizer, subtitleSearchContainer);
layoutContainer.append(videoCombineContainer, subtitleCombineContainer);
document.body.appendChild(layoutContainer);

// 字幕
const cc = getDiv('subtitle', 'no-select');
layoutContainer.append(cc);
cc.addEventListener('mousedown', handle.ccMousedown);
document.addEventListener('mouseup', handle.ccMouseup);
document.addEventListener('mousemove', handle.ccMousemove);

(() => {
  let nowSubtitle;
  setInterval(() => {
    cc.style.display = cc.hasChildNodes() ? 'block' : 'none';
    moviePlayer = document.querySelector('#movie_player');
    const video = moviePlayer.querySelector("video");
    if (!video) return;

    const curSec = video.currentTime;
    const curIdx = timestampData.findIndex(({ start, end }) => curSec >= start && curSec <= end);
    const nextSubtitle = subtitleContainer.children[curIdx];
    if (nextSubtitle && nextSubtitle.isEqualNode(nowSubtitle)) return; // 辨別內容而非指標

    nowSubtitle = nextSubtitle;
    if (!nowSubtitle) return;

    cc.replaceChildren();
    Array.from(subtitleContainer.children).forEach(child => child.style.backgroundColor = "");
    cc.append(nowSubtitle.cloneNode(true));
    subtitleContainer.scrollTop = nowSubtitle.offsetTop - subtitleContainer.offsetTop - (subtitleContainer.clientHeight / 2) + (nowSubtitle.clientHeight / 2);
    nowSubtitle.style.backgroundColor = "rgba(100, 100, 0, 0.3)";
  }, 100);
})()
  

// 影片
setTimeout(() => {
  moviePlayerParent = moviePlayer.parentNode
  ytpSizeBtn = document.querySelector('.ytp-size-button');
}, 3000)

// resizer
resizer.addEventListener('mousedown', handle.resizeMousedown);
window.onresize = handle.windowResize

// 建按鈕
createFnBtns()
createWhisperBtn()

// 主函數
async function applyCustomLayout(IP, apiKey, hasFile) {
  if (layoutContainer.style.zIndex === 10000) return;
  serverIP = IP;
  openaiApiKey = apiKey;
  document.addEventListener('keydown', handle.dictChange, true);
  document.addEventListener('keydown', handle.pressEsc);
  showContainers();
  handle.windowResize();

  if (hasFile) {
    await withLoader(subtitleContainer, async () => {
      if (!window.subtitleJson) await new Promise((resolve, reject) => {
        let count = 0
        const checkData = setInterval(() => {
          if (window[dataName] && window[dataName] !== '') { clearInterval(checkData);  resolve() }
          if (count >= 50) { clearInterval(checkData); reject() }
          count++
        }, 100);
      });
    });
    fillSubtitleContainer();
  } else {
    if (!subtitleContainer.hasChildNodes()) createWhisperBtn();
  }
}

function showContainers() {
  videoContainer.append(moviePlayer);
  setTimeout(() => { ytpSizeBtn.click() }, 100)
  if (ytpSizeBtn.getAttribute("data-title-no-tooltip") !== "預設檢視模式") {
    isHalfFull = false
  } else {
    isHalfFull = true
    setTimeout(() => setTimeout(() => { ytpSizeBtn.click() }, 100), 100);
  }
  document.documentElement.style.overflow = 'hidden';
  layoutContainer.style.zIndex = 10000
  layoutContainer.style.display = "flex"
}

function hideContainers() {
  moviePlayerParent.append(moviePlayer)
  setTimeout(() => { ytpSizeBtn.click() }, 100)
  setTimeout(() => { if (isHalfFull) {setTimeout(() => { ytpSizeBtn.click() }, 100)} }, 100)
  document.documentElement.style.overflow = 'auto';
  layoutContainer.style.zIndex = -1
  layoutContainer.style.display = "none"
}

// 主要功能
function getOriginalText() {
  return window.subtitleJson.map(sentenceArray => 
    sentenceArray.map(tokenDict => tokenDict.origin).join('')
  ).join('\n');
}

function getSubtitleData() {
  const subtitleData = window.subtitleJson.map((sentenceArray) => {
    return sentenceArray.map((tokenDict) => {
      const { origin, normalForm, kanji_index, kanji_reading } = tokenDict;
      const span = getTokenSpan(origin, kanji_index, kanji_reading)
      if (/[ぁ-んァ-ン一-龥]/.test(origin)) {
        span.addEventListener('mouseover', () => span.style.backgroundColor = 'rgba(100, 100, 100, 0.5)');
        span.addEventListener('mouseout', () => span.style.backgroundColor = '');
        span.addEventListener('click', () => { clickToken(origin, normalForm); });
        span.classList.add(normalForm)
      }
      return span;
    });
  });
  return subtitleData;
}

function fillSubtitleContainer() {
  if (!Array.isArray(window.subtitleJson)) {
    console.error("試著用字幕json, 但字幕json不是陣列");
    return;
  }

  subtitleContainer.replaceChildren();
  subtitleContainer.classList.remove("centerItems");
  const whisperDiv = document.getElementById("whisperDiv");
  if (whisperDiv) whisperDiv.remove();

  let translatedTextArray = [];
  if (window.translatedText) {
    translatedTextArray = window.translatedText.split('\n');
    console.log(window.translatedText);
  }

  originalText = getOriginalText();
  console.log(originalText);
  subtitleData = getSubtitleData();

  const originalTextArray = originalText.split('\n');
  originalTextArray.forEach((_, i) => {
    const subtitleWrapper = getDiv('', 'JPsubtitle-subtitle-wrapper');
    const orgSubtitleDiv = getDiv('', 'JPsubtitle-original-subtitle');
    const zhSubtitleDiv = getDiv('', 'JPsubtitle-chinese-subtitle');
    const zhSpan = document.createElement("span");

    subtitleWrapper.append(orgSubtitleDiv, zhSubtitleDiv);
    subtitleContainer.appendChild(subtitleWrapper);

    subtitleData[i].forEach(token => orgSubtitleDiv.appendChild(token));
    if (window.translatedText) {
      zhSpan.innerText = translatedTextArray[i] || "";
      zhSubtitleDiv.appendChild(zhSpan);
    }
  });
}

function getTokenSpan(origin, kanji_index, kanji_reading) {
  const span = document.createElement('span');
  // span 中放漢字或其他
  if (kanji_index === '-1') {
    span.innerText = origin;
  } else {
    const indices = kanji_index.split('').map(Number);
    let readingIndex = 0;

    for (let i = 0; i < origin.length; i++) {
      if (indices.includes(i)) {
        const ruby = document.createElement('ruby');
        const rt = document.createElement('rt');
        let e = i;
        while (e < origin.length && indices.includes(e)) { e++; }
        ruby.appendChild(document.createTextNode(origin.slice(i, e)));
        rt.innerText = kanji_reading.split(':')[readingIndex++] || '';
        ruby.appendChild(rt);
        span.appendChild(ruby);
        i = e - 1;
      } else {
        span.appendChild(document.createTextNode(origin[i]));
      }
    }
  }
  return span
}


async function clickToken (origin, normalForm) {
  // Initialize variables
  count = 1;
  hasMeaning = false;
  CrawlerJson = {};
  originalH2.innerText = normalForm;
  countH3.innerHTML = '';
  meanDiv.replaceChildren();
  examplesDiv.replaceChildren();

  // Reset previous vocabulary highlight
  if (nowVocab !== '') {
    const pS = document.getElementsByClassName(nowVocab);
    if (pS) Array.from(pS).forEach(S => S.removeAttribute("style"));
  }

  // Highlight selected vocabulary
  nowVocab = normalForm;
  const currentSpans = document.getElementsByClassName(nowVocab);
  if (currentSpans) {
    Array.from(currentSpans).forEach(span => span.setAttribute("style", "color:darksalmon;"));
  }

  // Fetch and display dictionary data
  await withLoader(examplesDiv, async () => {
    [CrawlerJson, hasMeaning] = await getCrawlerjson(serverIP, origin, normalForm);
    await changeMean(CrawlerJson, 0);
  });
};


async function changeMean(CrawlerJson, index) {
  const meanDict = CrawlerJson[index]
  countH3.innerHTML = `${index+1}/${CrawlerJson.length}`
  examplesDiv.replaceChildren()
  
  const jpString = meanDict["examples"].map(exampleDict => exampleDict["jp"]).join('\n');
  const jpJson = await getParse(serverIP, jpString)

  jpJson.forEach((sentenceArray, i) => {
    const exampleWrapper = getDiv('', 'JPsubtitle-token-example-wrapper');
    const jpDiv = getDiv('', 'JPsubtitle-token-example-jp');
    const zhDiv = getDiv('', 'JPsubtitle-token-example-zh');
    const zhSpan = document.createElement("span")
    zhDiv.appendChild(zhSpan)
    exampleWrapper.append(jpDiv, zhDiv)
    examplesDiv.appendChild(exampleWrapper)  
    
    sentenceArray.map((tokenDict) => {
      const { origin, normalForm, kanji_index, kanji_reading } = tokenDict;
      const span = getTokenSpan(origin, kanji_index, kanji_reading)
      jpDiv.appendChild(span)
    });

    zhSpan.innerHTML = meanDict["examples"][i]["zh"]
  })
  meanDiv.innerHTML = meanDict["mean"]
}

// 創造按鈕
function getFnBtn(name, handleFn, svgPath="", text="", tipText="") {
  const btnDiv = getDiv("", "JPsubtitle-btn")
  btnDiv.classList.add(name, "no-select")
  btnDiv.addEventListener("click", handleFn)
  if (svgPath) {
    const svgDiv = getDiv("", "JPsubtitle-svg-icon")
    putSvg(svgDiv, svgPath)
    btnDiv.append(svgDiv)
  }
  if (text) {
    const textDiv = getDiv("", "JPsubtitle-text")
    textDiv.innerText = text
    btnDiv.append(textDiv)
  }
  if (tipText) {
    const tipDiv = getDiv("", "JPsubtitle-tip")
    tipDiv.innerText = tipText
    btnDiv.append(tipDiv)
  }
  return btnDiv
}

function createFnBtns() {
  const btnArgs = [
    { name: "reset", handleFn: handle.clickResetBtn, svgPath: "icons/reset.svg", tipText: "清除字幕"},
    { name: "translate", handleFn: handle.clickTranslateBtn, svgPath: "icons/translate.svg", tipText: "翻譯字幕"},
    { name: "close", handleFn: handle.clickCloseBtn, svgPath: "icons/close.svg", tipText: "關閉"},
    { name: "jaOrZh", handleFn: handle.clickjaOrZhBtn, text: "日中"}
  ]
  btnArgs.forEach(({name, handleFn, svgPath, text, tipText}) => {
    const btn = getFnBtn(name, handleFn, svgPath, text, tipText)
    functionContainer.append(btn)
    const tip = btn.querySelector('.JPsubtitle-tip');
    if (!tip) {return}
    btn.addEventListener('mouseenter', (e) => {
      const rect = btn.getBoundingClientRect(); // 取得按鈕在視窗中的位置
      tip.style.top = `${rect.bottom+5}px`; // 動態設置提示框的位置
      tip.style.left = `${rect.left+15}px`;
      tip.style.display = 'block';
    });
    btn.addEventListener('mouseleave', () => {
        tip.style.display = 'none'; // 當滑鼠移開時隱藏提示框
    });
  })
}

function createWhisperBtn() {
  subtitleContainer.classList.add("centerItems")
  const whisperDiv = getFnBtn(
    "whisper", 
    handle.clickWhisperBtn, 
    "icons/text-to-speech.svg", 
    "AI 獲取字幕"
  )
  subtitleContainer.appendChild(whisperDiv)
}

// API
async function getTranscription(serverIP, apiKey, ytUrl) {
  const formData = new FormData();
  formData.append('apiKey', apiKey);
  formData.append('ytUrl', ytUrl);
  try {
    const response = await fetch(`${serverIP}/transcribe`, {
      method: 'POST',  body: formData
    });
    const json = await response.json();
    return json
  } catch (error) {
    return [{"line":`轉錄錯誤 ${error}`, "start":0, "end":0}]
  }
}

async function getTranslate(serverIP, apiKey, jpString) {
  const formData = new FormData();
  formData.append('apiKey', apiKey);
  formData.append('jpString', jpString);
  try {
    const response = await fetch(`${serverIP}/translate`, {
      method: 'POST',  body: formData
    });
    const text = await response.text();
    return text
  } catch (error) {
    console.error(error);
    return "翻譯時發生錯誤，請再試一次"
  }
}

async function getCrawlerjson(serverIP, origin, normalForm) {
  const formData = new FormData();
  formData.append('normalForm', normalForm);
  formData.append('origin', origin);
  try {
    const response = await fetch(`${serverIP}/crawler`, {
      method: 'POST',  body: formData
    })
    const data = await response.json()
    const {result, hasMeaning} = data
    return [result, hasMeaning]
  } 
  catch (error) {
    console.error("crawler error:", error)
    return [[{"mean":"查詢字典時發生錯誤", "examples":[dict()]}], false]
  }
}

async function getParse(serverIP, jpString) {
  if (jpString === '') {return []}

  const formData = new FormData();
  formData.append('jpString', jpString);
  try {
    const response = await fetch(`${serverIP}/parse`, {
      method: 'POST',  body: formData
    });
    const data = await response.json();
    return data
  } catch (error) {
      console.error('Error fetching data:', error);
      return [[{
        "origin": "",
        "normalForm": "",
        "kanji_index": "0",
        "kanji_reading": "發生錯誤"
      }]]
  }
}

function putSvg(svgParent, filePath) {
  fetch(chrome.runtime.getURL(filePath))
  .then(response => response.text())
  .then(svg => {svgParent.innerHTML = svg})
  .catch(error => console.error("SVG error: ",error))
}

// utils
function getDiv(id, className) {
  const div = document.createElement('div');
  div.id = id;
  div.className = className;
  return div;
}

// const formatTime = (seconds) => {
//   const minutes = Math.floor(seconds / 60);
//   const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
//   return `${minutes}:${secs}`;
// };

// function createElement(type, attributes = {}, innerText = '') {
//   const element = document.createElement(type);
//   Object.assign(element, attributes);
//   if (innerText) {element.innerText = innerText;}
//   return element;
// };

async function waitForData(dataName) {
  return 
}

async function withLoader(loaderParent, fn) {
  if (loaderParent.hasChildNodes()) { 
    console.error("loaderParent不該有子元素")
    return 
  }
  const loader = getDiv('', 'loader');
  loaderParent.appendChild(loader)

  try {
    await fn()
  } catch (error) {
    console.error("Error in withLoader:", error);
  } finally {
    if (loaderParent === loader.parentElement) {
      loaderParent.removeChild(loader); 
    }
  }
}

