import 'alpinejs'

function updateMarketState() {
 console.log("Calling updateMarketState");
 fetch('https://storage.googleapis.com/market-navigator-data/per_high_low_latest.json')
   .then(r => r.json())
   .then(result => {
     let max_delta_per = result['max_delta_per'] || 0.2;
     let top_stocks_label = `${Math.round(result['near_max'] * 100)}% of stocks are within ${Math.round(MAX_DELTA_PER * 100)}% of their 52 week MAX, compared to an average of ${Math.round(result['avg_near_max'] * 100)}%.`;
     let bottom_stocks_label = `${Math.round(result['near_min'] * 100)}% of stocks are within ${Math.round(MAX_DELTA_PER * 100)}% of their 52 week MIN, compared to an average of ${Math.round(result['avg_near_min'] * 100)}%.`;
     $('#topStocksLabel').text(top_stocks_label);
     $('#bottomStocksLabel').text(bottom_stocks_label);
   });
}
