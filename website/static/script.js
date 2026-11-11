/**
 * QuickNotes - Client-side Interactive Scripts
 * Single Page Application Note Management & Security UI
 */

document.addEventListener('DOMContentLoaded', () => {
    initCharCounter();
    initSearchFilter();
    initPasswordStrengthChecker();
    initAutoDismissAlerts();
});

// CSRF Token Helper
function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : '';
}

/* ========================================================
   Character Counter for Note Creation
   ======================================================== */
function initCharCounter() {
    const textarea = document.getElementById('noteContentInput');
    const counter = document.getElementById('charCounter');
    const clearBtn = document.getElementById('clearNoteBtn');

    if (!textarea || !counter) return;

    const updateCount = () => {
        const len = textarea.value.length;
        counter.textContent = `${len} / 5000`;
        if (len > 5000) {
            counter.style.color = 'var(--danger)';
        } else {
            counter.style.color = 'var(--text-muted)';
        }
    };

    textarea.addEventListener('input', updateCount);
    updateCount();

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            textarea.value = '';
            updateCount();
            textarea.focus();
        });
    }
}

/* ========================================================
   Real-Time Live Search Filter
   ======================================================== */
function initSearchFilter() {
    const searchInput = document.getElementById('noteSearchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const notesGrid = document.getElementById('notesGrid');
    const noResults = document.getElementById('noSearchResults');
    const visibleCounter = document.getElementById('visibleNotesCount');

    if (!searchInput || !notesGrid) return;

    const performFilter = () => {
        const query = searchInput.value.toLowerCase().trim();
        const noteCards = notesGrid.querySelectorAll('.note-card');
        let matchedCount = 0;

        if (clearSearchBtn) {
            clearSearchBtn.style.display = query.length > 0 ? 'block' : 'none';
        }

        noteCards.forEach(card => {
            const noteTextElem = card.querySelector('.note-text');
            const noteText = noteTextElem ? noteTextElem.textContent.toLowerCase() : '';

            if (noteText.includes(query)) {
                card.style.display = '';
                matchedCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (visibleCounter) {
            visibleCounter.textContent = matchedCount;
        }

        if (noResults) {
            if (matchedCount === 0 && noteCards.length > 0 && query.length > 0) {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
            }
        }
    };

    searchInput.addEventListener('input', performFilter);

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            performFilter();
            searchInput.focus();
        });
    }
}

/* ========================================================
   Password Strength Checker (Sign Up Page)
   ======================================================== */
function initPasswordStrengthChecker() {
    const pwdInput = document.getElementById('password');
    if (!pwdInput) return;

    const ruleLength = document.getElementById('rule-length');
    const ruleUpper = document.getElementById('rule-upper');
    const ruleLower = document.getElementById('rule-lower');
    const ruleNumber = document.getElementById('rule-number');
    const ruleSpecial = document.getElementById('rule-special');

    pwdInput.addEventListener('input', () => {
        const val = pwdInput.value;

        toggleRule(ruleLength, val.length >= 8);
        toggleRule(ruleUpper, /[A-Z]/.test(val));
        toggleRule(ruleLower, /[a-z]/.test(val));
        toggleRule(ruleNumber, /\d/.test(val));
        toggleRule(ruleSpecial, /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(val));
    });

    function toggleRule(element, isValid) {
        if (!element) return;
        if (isValid) {
            element.classList.add('valid');
        } else {
            element.classList.remove('valid');
        }
    }
}

/* ========================================================
   Auto-dismiss Flash Alerts
   ======================================================== */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentElement) {
                alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-6px)';
                setTimeout(() => alert.remove(), 400);
            }
        }, 6000);
    });
}

function showFlashNotification(message, category = 'success') {
    const wrapper = document.querySelector('.alerts-wrapper');
    if (!wrapper) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${category}`;
    alert.setAttribute('role', 'alert');

    const icon = category === 'success' ? '✓' : (category === 'error' ? '⚠️' : 'ℹ️');
    alert.innerHTML = `
        <span class="alert-icon">${icon}</span>
        <span class="alert-text">${escapeHtml(message)}</span>
        <button type="button" class="alert-close" onclick="this.parentElement.remove()" aria-label="Close">&times;</button>
    `;

    wrapper.prepend(alert);
    setTimeout(() => {
        if (alert && alert.parentElement) {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 400);
        }
    }, 5000);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/* ========================================================
   Edit Note Modal & AJAX Handling
   ======================================================== */
let currentEditId = null;

function openEditModal(noteId) {
    currentEditId = noteId;
    const contentElem = document.getElementById(`note-content-${noteId}`);
    const textarea = document.getElementById('editNoteTextarea');
    const hiddenId = document.getElementById('editNoteId');
    const modal = document.getElementById('editModal');

    if (!contentElem || !textarea || !modal) return;

    hiddenId.value = noteId;
    textarea.value = contentElem.textContent;
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    textarea.focus();
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
    }
    currentEditId = null;
}

async function handleEditSubmit(event) {
    event.preventDefault();
    const textarea = document.getElementById('editNoteTextarea');
    const saveBtn = document.getElementById('saveEditBtn');
    if (!textarea || !currentEditId) return;

    const newContent = textarea.value.trim();
    if (!newContent) {
        alert('Note content cannot be empty.');
        return;
    }

    if (newContent.length > 5000) {
        alert('Note content exceeds 5000 characters.');
        return;
    }

    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    try {
        const response = await fetch('/edit-note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                noteId: currentEditId,
                content: newContent
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            const contentElem = document.getElementById(`note-content-${currentEditId}`);
            if (contentElem) {
                contentElem.textContent = data.content;
            }

            const card = document.getElementById(`note-card-${currentEditId}`);
            if (card) {
                const metaBox = card.querySelector('.note-meta');
                if (metaBox && !card.querySelector('.note-edited-tag')) {
                    const editedTag = document.createElement('span');
                    editedTag.className = 'note-edited-tag';
                    editedTag.title = 'Last modified';
                    editedTag.textContent = '(edited)';
                    metaBox.appendChild(editedTag);
                }
            }

            showFlashNotification(data.message || 'Note updated successfully!', 'success');
            closeEditModal();
        } else {
            showFlashNotification(data.message || 'Failed to update note.', 'error');
        }
    } catch (err) {
        console.error('Error updating note:', err);
        showFlashNotification('Network or server error while updating note.', 'error');
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save Changes';
    }
}

/* ========================================================
   Delete Note Modal & AJAX Handling
   ======================================================== */
let targetDeleteId = null;

function confirmDeleteNote(noteId) {
    targetDeleteId = noteId;
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
    }
    targetDeleteId = null;
}

async function executeDeleteNote() {
    if (!targetDeleteId) return;

    const btn = document.getElementById('confirmDeleteBtn');
    btn.disabled = true;
    btn.textContent = 'Deleting...';

    try {
        const response = await fetch('/delete-note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                noteId: targetDeleteId
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            const card = document.getElementById(`note-card-${targetDeleteId}`);
            if (card) {
                card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    card.remove();
                    updateNoteCountsAfterDelete();
                }, 300);
            }
            showFlashNotification(data.message || 'Note deleted successfully!', 'success');
            closeDeleteModal();
        } else {
            showFlashNotification(data.message || 'Failed to delete note.', 'error');
        }
    } catch (err) {
        console.error('Error deleting note:', err);
        showFlashNotification('Network or server error while deleting note.', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Delete Permanently';
    }
}

function updateNoteCountsAfterDelete() {
    const totalCountElem = document.getElementById('totalNotesCount');
    const visibleCountElem = document.getElementById('visibleNotesCount');
    const notesGrid = document.getElementById('notesGrid');

    if (!notesGrid) return;
    const remainingCards = notesGrid.querySelectorAll('.note-card');

    if (totalCountElem) totalCountElem.textContent = remainingCards.length;
    if (visibleCountElem) visibleCountElem.textContent = remainingCards.length;

    if (remainingCards.length === 0) {
        notesGrid.innerHTML = `
            <div class="empty-state" id="emptyState">
                <div class="empty-icon">📝</div>
                <h3 class="empty-title">No notes yet</h3>
                <p class="empty-desc">Create your very first note using the box above to get started!</p>
            </div>
        `;
    }
}

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    const editModal = document.getElementById('editModal');
    const deleteModal = document.getElementById('deleteModal');

    if (event.target === editModal) {
        closeEditModal();
    }
    if (event.target === deleteModal) {
        closeDeleteModal();
    }
});

// Close modals on Escape key
window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeEditModal();
        closeDeleteModal();
    }
});
