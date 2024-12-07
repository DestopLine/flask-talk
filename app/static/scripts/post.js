let posts = document.querySelectorAll(".post");

for (let post of posts) {
	addDeleteFeature(post);
	addEditFeature(post);
	addLikeFeature(post);
}

/**
* @param {Element} post
*/
function addDeleteFeature(post) {
	let deleteButton = post.querySelector(".post-delete-btn");
	if (deleteButton == null) {
		return;
	}

	deleteButton.addEventListener("click", async _ => {
		const postId = post.dataset.postId;
		response = await fetch(`/post/${postId}`, { method: "DELETE" });

		if (response.ok) {
			post.remove();
		}
	})
}

/**
* @param {Element} post
*/
function addEditFeature(post) {
	let editButton = post.querySelector(".post-edit-btn");
	if (editButton == null) {
		return;
	}

	editButton.addEventListener("click", async _ => {
		const postId = post.dataset.postId;
		let postContent = post.querySelector(".post-content");
		let postActions = post.querySelector(".post-actions");
		let postText = postContent.querySelector("p");

		let textArea = document.createElement("textarea");
		textArea.textContent = postText.textContent;

		postContent.prepend(textArea);
		postText.classList.add("hidden");
		postActions.classList.add("hidden");

		let editActions = document.createElement("div");
		let saveButton = document.createElement("button");
		let cancelButton = document.createElement("button");
		saveButton.type = "button";
		saveButton.textContent = "Guardar";
		cancelButton.type = "button";
		cancelButton.textContent = "Cancelar";

		editActions.classList.add("post-actions");
		editActions.append(saveButton, cancelButton);
		post.append(editActions);

		const restorePost = () => {
			editActions.remove();
			textArea.remove();
			postText.classList.remove("hidden");
			postActions.classList.remove("hidden");
		}

		cancelButton.addEventListener("click", _ => {
			restorePost();
		})

		saveButton.addEventListener("click", async _ => {
			if (textArea.value == postText.textContent) {
				restorePost();
				return;
			}

			response = await fetch(`/post/${postId}`, {
				method: "PUT",
				body: JSON.stringify({
					text: textArea.value,
				}),
				headers: {
					"Content-Type": "application/json",
				},
			});

			if (response.ok) {
				postText.textContent = textArea.value;
			}

			restorePost();
		})
	})
}

/**
* @param {Element} post
*/
function addLikeFeature(post) {
	let likeButton = post.querySelector(".post-like-btn");
	const postId = post.dataset.postId;

	likeButton.addEventListener("click", async (_) => {
		let response = await fetch(`/post/${postId}/like`, {
			method: "post",
		})

		if (response.ok) {
			const body = await response.json();

			if (body["liked"]) {
				likeButton.classList.add("liked");
				likeButton.textContent = `❤️ ${body["likes"]}`;
			} else {
				likeButton.classList.remove("liked");
				likeButton.textContent = `♡ ${body["likes"]}`;
			}
		}
	})
}
