const original = document.querySelector("#original");
const original_div = document.querySelector("#original-div");
original.addEventListener("click", () => flipflop(original_div, result_div))

const result = document.querySelector("#result");
const result_div = document.querySelector("#result-div");
result.addEventListener("click", () => flipflop(result_div, original_div));

function flipflop(show, hide) {
    show.classList.remove('hidden');
    hide.classList.add('hidden');
}


const img_colors = document.querySelector("#img-colors");
let colors = ["#000000"];
if (img_colors) {
    let spans = img_colors.getElementsByClassName('label');
    colors = Array.from(spans).map(span => span.style.backgroundColor);
}
