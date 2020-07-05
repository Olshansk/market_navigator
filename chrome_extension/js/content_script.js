console.log("Executing content_script.js");

function htmlToElement(html) {
    var template = document.createElement('template');
     // Never return a text node of whitespace as the result
    html = html.trim();
    template.innerHTML = html;
    return template.content.firstChild;
}

var iframe_modal_parent = document.getElementById("iframe-modal-parent")
if (iframe_modal_parent == undefined) {
 document.body.appendChild(htmlToElement(modal_html));   // modal_html is injected by the popup
}
if (iframe_modal_parent != undefined && iframe_modal_parent.style.display != "block") {
  document.getElementById("iframe-modal-parent").style.display = "block";
}

var iframe_modal_content = document.getElementById("iframe-modal-content");
iframe_modal_content.style=`position: relative; height: ${iframe_height}px; width: ${iframe_width}px;`
var iframe = document.getElementById('iframe-content')
if (iframe != undefined) {
  iframe_modal_content.removeChild(iframe);
}

iframe = document.createElement('iframe');
iframe.src = iframe_url; // iframe_url is injected  by the popup
iframe.id = 'iframe-content';
iframe.scrolling='no';
iframe.frameborder='0';
iframe.classList.add("market-navigator-iframe-content");
iframe.onload="iFrameResize({log: true, bodyBackground: \"myImage\"})";

iframe_modal_content.appendChild(iframe);
