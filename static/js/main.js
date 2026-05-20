/*
=====================================================
Global JavaScript for Student Management System
=====================================================
*/

document.addEventListener('DOMContentLoaded', function() {
    // 1. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Use Bootstrap's Alert API to close it smoothly
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 2. Enable Bootstrap tooltips globally
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 3. Confirm before submitting delete forms (fallback if template doesn't have custom confirm page)
    const deleteForms = document.querySelectorAll('form.delete-confirm');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if(!confirm('Are you sure you want to delete this item? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});
