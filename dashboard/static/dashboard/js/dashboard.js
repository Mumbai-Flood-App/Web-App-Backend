// Dashboard download functionality
$(document).ready(function() {
    // Handle download button clicks
    $('.download-btn').click(function() {
        const source = $(this).data('source');
        const startDate = $('#start_date').val();
        const endDate = $('#end_date').val();
        window.location.href = `/dashboard/download/${source}/?start_date=${startDate}&end_date=${endDate}`;
    });
});
