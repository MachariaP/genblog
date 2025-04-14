// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

function setTheme(theme) {
  html.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

themeToggle.addEventListener('click', () => {
  const currentTheme = html.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  setTheme(newTheme);
});

// Load saved theme
const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
setTheme(savedTheme);

// Post Interactions
document.querySelectorAll('.post-like').forEach(button => {
  button.addEventListener('click', async () => {
    const postId = button.dataset.postId;
    try {
      const response = await fetch(`/like/${postId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      if (response.ok) {
        button.querySelector('.like-count').textContent = data.likes;
        button.classList.toggle('liked', data.action === 'liked');
      } else {
        console.error('Like failed:', data.error);
      }
    } catch (error) {
      console.error('Like error:', error);
    }
  });
});

function submitComment(postId) {
  const textarea = document.getElementById(`commentText-${postId}`);
  const comment = textarea.value.trim();
  if (comment && comment.length <= 140) {
    fetch(`/comment/${postId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comment })
    })
    .then(response => response.json())
    .then(data => {
      if (response.ok) {
        const commentButton = document.querySelector(`.post-comment[data-post-id="${postId}"]`);
        commentButton.querySelector('.comment-count').textContent = data.comments;
        textarea.value = ''; // Clear textarea
        bootstrap.Modal.getInstance(document.getElementById(`commentModal-${postId}`)).hide();
      } else {
        console.error('Comment failed:', data.error);
        alert(data.error);
      }
    })
    .catch(error => {
      console.error('Comment error:', error);
      alert('Failed to submit comment');
    });
  } else {
    alert('Comment must be 1-140 characters');
  }
}

// Lazy-load images
document.querySelectorAll('img[loading="lazy"]').forEach(img => {
  img.addEventListener('load', () => img.classList.add('loaded'));
});