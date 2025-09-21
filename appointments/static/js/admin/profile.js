// Modal references
const editModal = document.getElementById('edit-admin-modal');
const addModalCloseBtn = document.getElementById('add-modal-close-btn');
const editModalCloseBtn = document.getElementById('edit-modal-close-btn');

// Close edit modal
function closeEditModal() {
    editModal.classList.remove('active');
    document.body.style.overflow = 'auto';

    // Reset edit form
    const form = document.getElementById('edit-admin-form');
    form.reset();

    // Reset edit image preview
    const previewImg = document.getElementById('edit-image-preview');
    const placeholderIcon = document.getElementById('edit-image-placeholder');
    previewImg.style.display = 'none';
    previewImg.src = '#';
    if (placeholderIcon) placeholderIcon.style.display = 'block';
}

// Open edit modal with pre-filled data
function openEditModal(fullName, email, qualification, phone, imageUrl, userId) {
    // Scope queries to the edit form so we don't accidentally target the add form
    const editForm = document.getElementById('edit-admin-form');
    if (!editForm) return;

    // Split full name into first and last name
    const nameParts = fullName.split(' ');
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';

    // Pre-fill form fields inside editForm using name selectors
    const firstEl = editForm.querySelector('[name="first_name"]');
    const lastEl = editForm.querySelector('[name="last_name"]');
    const emailEl = editForm.querySelector('[name="email"]');
    const qualEl = editForm.querySelector('[name="qualification"]');
    const phoneEl = editForm.querySelector('[name="phone"]');

    if (firstEl) firstEl.value = firstName;
    if (lastEl) lastEl.value = lastName;
    if (emailEl) emailEl.value = email;
    if (qualEl) qualEl.value = qualification;
    if (phoneEl) phoneEl.value = phone;

    // Set edit form action to point to the correct user
    try {
        editForm.action = editForm.getAttribute('action') || '';
        if (userId) {
            // build URL using the known pattern
            editForm.action = '/admin/edit-admin/' + userId + '/';
        }
    } catch (err) { }

    // Set image preview if available (scoped)
    const previewImg = editForm.querySelector('#edit-image-preview') || document.getElementById('edit-image-preview');
    const placeholderIcon = editForm.querySelector('#edit-image-placeholder') || document.getElementById('edit-image-placeholder');
    const fileInput = editForm.querySelector('input[type="file"][name="image"]');

    if (previewImg) {
        if (imageUrl && imageUrl !== '#') {
            previewImg.src = imageUrl;
            previewImg.style.display = 'block';
            if (placeholderIcon) placeholderIcon.style.display = 'none';
        } else if (previewImg.src && previewImg.src !== '#' && previewImg.src !== '') {
            // keep existing preview
            previewImg.style.display = 'block';
            if (placeholderIcon) placeholderIcon.style.display = 'none';
        } else {
            previewImg.style.display = 'none';
            previewImg.src = '#';
            if (placeholderIcon) placeholderIcon.style.display = 'block';
        }
    }

    // Clear file input so change event fires even if same file selected
    if (fileInput) {
        try { fileInput.value = null; } catch (err) { }
        // Attach a one-time change handler to update preview
        fileInput.addEventListener('change', function onFileChange() {
            const f = fileInput.files && fileInput.files[0];
            if (f && f.type && f.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (ev) {
                    if (previewImg) {
                        previewImg.src = ev.target.result;
                        previewImg.style.display = 'block';
                        if (placeholderIcon) placeholderIcon.style.display = 'none';
                    }
                };
                reader.readAsDataURL(f);
            }
            // remove this handler to avoid duplicate binds
            fileInput.removeEventListener('change', onFileChange);
        });
    }

    // Open modal
    editModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}
// Event listeners for close buttons
editModalCloseBtn.addEventListener('click', closeEditModal);

editModal.addEventListener('click', (e) => {
    if (e.target === editModal) {
        closeEditModal();
    }
});

// Close modals with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (editModal.classList.contains('active')) {
            closeEditModal();
        }
    }
});

// Image preview functionality for add/edit modals (works with add_form.image and edit_form.image)
document.addEventListener('DOMContentLoaded', function () {
    // Find the add form's file input (Django may render its own id) - prefer file input inside add-admin-form


    function showPreviewFromFileInput(inputEl, previewImg, placeholderIcon) {
        const file = inputEl.files && inputEl.files[0];
        if (file && file.type && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (ev) {
                previewImg.src = ev.target.result;
                previewImg.style.display = 'block';
                previewImg.style.zIndex = '3';
                if (placeholderIcon) placeholderIcon.style.display = 'none';
            };
            reader.readAsDataURL(file);
        } else {
            previewImg.src = '#';
            previewImg.style.display = 'none';
            if (placeholderIcon) placeholderIcon.style.display = 'block';
        }
    }

    const editImageInput = document.getElementById('edit-image-input');
    const editPreviewImg = document.getElementById('edit-image-preview');
    const editPlaceholderIcon = document.getElementById('edit-image-placeholder');
    const editPreviewContainer = document.getElementById('edit-image-preview-container');

    if (editImageInput && editPreviewImg) {
        editImageInput.addEventListener('change', function () {
            showPreviewFromFileInput(editImageInput, editPreviewImg, editPlaceholderIcon);
        });
        if (editPreviewContainer) {
            editPreviewContainer.style.cursor = 'pointer';
            editPreviewContainer.addEventListener('click', function () {
                try { editImageInput.click(); } catch (err) { /* ignore */ }
            });
        }
    }
});

document.getElementById('edit-admin-form').addEventListener('submit', function (e) {
    // Add your form submission logic here for editing admin
    console.log('Edit admin form submitted');
    // closeEditModal(); // Uncomment to close modal after submission
});