let form = document.querySelector("#register-form");
let submitButton = form.querySelector(".registrarse");
let errorMessage = form.querySelector(".error")

submitButton.addEventListener("click", async (_) => {
	const formData = new FormData(form);

	const response = await fetch("/registro", {
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
})
