let form = document.querySelector("#create-post-form");
let container = form.querySelector(".create-post-image-container");
/** @type {HTMLInputElement} */
let imageInput = form.querySelector("#create-post-image-input");
let image = form.querySelector("#create-post-image");
let closeButton = form.querySelector("button");
let textArea = form.querySelector("textarea")
/** @type {HTMLButtonElement} */
let submitButton = form.querySelector("#create-post-submit");

imageInput.addEventListener("change", (event) => {
	image.src = URL.createObjectURL(event.target.files[0])
	container.classList.remove("hidden");
});

closeButton.addEventListener("click", (_) => {
	imageInput.value = "";
	container.classList.add("hidden");
})

function reloadSubmitButton() {
	submitButton.disabled = textArea.value.length == 0 && imageInput.files.length == 0;
}

textArea.addEventListener("input", reloadSubmitButton);
imageInput.addEventListener("change", reloadSubmitButton);
closeButton.addEventListener("click", reloadSubmitButton);

reloadSubmitButton()
