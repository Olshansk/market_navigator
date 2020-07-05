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

$(function() {
  // Load data on startup
  updateMarketState();

  // Reload data on click
  $('#marketState').on('click', updateMarketState);

  // Open up market state as a modal
  $("#pop").on("click", function() {
    $.get(chrome.extension.getURL('/html/modal_template.html'), function(modal_html) {
      // TODO(olshansky): Use https://github.com/davidjbradshaw/iframe-resizer in
      // the future when I end up owning the domain myself and don't have to pass
      // the width and height manually.
      var width = 600;
      var height = 200;
      var iframe_url = `https://picsum.photos/${width}/${height}`;
      var variable_injection_script = `
        var modal_html = \`${modal_html}\`;
        var iframe_url=\`${iframe_url}\`;
        var iframe_width = \`${width}\`;
        var iframe_height = \`${height}\`;
      `;
      chrome.tabs.executeScript(null, { code: variable_injection_script }, function(result) {
        chrome.tabs.executeScript(null, { file: '/js/content_script.js' }, function(result){
          window.close(); // Close the chrome extension window
        });
      });
    });
  });
});
