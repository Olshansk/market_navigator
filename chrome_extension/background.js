chrome.runtime.onInstalled.addListener(function() {
  chrome.storage.sync.set({color: '#aaa111'}, function() {
    console.log("The color is green.");
  });
});
