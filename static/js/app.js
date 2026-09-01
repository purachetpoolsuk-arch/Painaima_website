/**
 * Painaima (ไปไหนมา) - Dynamic Frontend Interactions
 */

// CSRF Token Helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification Manager
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast';
  
  let iconSvg = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="16" x2="12" y2="12"></line>
      <line x1="12" y1="8" x2="12.01" y2="8"></line>
    </svg>`;

  if (type === 'success') {
    iconSvg = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>`;
  } else if (type === 'heart') {
    iconSvg = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="#f43f5e" stroke="#f43f5e" stroke-width="2">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
      </svg>`;
  }

  toast.innerHTML = `${iconSvg}<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// Like Post Function
async function toggleLike(postId, btnElement) {
  if (!btnElement) return;
  try {
    const res = await fetch(`/p/${postId}/like/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      }
    });

    if (res.status === 403 || res.redirected) {
      window.location.href = '/accounts/login/';
      return;
    }

    const data = await res.json();
    if (data.success) {
      if (data.liked) {
        btnElement.classList.add('liked');
      } else {
        btnElement.classList.remove('liked');
      }

      // Update count text if exists
      const countEl = document.querySelector(`.likes-count-text-${postId}`);
      if (countEl) {
        countEl.textContent = `${data.likes_count} ถูกใจ`;
      }
      const btnCountEl = btnElement.querySelector('.like-btn-count');
      if (btnCountEl) {
        btnCountEl.textContent = data.likes_count;
      }
    }
  } catch (err) {
    console.error('Like error:', err);
  }
}

// Double Click Image to Like
function handleImageDoubleClick(event, postId) {
  const container = event.currentTarget;
  const heartAnim = container.querySelector('.heart-pop-animation');
  
  if (heartAnim) {
    heartAnim.classList.remove('active');
    void heartAnim.offsetWidth; // Trigger reflow
    heartAnim.classList.add('active');
  }

  const likeBtn = document.querySelector(`.like-btn-${postId}`);
  if (likeBtn && !likeBtn.classList.contains('liked')) {
    toggleLike(postId, likeBtn);
  }
}

// Bookmark Post Function
async function toggleBookmark(postId, btnElement) {
  if (!btnElement) return;
  try {
    const res = await fetch(`/p/${postId}/bookmark/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      }
    });

    if (res.status === 403 || res.redirected) {
      window.location.href = '/accounts/login/';
      return;
    }

    const data = await res.json();
    if (data.success) {
      if (data.bookmarked) {
        btnElement.classList.add('bookmarked');
        showToast('บันทึกโพสต์ไว้ในคอลเลกชันแล้ว', 'success');
      } else {
        btnElement.classList.remove('bookmarked');
        showToast('นำออกจากบันทึกแล้ว');
      }
    }
  } catch (err) {
    console.error('Bookmark error:', err);
  }
}

// Follow / Unfollow Toggle
async function toggleFollow(username, btnElement) {
  if (!btnElement) return;
  try {
    const res = await fetch(`/u/toggle-follow/${username}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      }
    });

    if (res.status === 403 || res.redirected) {
      window.location.href = '/accounts/login/';
      return;
    }

    const data = await res.json();
    if (data.success) {
      if (data.is_following) {
        btnElement.textContent = 'กำลังติดตาม';
        btnElement.classList.add('following');
        showToast(data.message, 'success');
      } else {
        btnElement.textContent = 'ติดตาม';
        btnElement.classList.remove('following');
        showToast(data.message);
      }

      // Update follower count in profile header if exists
      const followersEl = document.getElementById('profile-followers-count');
      if (followersEl) {
        followersEl.textContent = data.followers_count;
      }
    }
  } catch (err) {
    console.error('Follow error:', err);
  }
}

// Share Post Modal & Options
let currentSharePostId = null;
let currentSharePostUrl = null;
let currentSharePostAuthor = null;

function openShareModal(postId, postUrl, postAuthor) {
  currentSharePostId = postId;
  currentSharePostUrl = postUrl;
  currentSharePostAuthor = postAuthor;

  const modal = document.getElementById('share-modal');
  if (modal) {
    modal.classList.add('active');

    // Bind Share to Story
    const btnStory = document.getElementById('btn-share-to-story');
    if (btnStory) {
      btnStory.onclick = () => shareToStory(postId);
    }

    // Bind Copy Link
    const btnCopy = document.getElementById('btn-copy-link');
    if (btnCopy) {
      btnCopy.onclick = () => {
        const fullUrl = window.location.origin + postUrl;
        navigator.clipboard.writeText(fullUrl).then(() => {
          closeShareModal();
          showToast('คัดลอกลิงก์โพสต์เรียบร้อยแล้ว!', 'success');
        }).catch(() => {
          prompt('คัดลอกลิงก์:', fullUrl);
        });
      };
    }

    // Bind Share Apps
    const btnApps = document.getElementById('btn-share-apps');
    if (btnApps) {
      btnApps.onclick = () => {
        const fullUrl = window.location.origin + postUrl;
        closeShareModal();
        if (navigator.share) {
          navigator.share({
            title: `โพสต์โดย ${postAuthor} บน Painaima`,
            text: 'แชร์รูปสวยๆ จาก ไปไหนมา (Painaima)',
            url: fullUrl,
          }).catch((e) => console.log('Share dismissed', e));
        } else {
          navigator.clipboard.writeText(fullUrl).then(() => {
            showToast('คัดลอกลิงก์โพสต์เรียบร้อยแล้ว!', 'success');
          });
        }
      };
    }
  }
}

function closeShareModal() {
  const modal = document.getElementById('share-modal');
  if (modal) modal.classList.remove('active');
}

// Share to My Story AJAX
async function shareToStory(postId) {
  closeShareModal();
  try {
    const res = await fetch(`/p/${postId}/share-story/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      }
    });

    if (res.status === 403 || res.redirected) {
      window.location.href = '/accounts/login/';
      return;
    }

    const data = await res.json();
    if (data.success) {
      showToast(data.message || 'แชร์ลงสตอรี่ของคุณเรียบร้อยแล้ว!', 'success');
    }
  } catch (err) {
    console.error('Share to story error:', err);
    showToast('เกิดข้อผิดพลาดในการแชร์ลงสตอรี่');
  }
}

// ==========================================================================
// Create Story Modal Functions
// ==========================================================================
function openCreateStoryModal() {
  const modal = document.getElementById('create-story-modal');
  if (modal) {
    modal.classList.add('active');
  }
}

function closeCreateStoryModal() {
  const modal = document.getElementById('create-story-modal');
  if (modal) {
    modal.classList.remove('active');
  }
}

// Setup Create Story File Dropzone & Previews
document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('story-dropzone');
  const fileInput = document.getElementById('story-file-input');
  const previewImg = document.getElementById('story-preview-img');
  const previewVideo = document.getElementById('story-preview-video');
  const dropPrompt = document.getElementById('story-dropzone-prompt');

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleStoryMediaPreview(fileInput.files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) {
        handleStoryMediaPreview(fileInput.files[0]);
      }
    });

    function handleStoryMediaPreview(file) {
      if (!file) return;

      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previewImg.src = e.target.result;
          previewImg.style.display = 'block';
          previewVideo.style.display = 'none';
          if (dropPrompt) dropPrompt.style.display = 'none';
        };
        reader.readAsDataURL(file);
      } else if (file.type.startsWith('video/')) {
        const url = URL.createObjectURL(file);
        previewVideo.src = url;
        previewVideo.style.display = 'block';
        previewImg.style.display = 'none';
        if (dropPrompt) dropPrompt.style.display = 'none';
      }
    }
  }
});

// ==========================================================================
// ==========================================================================
// Story Viewer with Multi-Story & Seamless Next/Prev Navigation
// ==========================================================================
let storyTimer = null;
let currentStoryData = [];
let currentStoryIndex = 0;
let currentStoryUsername = null;
let currentStoryUserObj = null;
let currentUserQueueIndex = 0;

function getStoryQueue() {
  if (window.storyUsernamesQueue && window.storyUsernamesQueue.length > 0) {
    return window.storyUsernamesQueue;
  }
  // Fallback: collect from rings in DOM
  const rings = document.querySelectorAll('[id^="story-ring-"]');
  const queue = [];
  rings.forEach(r => {
    const u = r.id.replace('story-ring-', '');
    if (u && !queue.includes(u)) queue.push(u);
  });
  return queue;
}

async function openStoryViewer(username, startAtLast = false) {
  const queue = getStoryQueue();
  currentUserQueueIndex = queue.indexOf(username);
  if (currentUserQueueIndex === -1) {
    currentUserQueueIndex = 0;
  }

  currentStoryUsername = username;
  const modal = document.getElementById('story-viewer-modal');
  if (!modal) return;

  try {
    const res = await fetch(`/p/api/stories/${username}/`);
    const data = await res.json();

    if (!data.stories || data.stories.length === 0) {
      showToast(`@${username} ยังไม่มีสตอรี่ที่ใช้งานอยู่ในขณะนี้`);
      return;
    }

    currentStoryData = data.stories;
    currentStoryUserObj = data.user;
    currentStoryIndex = startAtLast ? currentStoryData.length - 1 : 0;
    
    // Mark ring as seen on the page
    const ringEl = document.getElementById(`story-ring-${username}`);
    if (ringEl) {
      ringEl.style.background = 'var(--border-subtle)';
    }

    modal.classList.add('active');
    renderStorySlide(data.user, currentStoryIndex);

  } catch (err) {
    console.error('Story viewer error:', err);
  }
}

function renderStorySlide(user, index) {
  if (index >= currentStoryData.length) {
    goToNextStory();
    return;
  }

  const story = currentStoryData[index];
  const avatarEl = document.getElementById('story-user-avatar');
  const nameEl = document.getElementById('story-user-name');
  const timeEl = document.getElementById('story-time');
  const imgEl = document.getElementById('story-image');
  const videoEl = document.getElementById('story-video');
  const captionEl = document.getElementById('story-caption-text');
  const postLinkEl = document.getElementById('story-post-link');
  const likeSvg = document.getElementById('story-like-svg');

  avatarEl.src = user.avatar_url;
  nameEl.textContent = user.display_name || user.username;
  timeEl.textContent = story.created_at;
  captionEl.textContent = story.caption || '';

  // Handle Image vs Video
  if (story.media_type === 'video') {
    imgEl.style.display = 'none';
    videoEl.src = story.media_url;
    videoEl.style.display = 'block';
    videoEl.currentTime = 0;
    videoEl.play().catch(e => console.log('Autoplay muted'));
  } else {
    videoEl.style.display = 'none';
    imgEl.src = story.media_url;
    imgEl.style.display = 'block';
  }

  if (story.shared_post_url) {
    postLinkEl.href = story.shared_post_url;
    postLinkEl.style.display = 'inline-flex';
  } else {
    postLinkEl.style.display = 'none';
  }

  // Update Heart like icon
  if (story.has_liked) {
    likeSvg.style.fill = '#f43f5e';
    likeSvg.style.stroke = '#f43f5e';
  } else {
    likeSvg.style.fill = 'none';
    likeSvg.style.stroke = '#ffffff';
  }

  // Multi-segment Progress Bar Rendering
  renderProgressBars(index, story.media_type === 'video' ? 8000 : 5000);

  // Update Navigation Arrows State
  const queue = getStoryQueue();
  const prevBtn = document.getElementById('story-prev-btn');
  const nextBtn = document.getElementById('story-next-btn');
  
  // Show Prev button if there is a previous story of this user OR a previous user
  const hasPrev = index > 0 || currentUserQueueIndex > 0;
  if (prevBtn) prevBtn.style.display = hasPrev ? 'flex' : 'none';
  if (nextBtn) nextBtn.style.display = 'flex';

  const duration = story.media_type === 'video' ? 8000 : 5000;
  clearTimeout(storyTimer);
  storyTimer = setTimeout(() => {
    goToNextStory();
  }, duration);
}

function renderProgressBars(currentIndex, duration) {
  const container = document.getElementById('story-progress-container');
  if (!container) return;

  container.innerHTML = '';
  const total = currentStoryData.length;

  for (let i = 0; i < total; i++) {
    const seg = document.createElement('div');
    seg.style.flex = '1';
    seg.style.height = '100%';
    seg.style.background = 'rgba(255,255,255,0.3)';
    seg.style.borderRadius = '3px';
    seg.style.overflow = 'hidden';

    const fill = document.createElement('div');
    fill.style.height = '100%';

    if (i < currentIndex) {
      fill.style.width = '100%';
      fill.style.background = '#ffffff';
    } else if (i === currentIndex) {
      fill.style.width = '0%';
      fill.style.background = '#ffffff';
      fill.style.animation = `storyProgressAnim ${duration / 1000}s linear forwards`;
    } else {
      fill.style.width = '0%';
    }

    seg.appendChild(fill);
    container.appendChild(seg);
  }
}

function goToPrevStory() {
  clearTimeout(storyTimer);
  
  if (currentStoryIndex > 0) {
    currentStoryIndex--;
    renderStorySlide(currentStoryUserObj, currentStoryIndex);
  } else {
    // Go to previous user's last story
    const queue = getStoryQueue();
    if (currentUserQueueIndex > 0) {
      currentUserQueueIndex--;
      const prevUsername = queue[currentUserQueueIndex];
      openStoryViewer(prevUsername, true); // true = start at last story of previous user
    }
  }
}

function goToNextStory() {
  clearTimeout(storyTimer);

  if (currentStoryIndex < currentStoryData.length - 1) {
    currentStoryIndex++;
    renderStorySlide(currentStoryUserObj, currentStoryIndex);
  } else {
    // Advance to next user's first story
    const queue = getStoryQueue();
    if (currentUserQueueIndex < queue.length - 1) {
      currentUserQueueIndex++;
      const nextUsername = queue[currentUserQueueIndex];
      openStoryViewer(nextUsername, false);
    } else {
      closeStoryViewer();
    }
  }
}

function closeStoryViewer() {
  const modal = document.getElementById('story-viewer-modal');
  const videoEl = document.getElementById('story-video');
  if (videoEl) videoEl.pause();
  if (modal) modal.classList.remove('active');
  clearTimeout(storyTimer);
}

// Like Current Story with Floating Hearts Animation
async function triggerStoryLike() {
  if (currentStoryIndex >= currentStoryData.length) return;
  const currentStory = currentStoryData[currentStoryIndex];
  const likeSvg = document.getElementById('story-like-svg');

  // Launch floating heart particles
  for (let i = 0; i < 4; i++) {
    setTimeout(() => createFloatingHeart(), i * 120);
  }

  try {
    const res = await fetch(`/p/story/${currentStory.id}/like/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
      }
    });

    const data = await res.json();
    if (data.success) {
      currentStory.has_liked = data.liked;
      if (data.liked) {
        likeSvg.style.fill = '#f43f5e';
        likeSvg.style.stroke = '#f43f5e';
      } else {
        likeSvg.style.fill = 'none';
        likeSvg.style.stroke = '#ffffff';
      }
    }
  } catch (err) {
    console.error('Story like error:', err);
  }
}

function createFloatingHeart() {
  const container = document.getElementById('floating-hearts-container');
  if (!container) return;

  const heart = document.createElement('div');
  const randomX = 70 + Math.random() * 20; // Near bottom right like button
  const randomSize = 24 + Math.random() * 18;

  heart.innerHTML = `
    <svg width="${randomSize}" height="${randomSize}" viewBox="0 0 24 24" fill="#f43f5e" stroke="#fff" stroke-width="1.5">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
    </svg>
  `;
  heart.style.position = 'absolute';
  heart.style.right = `${100 - randomX}%`;
  heart.style.bottom = '80px';
  heart.style.pointerEvents = 'none';
  heart.style.animation = 'floatUp 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards';

  container.appendChild(heart);
  setTimeout(() => heart.remove(), 1200);
}

// Reply to Story AJAX
async function submitStoryReply(e) {
  e.preventDefault();
  if (currentStoryIndex >= currentStoryData.length) return;
  const currentStory = currentStoryData[currentStoryIndex];
  const input = document.getElementById('story-reply-input');
  const text = input.value.trim();

  if (!text) return;

  const formData = new FormData();
  formData.append('text', text);

  try {
    const res = await fetch(`/p/story/${currentStory.id}/reply/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
      },
      body: formData,
    });

    const data = await res.json();
    if (data.success) {
      input.value = '';
      showToast(data.message || 'ส่งข้อความแล้ว!', 'success');
    }
  } catch (err) {
    console.error('Reply error:', err);
  }
}



// Inline Comment AJAX Submission
document.addEventListener('submit', async function(e) {
  if (e.target && e.target.classList.contains('inline-comment-form')) {
    e.preventDefault();
    const form = e.target;
    const postId = form.dataset.postId;
    const input = form.querySelector('.comment-input');
    const text = input.value.trim();

    if (!text) return;

    const formData = new FormData();
    formData.append('text', text);
    formData.append('is_ajax', '1');

    try {
      const res = await fetch(`/p/${postId}/comment/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
      });

      if (res.status === 403 || res.redirected) {
        window.location.href = '/accounts/login/';
        return;
      }

      const data = await res.json();
      if (data.success) {
        input.value = '';
        
        // Append comment item to post comment list
        const listEl = document.querySelector(`.post-comments-list-${postId}`);
        if (listEl) {
          const item = document.createElement('div');
          item.className = 'comment-item';
          item.innerHTML = `
            <div>
              <a href="/u/${data.comment.user}/" class="comment-author">${data.comment.display_name || data.comment.user}</a>
              <span class="comment-text">${data.comment.text}</span>
            </div>
          `;
          listEl.appendChild(item);
        }

        // Update comment count on post detail
        const countEl = document.querySelector(`.comments-count-text-${postId}`);
        if (countEl) {
          countEl.textContent = `${data.comments_count} ความคิดเห็น`;
        }

        showToast('เพิ่มความคิดเห็นแล้ว', 'success');
      }
    } catch (err) {
      console.error('Comment error:', err);
    }
  }
});

// Real-time Global Search Autocomplete
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('global-search-input');
  const autocompleteBox = document.getElementById('search-autocomplete');

  if (searchInput && autocompleteBox) {
    let debounceTimer;

    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      const query = searchInput.value.trim();

      if (query.length === 0) {
        autocompleteBox.style.display = 'none';
        autocompleteBox.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
          const data = await res.json();

          let html = '';

          if (data.users && data.users.length > 0) {
            html += '<div class="autocomplete-section-title">ผู้ใช้งาน</div>';
            data.users.forEach(u => {
              html += `
                <a href="${u.url}" class="autocomplete-item">
                  <img src="${u.avatar_url}" class="avatar-sm" alt="${u.username}">
                  <div>
                    <div style="font-weight:700; font-size:0.88rem;">${u.display_name}</div>
                    <div style="font-size:0.75rem; color:var(--text-muted);">@${u.username}</div>
                  </div>
                </a>
              `;
            });
          }

          if (data.tags && data.tags.length > 0) {
            html += '<div class="autocomplete-section-title">แฮชแท็ก</div>';
            data.tags.forEach(t => {
              html += `
                <a href="${t.url}" class="autocomplete-item">
                  <div style="font-weight:700; color:var(--accent-indigo);">#${t.name}</div>
                  <div style="font-size:0.75rem; color:var(--text-muted); margin-left:auto;">${t.posts_count} โพสต์</div>
                </a>
              `;
            });
          }

          if (data.locations && data.locations.length > 0) {
            html += '<div class="autocomplete-section-title">สถานที่</div>';
            data.locations.forEach(l => {
              html += `
                <a href="${l.url}" class="autocomplete-item">
                  <div style="font-weight:600; color:var(--accent-cyan);">${l.name}</div>
                  <div style="font-size:0.75rem; color:var(--text-muted); margin-left:auto;">${l.count} โพสต์</div>
                </a>
              `;
            });
          }

          if (html === '') {
            html = '<div style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 0.88rem;">ไม่พบผลการค้นหา</div>';
          }

          autocompleteBox.innerHTML = html;
          autocompleteBox.style.display = 'block';
        } catch (err) {
          console.error('Search error:', err);
        }
      }, 250);
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !autocompleteBox.contains(e.target)) {
        autocompleteBox.style.display = 'none';
      }
    });
  }

  // Image Upload Dropzone Preview
  const dropzone = document.getElementById('post-dropzone');
  const fileInput = document.getElementById('post-image-upload');
  const previewImg = document.getElementById('post-preview-image');
  const dropzoneContent = document.getElementById('dropzone-content');

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        updatePreview(fileInput.files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) {
        updatePreview(fileInput.files[0]);
      }
    });

    function updatePreview(file) {
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previewImg.src = e.target.result;
          previewImg.style.display = 'block';
          if (dropzoneContent) dropzoneContent.style.display = 'none';
        };
        reader.readAsDataURL(file);
      }
    }
  }
});

// Connections Modal (Followers / Following)
async function openConnectionsModal(username, type) {
  const modalBackdrop = document.getElementById('connections-modal');
  const modalTitle = document.getElementById('connections-modal-title');
  const modalList = document.getElementById('connections-modal-list');

  if (!modalBackdrop || !modalTitle || !modalList) return;

  modalTitle.textContent = type === 'followers' ? 'ผู้ติดตาม' : 'กำลังติดตาม';
  modalList.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-muted);">กำลังโหลด...</div>';
  modalBackdrop.classList.add('active');

  try {
    const res = await fetch(`/u/${username}/connections/${type}/`);
    const data = await res.json();

    if (data.users && data.users.length > 0) {
      let html = '';
      data.users.forEach(u => {
        let actionBtn = '';
        if (u.is_following !== null && !u.is_self) {
          actionBtn = `
            <button class="btn btn-sm btn-follow ${u.is_following ? 'following' : ''}" onclick="toggleFollow('${u.username}', this)">
              ${u.is_following ? 'กำลังติดตาม' : 'ติดตาม'}
            </button>
          `;
        }
        html += `
          <div class="suggested-user-row" style="padding: 10px 16px;">
            <div class="suggested-user-meta">
              <a href="${u.profile_url}">
                <img src="${u.avatar_url}" class="avatar-sm" alt="${u.username}">
              </a>
              <div class="user-name-box">
                <a href="${u.profile_url}" class="user-username-txt">${u.display_name}</a>
                <span class="user-display-txt">@${u.username}</span>
              </div>
            </div>
            ${actionBtn}
          </div>
        `;
      });
      modalList.innerHTML = html;
    } else {
      modalList.innerHTML = '<div style="padding: 28px; text-align: center; color: var(--text-muted);">ยังไม่มีข้อมูลในส่วนนี้</div>';
    }
  } catch (err) {
    modalList.innerHTML = '<div style="padding: 20px; text-align: center; color: #ef4444;">เกิดข้อผิดพลาดในการโหลด</div>';
  }
}

function closeConnectionsModal() {
  const modalBackdrop = document.getElementById('connections-modal');
  if (modalBackdrop) modalBackdrop.classList.remove('active');
}
