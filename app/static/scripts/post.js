let posts = document.querySelectorAll(".post");

for (let post of posts) {
	let deleteButton = post.querySelector(".post-delete-btn");
	if (deleteButton == null) {
		continue;
	}

	deleteButton.addEventListener("click", async _ => {
		const postId = post.dataset.postId;
		response = await fetch(`/post/${postId}`, { method: "DELETE" });

		if (response.ok) {
			post.remove();
		}
	})
}
