// Modular modal initialization to avoid cross-modal interference
(function () {
    // Utility: show image preview from a File input
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

    // Initialize Add modal behavior (fully scoped)
    function initAddModal() {
        const addAdminBtn = document.getElementById('add-admin-btn');
        const addModal = document.getElementById('add-admin-modal');
        const addModalCloseBtn = document.getElementById('add-modal-close-btn');
        const addForm = document.getElementById('add-admin-form');
        if (!addModal || !addForm) return;

        const addImageInput = addForm.querySelector('input[type="file"][name="image"]') || addForm.querySelector('input[type="file"]');
        const addPreviewImg = document.getElementById('add-image-preview');
        const addPlaceholderIcon = document.getElementById('add-image-placeholder');
        const addPreviewContainer = document.getElementById('add-image-preview-container');

        function openAddModal() {
            addModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        function closeAddModal() {
            addModal.classList.remove('active');
            document.body.style.overflow = 'auto';
            try { addForm.reset(); } catch (e) { }
            if (addPreviewImg) { addPreviewImg.style.display = 'none'; addPreviewImg.src = '#'; }
            if (addPlaceholderIcon) addPlaceholderIcon.style.display = 'block';
        }

        if (addAdminBtn) addAdminBtn.addEventListener('click', openAddModal);
        if (addModalCloseBtn) addModalCloseBtn.addEventListener('click', closeAddModal);
        addModal.addEventListener('click', (e) => { if (e.target === addModal) closeAddModal(); });

        // scoped image bindings
        if (addImageInput && addPreviewImg) {
            addImageInput.addEventListener('change', function () {
                showPreviewFromFileInput(addImageInput, addPreviewImg, addPlaceholderIcon);
            });
            if (addPreviewContainer) {
                addPreviewContainer.style.cursor = 'pointer';
                addPreviewContainer.addEventListener('click', function () { try { addImageInput.click(); } catch (e) { } });
            }
        }

        // safe submit handler
        if (addForm) {
            addForm.addEventListener('submit', function () {
                console.log('Add admin form submitted');
            });
        }
    }

    // Initialize Edit modal behavior (fully scoped)
    function initEditModal() {
        const editModal = document.getElementById('edit-admin-modal');
        const editModalCloseBtn = document.getElementById('edit-modal-close-btn');
        const editForm = document.getElementById('edit-admin-form');
        if (!editModal || !editForm) return;

        const editImageInput = document.getElementById('edit-image-input') || editForm.querySelector('input[type="file"][name="image"]');
        const editPreviewImg = document.getElementById('edit-image-preview');
        const editPlaceholderIcon = document.getElementById('edit-image-placeholder');
        const editPreviewContainer = document.getElementById('edit-image-preview-container');

        function closeEditModal() {
            editModal.classList.remove('active');
            document.body.style.overflow = 'auto';
            try { editForm.reset(); } catch (e) { }
            if (editPreviewImg) { editPreviewImg.style.display = 'none'; editPreviewImg.src = '#'; }
            if (editPlaceholderIcon) editPlaceholderIcon.style.display = 'block';
        }

        if (editModalCloseBtn) editModalCloseBtn.addEventListener('click', closeEditModal);
        editModal.addEventListener('click', (e) => { if (e.target === editModal) closeEditModal(); });

        if (editImageInput && editPreviewImg) {
            editImageInput.addEventListener('change', function () {
                showPreviewFromFileInput(editImageInput, editPreviewImg, editPlaceholderIcon);
            });
            if (editPreviewContainer) {
                editPreviewContainer.style.cursor = 'pointer';
                editPreviewContainer.addEventListener('click', function () { try { editImageInput.click(); } catch (e) { } });
            }
        }

        if (editForm) {
            editForm.addEventListener('submit', function () {
                console.log('Edit admin form submitted');
            });
        }

        // Expose a safe open function that templates can call
        window.openEditModal = function (fullName, email, qualification, phone, imageUrl, userId) {
            // scope queries
            const form = document.getElementById('edit-admin-form');
            if (!form) return;

            // Split full name
            const nameParts = (fullName || '').split(' ');
            const firstName = nameParts[0] || '';
            const lastName = nameParts.slice(1).join(' ') || '';

            const firstEl = form.querySelector('[name="first_name"]');
            const lastEl = form.querySelector('[name="last_name"]');
            const emailEl = form.querySelector('[name="email"]');
            const qualEl = form.querySelector('[name="qualification"]');
            const phoneEl = form.querySelector('[name="phone"]');

            if (firstEl) firstEl.value = firstName;
            if (lastEl) lastEl.value = lastName;
            if (emailEl) emailEl.value = email || '';
            if (qualEl) qualEl.value = qualification || '';
            if (phoneEl) phoneEl.value = phone || '';

            // set action
            try {
                form.action = form.getAttribute('action') || '';
                if (userId) form.action = '/admin/edit-admin/' + userId + '/';
            } catch (e) { }

            // preview
            if (editPreviewImg) {
                if (imageUrl && imageUrl !== '#') {
                    editPreviewImg.src = imageUrl;
                    editPreviewImg.style.display = 'block';
                    if (editPlaceholderIcon) editPlaceholderIcon.style.display = 'none';
                } else if (editPreviewImg.src && editPreviewImg.src !== '#' && editPreviewImg.src !== '') {
                    editPreviewImg.style.display = 'block';
                    if (editPlaceholderIcon) editPlaceholderIcon.style.display = 'none';
                } else {
                    editPreviewImg.style.display = 'none';
                    editPreviewImg.src = '#';
                    if (editPlaceholderIcon) editPlaceholderIcon.style.display = 'block';
                }
            }

            // clear file input so change triggers even if same file
            if (editImageInput) {
                try { editImageInput.value = null; } catch (e) { }
                // add a one-time change handler using { once: true }
                editImageInput.addEventListener('change', function onFileChange() {
                    const f = editImageInput.files && editImageInput.files[0];
                    if (f && f.type && f.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = function (ev) {
                            if (editPreviewImg) {
                                editPreviewImg.src = ev.target.result;
                                editPreviewImg.style.display = 'block';
                                if (editPlaceholderIcon) editPlaceholderIcon.style.display = 'none';
                            }
                        };
                        reader.readAsDataURL(f);
                    }
                }, { once: true });
            }

            // open modal
            editModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        };
    }

    // Initialize both modals on DOM ready
    document.addEventListener('DOMContentLoaded', function () {
        initAddModal();
        initEditModal();

        // Global escape key to close any open modal (non-invasive)
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                const addModal = document.getElementById('add-admin-modal');
                const editModal = document.getElementById('edit-admin-modal');
                if (addModal && addModal.classList.contains('active')) {
                    const closeBtn = document.getElementById('add-modal-close-btn');
                    if (closeBtn) closeBtn.click();
                }
                if (editModal && editModal.classList.contains('active')) {
                    const closeBtn = document.getElementById('edit-modal-close-btn');
                    if (closeBtn) closeBtn.click();
                }
            }
        });
    });

    // Confirm and submit delete form
    window.confirmAndSubmitDelete = function (btn) {
        if (!btn) return;
        const ok = confirm('Are you sure you want to delete this admin? This action cannot be undone.');
        if (!ok) return;
        const form = btn.closest('form');
        if (form) form.submit();
    };
})();