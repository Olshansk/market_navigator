console.log("Executing content_script.js");

function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

var iframe = document.createElement('iframe');
// var html = '<body>Foo</body>';
var url = "https://cdn.vox-cdn.com/thumbor/lcR5ObLoDAonmUMUON1eEqFcpY4=/0x0:2000x3000/920x613/filters:focal(711x1198:1031x1518):format(webp)/cdn.vox-cdn.com/uploads/chorus_image/image/66980073/1227448347.jpg.5.jpg";

// var html = `<iframe src="${url}></iframe>`;
// iframe = htmlToElement(html);
// var html = `<img src=${url} id="img01" style='height: 100%; width: 100%; object-fit: contain'>`;
// var html = `<img src=${url} id="img01" style='height: 100%; width: 100%; object-fit: contain'>`;
var html = `
  <script src="/iframeResizer.contentWindow.min.js"></script>
  <img id="myImage" src=${url}>
`;
// <style>iframe{width:100%}</style>
// <iframe src="http://anotherdomain.com/iframe.html" scrolling="no"></iframe>
// <script>iFrameResize({log:true})</script>

// iframe {
//   width: 1px;
//   min-width: 100%;
// }
// </style>
// <iframe id="myIframe" src="http://anotherdomain.com/iframe.html"></iframe>
// <script>
// iFrameResize({ log: true }, '#myIframe')
// </script>
// iframe.src = 'data:text/html;charset=utf-8,' + encodeURI(html);
iframe.src = url;
iframe.id = 'myIframe';
iframe.scrolling='no';
iframe.frameborder='0';
iframe.style="position: relative; height: 500px; width: 600px;"
iframe.onload="iFrameResize({log: true, bodyBackground: \"myImage\"})";
// iframe.style="position: relative;"
// document.body.appendChild(iframe);
// console.log('iframe.contentWindow =', iframe.contentWindow);

function resizeIFrameToFitContent( iFrame ) {
    console.log("HERE", iFrame.contentWindow.document.body.scrollHeight);
    iFrame.width  = iFrame.contentWindow.document.body.scrollWidth;
    iFrame.height = iFrame.contentWindow.document.body.scrollHeight;
}
// iframe[0].window.foo = function(){
//    console.log ("Look at me, executed inside an iframe!", window);
// }


// $('#imagepreview').attr('src', $('#imageresource').attr('src'));
// $('#imagepreview').attr('src', "https://cdn.vox-cdn.com/thumbor/lcR5ObLoDAonmUMUON1eEqFcpY4=/0x0:2000x3000/920x613/filters:focal(711x1198:1031x1518):format(webp)/cdn.vox-cdn.com/uploads/chorus_image/image/66980073/1227448347.jpg.5.jpg");
// $('#imagemodal').modal('show');


// <img id="img01" style="width:100%">


$(htmlToElement(modal_html)).appendTo('body');
console.log(modal_html);
document.getElementById("modal-content").appendChild(iframe);
// document.getElementById("img01").src = url;
document.getElementById("modal01").style.display = "block";

resizeIFrameToFitContent(document.getElementById('myIframe'));
// iFrameResize({ log: true }, '#myIframe');
// document.onload = function () {
  // console.log("Here");
  // $('#myIframe').iFrameResize( [{ log: true }] );
// };
// function myClick() {
//
// }

// setTimeout(
//   function() {
//     iFrameResize({ log: true , bodyBackground: "myImage"});
    // $('#myIframe').iFrameResize( [{ log: true }] );
    // resizeIFrameToFitContent($('#myIframe'));
    // document.getElementById('div1').style.display='none';
    // document.getElementById('div2').style.display='none';
  // }, 2000);

// document.body.appendChild(iframe);

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
