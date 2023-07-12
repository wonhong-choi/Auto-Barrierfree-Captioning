
// Get the elements
const commentText = document.getElementById('comment-text');
const newComment = document.getElementById('new-comment');
const submitBtn = document.getElementById('submit-btn');

// Add event listener to the submit button
submitBtn.addEventListener('click', function() {
// Get the new comment text from the textarea
const newText = newComment.value;

// Update the comment text
commentText.innerText = newText;
});