let comments = document.querySelectorAll(".comment");

for (let comment of comments) {
	addReplyToggleFeature(comment);
}

/**
 * @param {Element} comment
 */
function addReplyToggleFeature(comment) {
	let toggleButton = comment.querySelector(".toggle-respuestas-btn");
	let replies = comment.querySelector(".replies");
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