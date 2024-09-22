// window.onload = function () {
//   Particles.init({
//     selector: ".background",
//   });
// };

function copyToClipboard() {
  var textToCopy = document.getElementById("text-to-copy");
  //   console.log(textToCopy);
  if (textToCopy.value.length !== 3) {
    textToCopy.select();
    document.execCommand("copy");
    changecopy();
  }
}
function changecopy() {
  var ele = document.getElementById("change-copy");

  var textToCopy = document.getElementById("text-to-copy");
  if (textToCopy.value.length !== 2) {
    console.log(textToCopy.value.length);
    ele.classList.remove("btn-outline-primary");
    ele.classList.add("btn-success");
    ele.innerHTML = "copied!";
  }
}

$(document).ready(function () {
  $(".datatable").DataTable();
});

async function copy_Clipboard(text) {
  console.log(text);
  try {
    await navigator.clipboard.writeText(text);
    console.log("Text copied to clipboard");
  } catch (err) {
    console.error("Failed to copy text: ", err);
  }
}
