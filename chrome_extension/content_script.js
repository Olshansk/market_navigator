function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

// var iframe = document.createElement('iframe');
// var html = '<body>Foo</body>';
// iframe.src = 'data:text/html;charset=utf-8,' + encodeURI(modal_html);
// document.body.appendChild(iframe);
// console.log('iframe.contentWindow =', iframe.contentWindow);

console.log("Executing content_script.js");
console.log(modal_html);
$(htmlToElement(modal_html)).appendTo('body');
// $('#imagepreview').attr('src', $('#imageresource').attr('src'));
// $('#imagepreview').attr('src', "https://cdn.vox-cdn.com/thumbor/lcR5ObLoDAonmUMUON1eEqFcpY4=/0x0:2000x3000/920x613/filters:focal(711x1198:1031x1518):format(webp)/cdn.vox-cdn.com/uploads/chorus_image/image/66980073/1227448347.jpg.5.jpg");
// $('#imagemodal').modal('show');

var url = "https://cdn.vox-cdn.com/thumbor/lcR5ObLoDAonmUMUON1eEqFcpY4=/0x0:2000x3000/920x613/filters:focal(711x1198:1031x1518):format(webp)/cdn.vox-cdn.com/uploads/chorus_image/image/66980073/1227448347.jpg.5.jpg";
// var url = image_url;
document.getElementById("img01").src = url;
document.getElementById("modal01").style.display = "block";

// console.log("HELLO")
 // $('#imagemodal').modal('show');
//
// // Got solution from https://stackoverflow.com/questions/21314897/access-dom-elements-through-chrome-extension
// chrome.runtime.onMessage.addListener(function(msg, sender, sendResponse) {
//   $.get(chrome.extension.getURL('/template.html'), function(data) {
//     $(data).appendTo('body');
//     // Or if you're using jQuery 1.8+:
//     // $($.parseHTML(data)).appendTo('body');
// });
//   // if (msg.text && (msg.text == "report_back")) {
//   //   sendResponse(document.documentElement.innerHTML);
//   // }
// });

// $.get(chrome.extension.getURL('/template.html'), function(data) {
//     $(data).appendTo('body');
//     // Or if you're using jQuery 1.8+:
//     // $($.parseHTML(data)).appendTo(
// });

// alert("Message recieved!");

// $.get(chrome.extension.getURL('/modal.html'))
//     // .then(response => response.text())
//     .then(data => {
//       $(data).appendTo('body');
//         // console.log("HERE");
//         //   document.body.innerHTML += data;
//         // other code
//         // eg update injected elements,
//         // add event listeners or logic to connect to other parts of the app
//     }).catch(err => {
//         // handle error
//     });
// console.log("TEST");
//
// chrome.extension.onMessage.addListener(function(msg, sender, sendResponse) {
//   if (msg.action == 'open_dialog_box') {
//     alert("Message recieved!");
//   }
// });
//
// function ping() {
//   chrome.runtime.sendMessage('ping', response => {
//     if(chrome.runtime.lastError) {
//       setTimeout(ping, 1000);
//     } else {
//       // Do whatever you want, background script is ready now
//     }
//   });
// }
//
// ping();