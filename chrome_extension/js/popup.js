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
 fetch('https://storage.googleapis.com/market-navigator-data/per_high_low_latest.json')
   .then(r => r.json())
   .then(result => {
     // TODO(olshansky): Replace this with result['max_delta_per'] after the next deployment.
     let MAX_DELTA_PER = 0.2;
     let top_stocks_label = `${Math.round(result['near_max'] * 100)}% of stocks are within ${Math.round(MAX_DELTA_PER * 100)}% of their 52 week MAX, compared to an average of ${Math.round(result['avg_near_max'] * 100)}%.`;
     let bottom_stocks_label = `${Math.round(result['near_min'] * 100)}% of stocks are within ${Math.round(MAX_DELTA_PER * 100)}% of their 52 week MIN, compared to an average of ${Math.round(result['avg_near_min'] * 100)}%.`;
     $('#topStocksLabel').text(top_stocks_label);
     $('#bottomStocksLabel').text(bottom_stocks_label);
   });
}

// function updateMarketState() {
//   console.log("Calling updateMarketState");
//   fetch('http://localhost:8080/market_state')
//     .then(r => r.json())
//     .then(result => {
//       $('#topStocksLabel').text(result['top_stocks_label']);
//       $('#bottomStocksLabel').text(result['bottom_stocks_label']);
//     });
// }

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
