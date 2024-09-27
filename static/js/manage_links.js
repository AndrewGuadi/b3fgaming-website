// manage_links.js

document.addEventListener('DOMContentLoaded', function () {
    const platformSelect = document.getElementById('platform_id');
    const customPlatformField = document.getElementById('custom-platform-field');

    function toggleCustomPlatform() {
        if (platformSelect.value === 'Custom') {
            customPlatformField.style.display = 'block';
        } else {
            customPlatformField.style.display = 'none';
        }
    }

    platformSelect.addEventListener('change', toggleCustomPlatform);

    // Initial toggle based on current selection (for edit pages)
    toggleCustomPlatform();
});
