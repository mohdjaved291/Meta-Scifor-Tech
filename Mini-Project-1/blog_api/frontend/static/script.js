/*
Modern Blog Platform JavaScript
Integrates with Django REST API backend - FIXED VERSION
*/

// API Configuration
const API_URL = 'https://mohdjaved25.pythonanywhere.com/api/posts/';
const CATEGORIES_URL = 'https://mohdjaved25.pythonanywhere.com/api/posts/categories/';
const STATS_URL = 'https://mohdjaved25.pythonanywhere.com/api/posts/stats/';

// Global state
let currentPosts = [];
let currentCategories = [];
let currentStats = {};
let selectedCategory = 'all';
let searchQuery = '';
let editingPostId = null;

// DOM elements
const elements = {
    searchInput: document.getElementById('searchInput'),
    clearSearch: document.getElementById('clearSearch'),
    categoryFilters: document.getElementById('categoryFilters'),
    loadingState: document.getElementById('loadingState'),
    postsGrid: document.getElementById('postsGrid'),
    emptyState: document.getElementById('emptyState'),
    totalPosts: document.getElementById('totalPosts'),
    totalViews: document.getElementById('totalViews'),
    totalCategories: document.getElementById('totalCategories'),
    activityList: document.getElementById('activityList'),
    themeToggle: document.getElementById('themeToggle'),
    themeIcon: document.getElementById('themeIcon'),
    newPostBtn: document.getElementById('newPostBtn'),
    refreshPosts: document.getElementById('refreshPosts'),
    clearSearchBtn: document.getElementById('clearSearchBtn'),
    postModal: document.getElementById('postModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalClose: document.getElementById('modalClose'),
    postForm: document.getElementById('postForm'),
    postTitle: document.getElementById('postTitle'),
    postCategory: document.getElementById('postCategory'),
    postExcerpt: document.getElementById('postExcerpt'),
    postContent: document.getElementById('postContent'),
    postImage: document.getElementById('postImage'),
    imagePreview: document.getElementById('imagePreview'),
    previewImg: document.getElementById('previewImg'),
    removeImage: document.getElementById('removeImage'),
    cancelBtn: document.getElementById('cancelBtn'),
    submitBtn: document.getElementById('submitBtn'),
    toastContainer: document.getElementById('toastContainer')
};

// BLOG MODAL FUNCTIONS - DEFINED FIRST
function viewPost(postId) {
    console.log('viewPost called with ID:', postId);
    const post = currentPosts.find(p => p.id == postId);
    if (!post) {
        console.error('Post not found:', postId);
        return;
    }

    showPostModal(post);
}

function showPostModal(post) {
    console.log('Showing modal for post:', post.title);

    // Get or create modal
    let modal = document.getElementById('blogModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'blogModal';
        modal.className = 'blog-modal';
        document.body.appendChild(modal);
    }

    const formattedDate = formatDate(post.created_at);
    const categoryClass = post.category || 'other';

    let imageHtml = '';
    if (post.image_url) {
        imageHtml = `<div class="blog-image-container"><img src="${post.image_url}" alt="${escapeHtml(post.title)}"></div>`;
    }

    modal.innerHTML = `
        <div class="blog-modal-content">
            <div class="blog-modal-header">
                <button class="blog-modal-back" onclick="closePostModal()">
                    <i class="fas fa-arrow-left"></i> Back to Posts
                </button>
                <button class="blog-modal-close" onclick="closePostModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="blog-modal-body">
                ${imageHtml}
                <div class="blog-content">
                    <div class="blog-header">
                        <span class="blog-category-tag ${categoryClass}">${post.category_display || post.category || 'Other'}</span>
                        <h1 class="blog-title">${escapeHtml(post.title)}</h1>
                        <div class="blog-meta-info">
                            <span class="blog-date">${formattedDate}</span>
                            <div class="blog-stats">
                                <span class="blog-reading-time">${post.reading_time || '5 min read'}</span>
                                <span class="blog-views">${(post.view_count || 0).toLocaleString()} views</span>
                            </div>
                        </div>
                    </div>
                    ${post.excerpt ? `<div class="blog-excerpt">${escapeHtml(post.excerpt)}</div>` : ''}
                    <div class="blog-text"><p>${escapeHtml(post.content || '')}</p></div>
                    <div class="blog-actions">
                        <button class="blog-action-btn edit" onclick="editPostFromModal(${post.id})">
                            <i class="fas fa-edit"></i> Edit Post
                        </button>
                        <button class="blog-action-btn delete" onclick="deletePostFromModal(${post.id})">
                            <i class="fas fa-trash"></i> Delete Post
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closePostModal() {
    const modal = document.getElementById('blogModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function editPostFromModal(postId) {
    closePostModal();
    editPost(postId);
}

function deletePostFromModal(postId) {
    closePostModal();
    handleDeletePost(postId);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing app...');
    initializeApp();
    setupEventListeners();
    loadTheme();
});

async function initializeApp() {
    showLoading(true);
    try {
        await Promise.all([loadPosts(), loadCategories(), loadStats()]);
        renderPosts();
        renderCategories();
        renderStats();
        showLoading(false);
    } catch (error) {
        console.error('Error initializing app:', error);
        showToast('Error loading blog data', 'Please check your connection and try again.', 'error');
        showLoading(false);
    }
}

// API Functions
async function loadPosts() {
    try {
        console.log('Loading posts from:', API_URL);
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        currentPosts = data.results || data;
        console.log('Loaded posts:', currentPosts);
        return currentPosts;
    } catch (error) {
        console.error('Error loading posts:', error);
        throw error;
    }
}

async function loadCategories() {
    try {
        const response = await fetch(CATEGORIES_URL);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        currentCategories = await response.json();
        return currentCategories;
    } catch (error) {
        console.error('Error loading categories:', error);
        currentCategories = [
            { category: 'tech', category_display: 'Technology', count: 0 },
            { category: 'design', category_display: 'Design', count: 0 },
            { category: 'business', category_display: 'Business', count: 0 },
            { category: 'lifestyle', category_display: 'Lifestyle', count: 0 },
            { category: 'education', category_display: 'Education', count: 0 },
            { category: 'entertainment', category_display: 'Entertainment', count: 0 }
        ];
        return currentCategories;
    }
}

async function loadStats() {
    try {
        const response = await fetch(STATS_URL);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        currentStats = await response.json();
        return currentStats;
    } catch (error) {
        console.error('Error loading stats:', error);
        currentStats = {
            total_posts: currentPosts.length,
            total_views: currentPosts.reduce((sum, post) => sum + (post.view_count || 0), 0),
            categories: currentCategories
        };
        return currentStats;
    }
}

async function createPost(postData) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(postData)
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to create post');
        }
        const result = await response.json();
        return result.post || result;
    } catch (error) {
        console.error('Error creating post:', error);
        throw error;
    }
}

async function updatePost(postId, postData) {
    try {
        const response = await fetch(`${API_URL}${postId}/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(postData)
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to update post');
        }
        const result = await response.json();
        return result.post || result;
    } catch (error) {
        console.error('Error updating post:', error);
        throw error;
    }
}

async function deletePost(postId) {
    try {
        const response = await fetch(`${API_URL}${postId}/`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete post');
        return true;
    } catch (error) {
        console.error('Error deleting post:', error);
        throw error;
    }
}

// Event Listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');

    if (elements.searchInput) {
        elements.searchInput.addEventListener('input', handleSearch);
    }
    if (elements.clearSearch) {
        elements.clearSearch.addEventListener('click', clearSearchQuery);
    }
    if (elements.clearSearchBtn) {
        elements.clearSearchBtn.addEventListener('click', clearSearchQuery);
    }
    if (elements.newPostBtn) {
        elements.newPostBtn.addEventListener('click', openCreateModal);
    }
    if (elements.refreshPosts) {
        elements.refreshPosts.addEventListener('click', handleRefresh);
    }
    if (elements.themeToggle) {
        elements.themeToggle.addEventListener('click', toggleTheme);
    }
    if (elements.modalClose) {
        elements.modalClose.addEventListener('click', closeModal);
    }
    if (elements.cancelBtn) {
        elements.cancelBtn.addEventListener('click', closeModal);
    }
    if (elements.postForm) {
        elements.postForm.addEventListener('submit', handleFormSubmit);
    }
    if (elements.postImage) {
        elements.postImage.addEventListener('change', handleImageSelect);
    }
    if (elements.removeImage) {
        elements.removeImage.addEventListener('click', removeSelectedImage);
    }
    if (elements.postModal) {
        elements.postModal.addEventListener('click', (e) => {
            if (e.target === elements.postModal) closeModal();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.postModal && elements.postModal.classList.contains('active')) {
            closeModal();
        }
    });
}

function handleSearch(e) {
    searchQuery = e.target.value.toLowerCase().trim();
    if (elements.clearSearch) {
        elements.clearSearch.style.display = searchQuery ? 'block' : 'none';
    }
    renderPosts();
}

function clearSearchQuery() {
    searchQuery = '';
    if (elements.searchInput) elements.searchInput.value = '';
    if (elements.clearSearch) elements.clearSearch.style.display = 'none';
    renderPosts();
    showToast('Search Cleared', 'Search query has been cleared.', 'info');
}

function handleCategoryFilter(category) {
    selectedCategory = category;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.querySelector(`[data-category="${category}"]`);
    if (activeBtn) activeBtn.classList.add('active');
    renderPosts();
}

function getFilteredPosts() {
    let filtered = [...currentPosts];
    if (selectedCategory !== 'all') {
        filtered = filtered.filter(post => post.category === selectedCategory);
    }
    if (searchQuery) {
        filtered = filtered.filter(post => {
            const searchableText = [
                post.title,
                post.content,
                post.excerpt,
                post.category_display || post.category
            ].join(' ').toLowerCase();
            return searchableText.includes(searchQuery);
        });
    }
    return filtered;
}

function renderPosts() {
    const filteredPosts = getFilteredPosts();
    if (!elements.postsGrid) {
        console.warn('postsGrid element not found');
        return;
    }

    if (filteredPosts.length === 0) {
        elements.postsGrid.style.display = 'none';
        if (elements.emptyState) elements.emptyState.style.display = 'block';
        return;
    }

    elements.postsGrid.style.display = 'grid';
    if (elements.emptyState) elements.emptyState.style.display = 'none';

    elements.postsGrid.innerHTML = filteredPosts.map(post => createPostCard(post)).join('');
    attachPostEventListeners();
}

function createPostCard(post) {
    const formattedDate = formatDate(post.created_at);
    const categoryClass = post.category || 'other';

    let imageHtml = '';
    if (post.image_url) {
        imageHtml = `<img src="${post.image_url}" alt="${escapeHtml(post.title)}" style="width: 100%; height: 200px; object-fit: cover;">`;
    } else {
        imageHtml = `<div class="gradient-bg ${categoryClass}" style="width: 100%; height: 200px;"></div>`;
    }

    return `
        <div class="post-card" data-post-id="${post.id}" onclick="viewPost(${post.id})">
            <div class="post-image ${categoryClass}">
                ${imageHtml}
            </div>
            <div class="post-content">
                <div class="post-header">
                    <span class="post-category ${categoryClass}">
                        ${post.category_display || post.category || 'Other'}
                    </span>
                    <div class="post-actions" onclick="event.stopPropagation()">
                        <button class="action-btn-small edit" onclick="editPost(${post.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn-small delete" onclick="handleDeletePost(${post.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <h3 class="post-title">${escapeHtml(post.title)}</h3>
                <p class="post-excerpt">${escapeHtml(post.excerpt || post.content?.substring(0, 150) + '...' || '')}</p>
                <div class="post-meta">
                    <div class="post-stats">
                        <div class="post-stat">
                            <i class="fas fa-clock"></i>
                            ${post.reading_time || '5 min read'}
                        </div>
                        <div class="post-stat">
                            <i class="fas fa-eye"></i>
                            ${(post.view_count || 0).toLocaleString()}
                        </div>
                    </div>
                    <time datetime="${post.created_at}">${formattedDate}</time>
                </div>
            </div>
        </div>
    `;
}

function attachPostEventListeners() {
    // Event listeners are now handled by onclick attributes in the HTML
    console.log('Post event listeners attached via onclick attributes');
}

function renderCategories() {
    if (!elements.categoryFilters) return;

    const totalPosts = currentPosts.length;
    let filtersHTML = `
        <button class="filter-btn ${selectedCategory === 'all' ? 'active' : ''}" data-category="all" onclick="handleCategoryFilter('all')">
            <i class="fas fa-filter"></i>
            All Posts
            <span class="category-count">${totalPosts}</span>
        </button>
    `;

    currentCategories.forEach(cat => {
        const isActive = selectedCategory === cat.category;
        filtersHTML += `
            <button class="filter-btn ${isActive ? 'active' : ''}" data-category="${cat.category}" onclick="handleCategoryFilter('${cat.category}')">
                <i class="fas fa-tag"></i>
                ${cat.category_display}
                <span class="category-count">${cat.count}</span>
            </button>
        `;
    });

    elements.categoryFilters.innerHTML = filtersHTML;
}

function renderStats() {
    if (elements.totalPosts) elements.totalPosts.textContent = currentStats.total_posts || 0;
    if (elements.totalViews) elements.totalViews.textContent = (currentStats.total_views || 0).toLocaleString();
    if (elements.totalCategories) elements.totalCategories.textContent = currentCategories.length;

    if (elements.activityList) renderActivity();
}

function renderActivity() {
    if (!elements.activityList) return;

    const activities = [
        { text: `New comment on "Web Development"`, type: 'primary' },
        { text: `Post "Design Systems" published`, type: 'secondary' },
        { text: `${(currentStats.total_views || 0).toLocaleString()} views this week`, type: 'success' }
    ];

    elements.activityList.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-dot ${activity.type}"></div>
            <span class="activity-text">${activity.text}</span>
        </div>
    `).join('');
}

// Modal Functions
function openCreateModal() {
    if (!elements.postModal || !elements.modalTitle || !elements.submitBtn) return;
    editingPostId = null;
    elements.modalTitle.textContent = 'Create New Post';
    elements.submitBtn.textContent = 'Create Post';
    if (elements.postForm) elements.postForm.reset();
    removeSelectedImage();
    openModal();
}

function editPost(postId) {
    const post = currentPosts.find(p => p.id === postId);
    if (!post || !elements.postModal || !elements.modalTitle || !elements.submitBtn) return;

    editingPostId = postId;
    elements.modalTitle.textContent = 'Edit Post';
    elements.submitBtn.textContent = 'Update Post';

    if (elements.postTitle) elements.postTitle.value = post.title;
    if (elements.postCategory) elements.postCategory.value = post.category;
    if (elements.postExcerpt) elements.postExcerpt.value = post.excerpt || '';
    if (elements.postContent) elements.postContent.value = post.content;

    removeSelectedImage();
    openModal();
}

function openModal() {
    if (!elements.postModal) return;
    elements.postModal.classList.add('active');
    document.body.style.overflow = 'hidden';
    if (elements.postTitle) elements.postTitle.focus();
}

function closeModal() {
    if (!elements.postModal) return;
    elements.postModal.classList.remove('active');
    document.body.style.overflow = '';
    editingPostId = null;
    if (elements.postForm) elements.postForm.reset();
    removeSelectedImage();
}

async function handleFormSubmit(e) {
    e.preventDefault();
    if (!elements.postTitle || !elements.postContent || !elements.postCategory || !elements.submitBtn) return;

    const postData = {
        title: elements.postTitle.value.trim(),
        content: elements.postContent.value.trim(),
        category: elements.postCategory.value,
        excerpt: elements.postExcerpt ? elements.postExcerpt.value.trim() || undefined : undefined,
        is_published: true
    };

    if (!postData.title || !postData.content || !postData.category) {
        showToast('Validation Error', 'Please fill in all required fields.', 'error');
        return;
    }

    try {
        elements.submitBtn.disabled = true;
        elements.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + (editingPostId ? 'Updating...' : 'Creating...');

        let result;
        if (editingPostId) {
            result = await updatePost(editingPostId, postData);
            showToast('Post Updated', 'Your post has been updated successfully.', 'success');
        } else {
            result = await createPost(postData);
            showToast('Post Created', 'Your post has been created successfully.', 'success');
        }

        closeModal();
        await handleRefresh();
    } catch (error) {
        console.error('Error saving post:', error);
        showToast('Error', error.message || 'Failed to save post. Please try again.', 'error');
    } finally {
        elements.submitBtn.disabled = false;
        elements.submitBtn.textContent = editingPostId ? 'Update Post' : 'Create Post';
    }
}

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (file) {
        if (!file.type.startsWith('image/')) {
            showToast('Invalid File', 'Please select an image file.', 'error');
            e.target.value = '';
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            showToast('File Too Large', 'Please select an image smaller than 5MB.', 'error');
            e.target.value = '';
            return;
        }
        if (elements.previewImg && elements.imagePreview) {
            const reader = new FileReader();
            reader.onload = function (e) {
                elements.previewImg.src = e.target.result;
                elements.imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }
}

function removeSelectedImage() {
    if (elements.postImage) elements.postImage.value = '';
    if (elements.imagePreview) elements.imagePreview.style.display = 'none';
    if (elements.previewImg) elements.previewImg.src = '';
}

async function handleDeletePost(postId) {
    if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) return;
    try {
        await deletePost(postId);
        showToast('Post Deleted', 'The post has been deleted successfully.', 'success');
        await handleRefresh();
    } catch (error) {
        console.error('Error deleting post:', error);
        showToast('Error', 'Failed to delete post. Please try again.', 'error');
    }
}

// Utility Functions
function showLoading(show) {
    if (!elements.loadingState || !elements.postsGrid || !elements.emptyState) return;
    if (show) {
        elements.loadingState.style.display = 'block';
        elements.postsGrid.style.display = 'none';
        elements.emptyState.style.display = 'none';
    } else {
        elements.loadingState.style.display = 'none';
    }
}

async function handleRefresh() {
    showLoading(true);
    try {
        await Promise.all([loadPosts(), loadCategories(), loadStats()]);
        renderPosts();
        renderCategories();
        renderStats();
        showLoading(false);
        showToast('Refreshed', 'Blog posts have been refreshed successfully.', 'success');
    } catch (error) {
        console.error('Error refreshing:', error);
        showToast('Error', 'Failed to refresh posts. Please try again.', 'error');
        showLoading(false);
    }
}

function formatDate(isoDate) {
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Theme Functions
function loadTheme() {
    const savedTheme = localStorage.getItem('blog-theme') || 'light';
    applyTheme(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
    localStorage.setItem('blog-theme', newTheme);
    showToast('Theme Changed', `Switched to ${newTheme} mode.`, 'info');
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (elements.themeIcon) {
        elements.themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Toast Notifications
function showToast(title, message, type = 'info') {
    if (!elements.toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-title">${escapeHtml(title)}</div>
            <div class="toast-message">${escapeHtml(message)}</div>
        </div>
        <button class="toast-close">
            <i class="fas fa-times"></i>
        </button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => removeToast(toast));
    elements.toastContainer.appendChild(toast);
    setTimeout(() => removeToast(toast), 5000);
}

function removeToast(toast) {
    if (toast && toast.parentNode) {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }
}

// Global functions for onclick handlers
window.handleCategoryFilter = handleCategoryFilter;
window.editPost = editPost;
window.handleDeletePost = handleDeletePost;
window.viewPost = viewPost;
window.closePostModal = closePostModal;
window.editPostFromModal = editPostFromModal;
window.deletePostFromModal = deletePostFromModal;