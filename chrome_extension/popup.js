console.log("Executing popup.js");
chrome.runtime.onMessage.addListener(
    function(message, callback) {
      if (message == "changeColor"){
        chrome.tabs.executeScript({
          file: "content_script.js"
        });
      }
   });


function updateMarketState() {
  console.log("Calling updateMarketState");
  fetch('http://localhost:8080/market_state')
    .then(r => r.json())
    .then(result => {
      $('#topStocksLabel').text(result['top_stocks_label']);
      $('#bottomStocksLabel').text(result['bottom_stocks_label']);
    });
}

chrome.browserAction.onClicked.addListener(function(tab) {
    /*...check the URL of the active tab against our pattern and... */
    if (urlRegex.test(tab.url)) {
        /* ...if it matches, send a message specifying a callback too */
        chrome.tabs.sendMessage(tab.id, { text: "report_back" }, doStuffWithDOM);
    }
});

function doStuffWithDOM(element) {
  $('#imagepreview').attr('src', $('#imageresource').attr('src'));
  $('#imagemodal').modal('show');
    alert("I received the following DOM content:\n" + element);
}

function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}


$(function() {

  // Load data on startup
  updateMarketState();

  // Reload data on click
  $('#marketState').on('click', updateMarketState);

  // Open up market state modal popup
  $("#pop").on("click", function() {
    // $('#imagepreview').attr('src', $('#imageresource').attr('src'));
    // var modal_html = $('#imagemodal').html();
    // console.log("~~~~~")
    // console.log($('#imagemodal').html());
    // $('#imagemodal').modal('show');


    $.get(chrome.extension.getURL('/modal.html'), function(data) {
      $.get(chrome.extension.getURL('/modal2.html'), function(data2) {
        var image_url = chrome.runtime.getURL($('#imageresource').attr('src'));
        var js_url = chrome.runtime.getURL('/iframeResizer.contentWindow.min.js');
        console.log(js_url);
        var element = htmlToElement(data2)
        var s = `var js_url=\`${js_url}\`; var image_url= \`${image_url}\`; var modal_html = \`${data2}\``;
        // console.log(s);
        // console.log();
        // $(element).appendTo('body');
        // $('#imagepreview').attr('src', image_url);
        // $('#imagemodal').modal('show');
          // console.log(data);

          // Or if you're using jQuery 1.8+:
          // $($.parseHTML(data)).appendTo('body');
          chrome.tabs.executeScript(null, {file:'iframeResizer.min.js'});
          // chrome.tabs.executeScript(null, {file:'iframeResizer.contentWindow.min.js'});
          chrome.tabs.executeScript(null, {file:'jquery3.5.1.min.js'}, function(result){
            chrome.tabs.executeScript(null, { code: s }, function(result) {
              chrome.tabs.executeScript(null, { file: 'content_script.js' }, function(result){
                // window.close();
              });
            });
          });
      });
    });
  });

  //   chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
  //       console.log("HERE", tabs[0].id);
  //       chrome.tabs.sendMessage(tabs[0].id, {action: "open_dialog_box"}, function(response) {});
  //   });
  //   // chrome.tabs.executeScript(null, { file: 'content_script.js' });
  //   // $('#imagepreview').attr('src', $('#imageresource').attr('src'));
  //   // $('#imagemodal').modal('show');
  //


});


chrome.runtime.onConnect.addListener(port => {
  port.onMessage.addListener(msg => {
    // Handle message however you want
  })
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => sendResponse('pong'));
