// 电影交互相关功能
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有交互功能
    initializeInteractions();
});

function initializeInteractions() {
    // 为所有点赞按钮绑定事件
    const likeButtons = document.querySelectorAll('.like-btn, .btn-like');
    likeButtons.forEach(button => {
        button.addEventListener('click', handleLikeClick);
    });

    // 为交互表单绑定事件
    const interactionForm = document.getElementById('interaction-form');
    if (interactionForm) {
        interactionForm.addEventListener('submit', handleInteractionSubmit);
    }

    // 为删除评价按钮绑定事件
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

    // 禁用按钮防止重复点击
    button.disabled = true;
    button.textContent = '处理中...';

    try {
        const response = await fetch(`/api/like/${filmId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            // 更新按钮状态
            updateLikeButton(button, data.liked);

            // 更新点赞计数
            updateLikeCount(filmId, data.like_count);

            // 显示消息
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message || '操作失败', 'error');
        }
    } catch (error) {
        console.error('Like request failed:', error);
        showMessage('网络错误，请重试', 'error');
    } finally {
        // 重新启用按钮
        button.disabled = false;
    }
}

async function handleInteractionSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const filmId = form.dataset.filmId || getFilmIdFromUrl();
    const submitButton = form.querySelector('button[type="submit"]');

    if (!filmId) {
        showMessage('无法获取电影ID', 'error');
        return;
    }

    // 收集表单数据
    const formData = new FormData(form);
    const data = {
        rating: formData.get('rating') || null,
        liked: formData.has('liked'),
        review: formData.get('review') || ''
    };

    // 禁用提交按钮
    submitButton.disabled = true;
    submitButton.textContent = '保存中...';

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

            // 更新页面显示
            if (result.data) {
                updateInteractionDisplay(result.data);
                updateFilmStats(result.data.film_stats);
            }

            // 重新加载页面以显示更新
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showMessage(result.message || '保存失败', 'error');
        }
    } catch (error) {
        console.error('Interaction submit failed:', error);
        showMessage('网络错误，请重试', 'error');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = '保存评价';
    }
}

async function handleDeleteInteraction(event) {
    event.preventDefault();

    const filmId = getFilmIdFromUrl();
    if (!filmId) {
        showMessage('无法获取电影ID', 'error');
        return;
    }

    if (!confirm('确定要删除这条评价吗？此操作不可撤销。')) {
        return;
    }

    const button = event.target;
    button.disabled = true;
    button.textContent = '删除中...';

    try {
        const response = await fetch(`/api/interaction/${filmId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            showMessage(result.message, 'success');
            // 重新加载页面
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showMessage(result.message || '删除失败', 'error');
        }
    } catch (error) {
        console.error('Delete interaction failed:', error);
        showMessage('网络错误，请重试', 'error');
    } finally {
        button.disabled = false;
        button.textContent = '删除评价';
    }
}

function updateLikeButton(button, liked) {
    if (liked) {
        button.classList.add('liked');
        button.textContent = '已点赞';
        button.setAttribute('aria-pressed', 'true');
    } else {
        button.classList.remove('liked');
        button.textContent = '点赞';
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
    // 更新评分显示
    const ratingDisplay = document.querySelector('.rating-display');
    if (ratingDisplay && data.rating) {
        ratingDisplay.textContent = `你的评分：${data.rating}/5 ★`;
    }

    // 更新点赞状态
    const likeStatus = document.querySelector('.like-status');
    if (likeStatus) {
        likeStatus.style.display = data.liked ? 'block' : 'none';
    }

    // 更新评论显示
    const reviewDisplay = document.querySelector('.review-display');
    if (reviewDisplay) {
        reviewDisplay.style.display = data.has_review ? 'block' : 'none';
        if (data.has_review) {
            reviewDisplay.querySelector('p').textContent = data.review_text;
        }
    }
}

function updateFilmStats(stats) {
    // 更新电影平均评分
    const ratingElements = document.querySelectorAll('.rating-value');
    ratingElements.forEach(element => {
        if (stats.average_rating > 0) {
            element.textContent = stats.average_rating.toFixed(1);
        }
    });

    // 更新点赞数量
    const likeCountElements = document.querySelectorAll('.likes');
    likeCountElements.forEach(element => {
        element.textContent = `${stats.like_count} 人喜欢`;
    });

    // 更新评分人数
    const ratingCountElements = document.querySelectorAll('.rating-count');
    ratingCountElements.forEach(element => {
        element.textContent = `(${stats.rating_count}人评分)`;
    });
}

function showMessage(message, type = 'info') {
    // 创建消息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.setAttribute('role', 'alert');
    messageDiv.textContent = message;

    // 添加到页面顶部
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(messageDiv, container.firstChild);

    // 3秒后自动移除
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

function getFilmIdFromUrl() {
    const match = window.location.pathname.match(/\/films\/(\d+)/);
    return match ? match[1] : null;
}

// 向后兼容的函数
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
