// Dropdown list searching functionality
$(document).ready(function() {
    // Initialize Select2 on the select element
    $('.select2').select2();

    // Attach the change event to the select element
    $("#dkNumberSelect").on("change", function() {
        var selectedOption = $(this).find(":selected");
        $("#descriptionTextArea").val(selectedOption.data("description"));
    });
});

// Text area for the describing dk_numbers
//const selectElement = document.querySelector('#dkNumberSelect');
//const descriptionTextArea = document.querySelector('#descriptionTextArea');
//
//selectElement.addEventListener('change', function() {
//    const selectedOption = selectElement.options[selectElement.selectedIndex];
//    descriptionTextArea.value = selectedOption.getAttribute('data-description');
//});

document.addEventListener('DOMContentLoaded', function() {
    const selectElement = document.querySelector('#dkNumberSelect');
    const descriptionTextArea = document.querySelector('#descriptionTextArea');

    // Function to update description text area
    function updateDescription() {
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        descriptionTextArea.value = selectedOption.getAttribute('data-description');
    }

    // Add event listener to the select element
//    selectElement.addEventListener('change', updateDescription);

    // Call the updateDescription function on page load
    updateDescription();
});
