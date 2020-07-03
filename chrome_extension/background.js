console.log("Executing background.js script");

chrome.runtime.onInstalled.addListener(function() {
  chrome.storage.sync.set({color: '#aaa111'}, function() {
    console.log("The color is green.");
  });
});


// chrome.tabs.executeScript(null, {file:'jquery.js'}, function(result){
// });
