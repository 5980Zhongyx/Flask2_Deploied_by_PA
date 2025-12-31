// Movie interaction related functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interaction features
    initializeInteractions();
});

function initializeInteractions() {
    // Bind events for all like buttons
    const likeButtons = document.querySelectorAll('.like-btn, .btn-like');
    likeButtons.forEach(button => {
        button.addEventListener('click', handleLikeClick);
    });

    // Bind events for interaction form
    const interactionForm = document.getElementById('interaction-form');
    if (interactionForm) {
        interactionForm.addEventListener('submit', handleInteractionSubmit);
    }

    // Bind events for delete review button
    const deleteButton = document.getElementById('delete-interaction');
    if (deleteButton) {
        deleteButton.addEventListener('click', handleDeleteInteraction);
    }
}

async function handleLikeClick(event) {
    event.preventDefault();

    const button = event.currentTarget;
    const filmId = button.dataset.filmId || button.getAttribute('data-film-id');

    if (!filmId) {
        console.error('Film ID not found');
        return;
    }

    // Disable button to prevent double clicks
    button.disabled = true;
        button.textContent = 'Processing...';

    try {
        const response = await fetch(`/api/like/${filmId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            // Update button status
            updateLikeButton(button, data.liked);

            // Update like count
            updateLikeCount(filmId, data.like_count);

            // Show message
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message || 'Operation failed', 'error');
        }
    } catch (error) {
        console.error('Like request failed:', error);
        showMessage('Network error, please retry', 'error');
    } finally {
        // Re-enable button
        button.disabled = false;
    }
}

async function handleInteractionSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const filmId = form.dataset.filmId || getFilmIdFromUrl();
    const submitButton = form.querySelector('button[type="submit"]');

    if (!filmId) {
        showMessage('Unable to get film ID', 'error');
        return;
    }

    // Collect form data
    const formData = new FormData(form);
    const data = {
        rating: formData.get('rating') || null,
        liked: formData.has('liked'),
        review: formData.get('review') || ''
    };

    // Disable submit button
    submitButton.disabled = true;
    submitButton.textContent = 'Saving...';

    try {
        const response = await fetch(`/api/interaction/${filmId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showMessage(result.message, 'success');

            // Update page display
            if (result.data) {
                updateInteractionDisplay(result.data);
                updateFilmStats(result.data.film_stats);
            }

            // Partial refresh update comments list and stats (prioritize comments refresh)
            if (result.data) {
                updateInteractionDisplay(result.data);
                updateFilmStats(result.data.film_stats);
            }
            // Reload first page of comments
            setTimeout(() => {
                loadReviews(filmId, 1);
            }, 300);
        } else {
            showMessage(result.message || 'Save failed', 'error');
        }
    } catch (error) {
        console.error('Interaction submit failed:', error);
        showMessage('Network error, please retry', 'error');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Save Review';
    }
}

// Load specified page of comments and render to page
async function loadReviews(filmId, page = 1, per_page = 5) {
    try {
        const resp = await fetch(`/api/reviews/${filmId}?page=${page}&per_page=${per_page}`);
        const json = await resp.json();
        if (!json.success) return;

        const container = document.getElementById('reviews-container');
        if (!container) return;

        // Render comments
        container.innerHTML = '';
        json.data.forEach(review => {
            const div = document.createElement('div');
            div.className = 'review-item';
            div.innerHTML = `
                <div class="review-header">
                    <strong>${escapeHtml(review.user.username)}</strong>
                    ${review.rating ? `<span class="review-rating">${review.rating}/5 ★</span>` : ''}
                    <span class="review-date">${new Date(review.created_at).toLocaleString()}</span>
                </div>
                <div class="review-content"><p>${escapeHtml(review.review_text)}</p></div>
            `;
            container.appendChild(div);
        });

        // Pagination controls
        const pageInfo = document.getElementById('reviews-pagination');
        if (pageInfo) {
            const total = json.total;
            const totalPages = Math.max(1, Math.ceil(total / per_page));
            pageInfo.innerHTML = renderReviewsPagination(page, totalPages);
            // Bind pagination buttons
            pageInfo.querySelectorAll('.review-page-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const p = parseInt(e.currentTarget.dataset.page);
                    loadReviews(filmId, p, per_page);
                });
            });
        }
    } catch (e) {
        console.error('Load reviews failed', e);
    }
}

function renderReviewsPagination(current, totalPages) {
    let html = '';
    if (totalPages <= 1) return html;
    if (current > 1) {
        html += `<button class="review-page-btn" data-page="${current-1}">Previous</button>`;
    }
    html += `<span> Page ${current} / ${totalPages} </span>`;
    if (current < totalPages) {
        html += `<button class="review-page-btn" data-page="${current+1}">Next</button>`;
    }
    return html;
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[m]; });
}

async function handleDeleteInteraction(event) {
    event.preventDefault();

    const filmId = getFilmIdFromUrl();
    if (!filmId) {
        showMessage('Unable to get film ID', 'error');
        return;
    }

    if (!confirm('Are you sure you want to delete this review? This action cannot be undone.')) {
        return;
    }

    const button = event.target;
    button.disabled = true;
    button.textContent = 'Deleting...';

    try {
        const response = await fetch(`/api/interaction/${filmId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            showMessage(result.message, 'success');
            // Reload page
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showMessage(result.message || 'Delete failed', 'error');
        }
    } catch (error) {
        console.error('Delete interaction failed:', error);
        showMessage('Network error, please retry', 'error');
    } finally {
        button.disabled = false;
        button.textContent = 'Delete Review';
    }
}

function updateLikeButton(button, liked) {
    if (liked) {
        button.classList.add('liked');
        button.textContent = 'Liked';
        button.setAttribute('aria-pressed', 'true');
    } else {
        button.classList.remove('liked');
        button.textContent = 'Like';
        button.setAttribute('aria-pressed', 'false');
    }
}

function updateLikeCount(filmId, count) {
    const countElements = document.querySelectorAll(`[data-like-count="${filmId}"]`);
    countElements.forEach(element => {
        element.textContent = count;
    });
}

function updateInteractionDisplay(data) {
    // Update rating display
    const ratingDisplay = document.querySelector('.rating-display');
    if (ratingDisplay && data.rating) {
        ratingDisplay.textContent = `Your rating: ${data.rating}/5 ★`;
    }

    // Update like status
    const likeStatus = document.querySelector('.like-status');
    if (likeStatus) {
        likeStatus.style.display = data.liked ? 'block' : 'none';
    }

    // Update review display
    const reviewDisplay = document.querySelector('.review-display');
    if (reviewDisplay) {
        reviewDisplay.style.display = data.has_review ? 'block' : 'none';
        if (data.has_review) {
            reviewDisplay.querySelector('p').textContent = data.review_text;
        }
    }
}

function updateFilmStats(stats) {
    // Update movie average rating
    const ratingElements = document.querySelectorAll('.rating-value');
    ratingElements.forEach(element => {
        if (stats.average_rating > 0) {
            element.textContent = stats.average_rating.toFixed(1);
        }
    });

    // Update like count
    const likeCountElements = document.querySelectorAll('.likes');
    likeCountElements.forEach(element => {
        element.textContent = `${stats.like_count} likes`;
    });

    // Update rating count
    const ratingCountElements = document.querySelectorAll('.rating-count');
    ratingCountElements.forEach(element => {
        element.textContent = `(${stats.rating_count} ratings)`;
    });
}

function showMessage(message, type = 'info') {
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.setAttribute('role', 'alert');
    messageDiv.textContent = message;

    // Add to top of page
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(messageDiv, container.firstChild);

    // Auto remove after 3 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

function getFilmIdFromUrl() {
    const match = window.location.pathname.match(/\/films\/(\d+)/);
    return match ? match[1] : null;
}

// Backward compatibility functions
function likeFilm(filmId) {
    const button = document.querySelector(`[data-film-id="${filmId}"]`);
    if (button) {
        button.click();
    } else {
        // 降级到传统请求
        fetch(`/like/${filmId}`, {
            method: "POST"
        }).then(() => {
            window.location.reload();
        });
    }
}
