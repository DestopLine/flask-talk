let form = document.querySelector("#login-form");
let submitButton = form.querySelector(".iniciar-sesion");
let errorMessage = form.querySelector(".error")

submitButton.addEventListener("click", async (_) => {
	const formData = new FormData(form);

	const response = await fetch("/login", {
		method: "post",
		body: formData,
	})

	if (response.ok) {
		location.href = "/";
		return;
	}

	const body = await response.json();
	errorMessage.textContent = body["error"]
	errorMessage.classList.remove("hidden")
	console.log("asdfasdf");
})
