function updateMarketState() {
  console.log("Calling updateMarketState");
  fetch('http://localhost:8080/market_state')
    .then(r => r.json())
    .then(result => {
      $('#topStocksLabel').text(result['top_stocks_label']);
      $('#bottomStocksLabel').text(result['bottom_stocks_label']);
    });
}

$(function(){
  updateMarketState();
  $('#marketState').on('click', updateMarketState);
});
