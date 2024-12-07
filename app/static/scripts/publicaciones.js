let comments = document.querySelectorAll(".comment");
let replies = document.querySelectorAll(".reply");

for (let comment of comments) {
	addReplyToggleFeature(comment);
	addCommentLikeFeature(comment)
}

for (let reply of replies) {
	addReplyLikeFeature(reply)
}

/**
 * @param {Element} comment
 */
function addReplyToggleFeature(comment) {
	let toggleButton = comment.querySelector(".toggle-respuestas-btn");
	let replies = comment.querySelector(".replies");

	if (replies === null) {
		return;
	}

	const replyAmount = replies.children.length;

	toggleButton.addEventListener("click", (_) => {
		if (replies.classList.contains("hidden")) {
			replies.classList.remove("hidden");
			toggleButton.textContent = `Ocultar ${replyAmount} respuestas`;
		} else {
			replies.classList.add("hidden");
			toggleButton.textContent = `Mostrar ${replyAmount} respuestas`;
		}
	});
}

/**
* @param {Element} comment
*/
function addCommentLikeFeature(comment) {
	let likeButton = comment.querySelector(".comment-like-btn");
	const commentId = comment.dataset.commentId;

	likeButton.addEventListener("click", async (_) => {
		let response = await fetch(`/comment/${commentId}/like`, {
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

/**
* @param {Element} reply
*/
function addReplyLikeFeature(reply) {
	let likeButton = reply.querySelector(".reply-like-btn");
	const replyId = reply.dataset.replyId;

	likeButton.addEventListener("click", async (_) => {
		let response = await fetch(`/reply/${replyId}/like`, {
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
