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
    // Initialize comment UX (char counter, disable empty submit)
    initializeCommentFeatures();
}

function initializeCommentFeatures() {
    const form = document.getElementById('interaction-form');
    if (!form) return;

    const textarea = form.querySelector('#review');
    const submitButton = form.querySelector('button[type="submit"]');
    if (!textarea || !submitButton) return;

    // Create or reuse counter element
    let counter = form.querySelector('.comment-counter');
    if (!counter) {
        counter = document.createElement('div');
        counter.className = 'comment-counter';
        counter.style.fontSize = '0.85rem';
        counter.style.color = '#666';
        counter.style.marginTop = '6px';
        textarea.parentNode.appendChild(counter);
    }

    const updateCounter = () => {
        const len = textarea.value.trim().length;
        counter.textContent = `${len} / 1000`;
        // disable submit if empty and no rating/like
        const rating = form.querySelector('#rating') ? form.querySelector('#rating').value : '';
        const liked = form.querySelector('#liked') ? form.querySelector('#liked').checked : false;
        submitButton.disabled = !(len > 0 || rating || liked);
    };

    textarea.addEventListener('input', updateCounter);
    // init
    updateCounter();
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
    button.setAttribute('aria-busy', 'true');
    button.classList.add('processing');

    try {
        const response = await fetch(`/api/like/${filmId}`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        // If server returned unauthorized for AJAX, redirect to login
        if (response.status === 401) {
            // try to preserve current path for redirect after login
            const next = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = `/login?next=${next}`;
            return;
        }
        // Inspect content type before parsing JSON to detect HTML redirects (e.g., login page)
        const ct = response.headers.get('content-type') || '';
        if (!ct.includes('application/json')) {
            // likely a redirect to login or an HTML error page
            if (response.url && response.url.includes('/login')) {
                // redirect user to login
                window.location.href = response.url;
                return;
            }
            showMessage(`Operation failed (${response.status})`, 'error');
            return;
        }

        let data = null;
        try {
            data = await response.json();
        } catch (e) {
            console.warn('Could not parse like response as JSON', e);
            showMessage('Unexpected server response, please retry', 'error');
            return;
        }

        if (data && data.success) {
            // Update button status
            updateLikeButton(button, data.liked);

            // Update like count
            updateLikeCount(filmId, data.like_count);

            // Show message
            showMessage(data.message || 'Like updated', 'success');
        } else {
            // server returned success=false
            const msg = data.message || `Operation failed (${response.status})`;
            showMessage(msg, 'error');
        }
    } catch (error) {
        console.error('Like request failed:', error);
        // Show clearer error for network/fetch problems
        const errMsg = error && error.message ? error.message : 'Network error, please retry';
        showMessage(errMsg, 'error');
    } finally {
        // Re-enable button and clear processing state
        button.disabled = false;
        button.removeAttribute('aria-busy');
        button.classList.remove('processing');
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
        // handle auth redirect for AJAX
        if (response.status === 401) {
            const next = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = `/login?next=${next}`;
            return;
        }

        const result = await response.json();

            if (result.success) {
                showMessage(result.message, 'success');

                // Update page display
                if (result.data) {
                    updateInteractionDisplay(result.data);
                    updateFilmStats(result.data.film_stats);
                }

                // Optimistic append: if server returned review content or we have local text, prepend immediately
                const newReview = result.data && (result.data.review || result.data.interaction) ? (result.data.review || result.data.interaction) : null;
                if (newReview) {
                    prependReview(newReview);
                } else if (data.review && data.review.trim().length > 0) {
                    // construct a minimal review object using current username if available
                    const username = document.querySelector('.user-menu-trigger span')?.textContent || 'You';
                    prependReview({
                        user: { username: username },
                        rating: data.rating || null,
                        created_at: new Date().toISOString(),
                        review_text: data.review
                    });
                }

                // Reload first page of comments to ensure consistency (after short delay)
                setTimeout(() => {
                    loadReviews(filmId, 1);
                }, 800);
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
    return text.replace(/[&<>"']/g, function(m) {
        return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[m];
    });
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
        if (response.status === 401) {
            const next = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = `/login?next=${next}`;
            return;
        }

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
    // set aria and visual state, keep icon
    button.setAttribute('aria-pressed', liked ? 'true' : 'false');
    if (liked) {
        button.classList.add('liked');
        // add small animation class
        button.classList.add('liked-anim');
        button.innerHTML = '<i class="fas fa-heart"></i> <span class="like-label">Liked</span>';
        // remove animation class after animation (300ms)
        setTimeout(() => button.classList.remove('liked-anim'), 350);
    } else {
        button.classList.remove('liked');
        button.innerHTML = '<i class="fas fa-heart"></i> <span class="like-label">Like</span>';
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
    messageDiv.setAttribute('aria-live', 'polite');
    messageDiv.textContent = message;

    // Add to top of page
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(messageDiv, container.firstChild);

    // Also announce via dedicated live region if present (for dynamic updates)
    const live = document.getElementById('aria-live');
    if (live) {
        live.textContent = message;
    }

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

// Prepend a single review element (optimistic UI)
function prependReview(review) {
    const container = document.getElementById('reviews-container');
    if (!container || !review) return;

    const div = document.createElement('div');
    div.className = 'review-item review-new';

    const username = escapeHtml(review.user && (review.user.username || review.user) || document.querySelector('.user-menu-trigger span')?.textContent || 'You');
    const rating = review.rating ? `<span class="review-rating">${review.rating}/5 ★</span>` : '';
    const date = review.created_at ? new Date(review.created_at).toLocaleString() : new Date().toLocaleString();
    const text = escapeHtml(review.review_text || review.text || '');

    div.innerHTML = `
        <div class="review-header">
            <strong>${username}</strong>
            ${rating}
            <span class="review-date">${date}</span>
        </div>
        <div class="review-content"><p>${text}</p></div>
    `;

    container.insertBefore(div, container.firstChild);
    // remove the highlight class after animation finishes
    setTimeout(() => div.classList.remove('review-new'), 900);
}
