// static/script.js

// --- Core Modal Show/Hide Logic ---
function showModal(modalElement) {
    if (modalElement) {
        modalElement.style.display = "block";
    }
}

function hideModal(modalElement) {
    if (modalElement) {
        modalElement.style.display = "none";
        // Reset form on close
        const form = modalElement.querySelector('form');
        if (form) {
            form.reset();
        }
         // Clear dynamic fields and hidden IDs in generic edit modal
        if(modalElement.id === 'genericEditModal') {
            const fieldsContainer = document.getElementById("genericEditFields");
            if(fieldsContainer) fieldsContainer.innerHTML = '';
            // Reset hidden ID fields
            const gameIdInput = document.getElementById("generic_edit_game_id");
            const reviewGameIdInput = document.getElementById("generic_edit_game_review_id");
            const reviewIdInput = document.getElementById("generic_edit_review_id");
            const productIdInput = document.getElementById("generic_edit_product_id");
            if(gameIdInput) gameIdInput.value = '';
            if(reviewGameIdInput) reviewGameIdInput.value = '';
            if(reviewIdInput) reviewIdInput.value = '';
            if(productIdInput) productIdInput.value = '';
        }
    }
}

// --- Handle Clicks Outside Modals ---
window.onclick = function(event) {
    const genericEditModal = document.getElementById("genericEditModal");
    const addGameModal = document.getElementById("addGameModal");

    if (genericEditModal && event.target === genericEditModal) {
        hideModal(genericEditModal);
    }
    if (addGameModal && event.target === addGameModal) {
        hideModal(addGameModal);
    }
}


// --- Generic AJAX Delete Handler ---
document.addEventListener('DOMContentLoaded', function() {
    const deleteItemIcons = document.querySelectorAll(".delete-item-icon");

    deleteItemIcons.forEach(icon => {
        icon.addEventListener('click', function(event) {
            event.preventDefault();

            const finalDataType = icon.getAttribute('data-type') || 'game';
            let gameId = null;
            let reviewGameId = null;
            let reviewId = null;
            let displayId = '';

            if (finalDataType === 'game') {
                gameId = icon.getAttribute('data-id');
                displayId = gameId;
            } else if (finalDataType === 'review') {
                reviewGameId = icon.getAttribute('data-game-review-id');
                reviewId = icon.getAttribute('data-review-id');
                displayId = `${reviewGameId}/${reviewId}`;
            }

            if ((finalDataType === 'game' && !gameId) || (finalDataType === 'review' && (!reviewGameId || !reviewId))) {
                 alert(`Error: Missing ID information for ${finalDataType} deletion.`);
                 return;
            }

            if (confirm(`Are you sure you want to delete this ${finalDataType} (${displayId})?`)) {
                const formData = new FormData();
                let deleteUrl;

                if (finalDataType === 'game') {
                    deleteUrl = "{{ url_for('delete_game_api') }}";
                    formData.append('item_id', gameId);
                } else if (finalDataType === 'review') {
                    deleteUrl = "{{ url_for('delete_review_api') }}";
                    formData.append('game_review_id', reviewGameId);
                    formData.append('review_id', reviewId);
                }

                fetch(deleteUrl, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                           throw new Error(data.error || `HTTP error! Status: ${response.status}`);
                       }).catch(() => { // Catch JSON parse error on non-ok response
                            return response.text().then(text => {
                                throw new Error(`Non-JSON error response: ${response.status} ${response.statusText} - ${text.substring(0, 200)}...`);
                            });
                       });
                    }
                    return response.json().catch(() => { // Catch JSON parse error on ok response
                         return response.text().then(text => {
                             throw new Error(`Unexpected non-JSON success response: ${response.status} ${response.statusText} - ${text.substring(0, 200)}...`);
                         });
                    });
                })
                .then(data => {
                    if (data.success) {
                        alert(data.message || "Item deleted successfully!");
                        window.location.reload();
                    } else {
                        alert(`Deletion Error: ` + (data.error || "Deletion failed."));
                    }
                })
                .catch(error => {
                    console.error('Fetch Error:', error);
                    alert(`An error occurred during deletion: ` + error.message);
                });
            }
        });
    });
});


// --- Generic Edit Modal Handler ---
function handleEditItemClick(event, linkElement) {
    event.preventDefault();

    const genericEditModal = document.getElementById("genericEditModal");
    const genericEditForm = document.getElementById("genericEditForm");
    const genericEditModalTitle = document.getElementById("genericEditModalTitle");
    const genericEditDataTypeInput = document.getElementById("generic_edit_data_type");
    const genericEditGameIdInput = document.getElementById("generic_edit_game_id");
    const genericEditReviewGameIdInput = document.getElementById("generic_edit_game_review_id");
    const genericEditReviewIdInput = document.getElementById("generic_edit_review_id");
    const genericEditProductIdInput = document.getElementById("generic_edit_product_id");
    const genericEditFieldsContainer = document.getElementById("genericEditFields");

    if (!genericEditModal) return; // Ensure modal exists


    const finalDataType = linkElement.getAttribute('data-type') || 'game'; // Default to 'game'

    let gameId = null;
    let reviewGameId = null;
    let reviewId = null;
    let productId = null; // Product ID for games

    let gameName = '';
    let gameDescription = '';
    let productPrice = '';
    let tradeable = '';

    let reviewComment = '';
    let reviewRatingScore = '';

    // --- Get Data Attributes ---
    if (finalDataType === 'game') {
        // Data from index.html game card or procedures_demo.html table link
        const gameCard = linkElement.closest('.game-card');
        if (gameCard) { // From index.html
            gameId = gameCard.getAttribute('data-game-id');
            gameName = gameCard.getAttribute('data-game-name') || '';
            gameDescription = gameCard.getAttribute('data-game-description') || '';
            productId = gameCard.getAttribute('data-product-id') || null;
            productPrice = gameCard.getAttribute('data-product-price') || '';
            // tradeable = gameCard.getAttribute('data-tradeable') || '';
        } else { // From procedures_demo.html table link (best_seller results)
            gameId = linkElement.getAttribute('data-id');
            gameName = linkElement.getAttribute('data-game-name') || '';
            gameDescription = linkElement.getAttribute('data-game-description') || ''; // May be empty from SP
            productId = linkElement.getAttribute('data-product-id') || null; // May be present if SP includes it
            productPrice = linkElement.getAttribute('data-product-price') || ''; // May be present if SP includes it
            // tradeable = linkElement.getAttribute('data-tradeable') || '';
        }

    } else if (finalDataType === 'review') {
        // Data from procedures_demo.html table link (CommentFilter results)
        reviewGameId = linkElement.getAttribute('data-game-review-id');
        reviewId = linkElement.getAttribute('data-review-id');
        reviewComment = linkElement.getAttribute('data-comment') || '';
        reviewRatingScore = linkElement.getAttribute('data-rating-score') || '';

    } else {
        alert("Unknown data type for editing.");
        return;
    }

    // --- Validate IDs ---
    if ((finalDataType === 'game' && !gameId) || (finalDataType === 'review' && (!reviewGameId || !reviewId))) {
        alert(`Error: Missing required ID information for ${finalDataType} editing.`);
        return;
    }

    // --- Populate Hidden Inputs and Dynamic Fields ---
    hideModal(genericEditModal); // Reset/hide before showing
    genericEditDataTypeInput.value = finalDataType;

    if (finalDataType === 'game') {
        genericEditModalTitle.textContent = 'Edit Game Info';
        genericEditForm.action = "{{ url_for('update_game_api') }}";

        genericEditGameIdInput.value = gameId;
        genericEditProductIdInput.value = productId; // Pass product ID as well, even if SP doesn't use it directly

        // Fields based on UpdateGameInfo SP (Name, Description)
        genericEditFieldsContainer.innerHTML = `
            <div>
                <label for="generic_edit_g_name">Game Name:</label><br>
                <input type="text" id="generic_edit_g_name" name="g_name" value="${gameName}" required>
            </div>
            <br>
            <div>
                <label for="generic_edit_g_description">Description:</label><br>
                <textarea id="generic_edit_g_description" name="g_description">${gameDescription}</textarea>
            </div>
            <br>
            {# If UpdateGameInfo SP was updated to handle price/tradeable, uncomment these #}
            {#
            <div>
                <label for="generic_edit_product_price">Price:</label><br>
                <input type="number" id="generic_edit_product_price" name="product_price" value="${productPrice}" step="0.01" min="0">
            </div>
            <br>
             <div>
                 <label for="generic_edit_tradeable">Tradeable:</label><br>
                 <select id="generic_edit_tradeable" name="tradeable" required>
                     <option value="0" ${tradeable === '0' ? 'selected' : ''}>No</option>
                     <option value="1" ${tradeable === '1' ? 'selected' : ''}>Yes</option>
                 </select>
             </div>
             <br>
            #}
        `;

    } else if (finalDataType === 'review') {
        genericEditModalTitle.textContent = 'Edit Review';
        genericEditForm.action = "{{ url_for('update_review_api') }}";

        genericEditReviewGameIdInput.value = reviewGameId;
        genericEditReviewIdInput.value = reviewId;

        // Fields based on UpdateReviewInfo (Comment, Rating Score)
        genericEditFieldsContainer.innerHTML = `
            <div>
                <label for="generic_edit_comment">Comment:</label><br>
                <textarea id="generic_edit_comment" name="comment">${reviewComment}</textarea>
            </div>
            <br>
            <div>
                <label for="generic_edit_rating_score">Rating Score (1-10):</label><br>
                <input type="number" id="generic_edit_rating_score" name="rating_score" value="${reviewRatingScore}" min="1" max="10" required>
            </div>
            <br>
        `;
    }

    // Show the modal
    showModal(genericEditModal);
}

// --- Generic AJAX Form Submit Handler (for Edit Modal) ---
document.addEventListener('DOMContentLoaded', function() {
    const genericEditForm = document.getElementById("genericEditForm");
    if (genericEditForm) {
         genericEditForm.addEventListener('submit', function(event) {
             event.preventDefault();

             const formData = new FormData(genericEditForm);
             // formData automatically includes hidden inputs by their 'name' attribute
             // (game_id, game_review_id, review_id, product_id, data_type)
             // and dynamic inputs generated in genericEditFields (g_name, g_description, comment, rating_score etc.)

             const formActionUrl = genericEditForm.action; // Get URL from form action

             fetch(formActionUrl, {
                 method: 'POST',
                 body: formData
             })
             .then(response => {
                 if (!response.ok) {
                      return response.json().then(data => {
                          throw new Error(data.error || `HTTP error! Status: ${response.status}`);
                     }).catch(() => { // Catch JSON parse error
                         return response.text().then(text => {
                             throw new Error(`Non-JSON error response: ${response.status} ${response.statusText} - ${text.substring(0, 200)}...`);
                         });
                      });
                 }
                 return response.json().catch(() => { // Catch JSON parse error on success
                      return response.text().then(text => {
                          throw new Error(`Unexpected non-JSON success response: ${response.status} ${response.statusText} - ${text.substring(0, 200)}...`);
                      });
                 });
             })
             .then(data => {
                 if (data.success) {
                     alert(data.message || "Data updated successfully!");
                     hideModal(genericEditModal);
                     window.location.reload(); // Reload page to see changes
                 } else {
                     alert("Update Error: " + (data.error || "Update failed."));
                 }
             })
             .catch(error => {
                 console.error('Fetch Error:', error);
                 alert("An error occurred during update: " + error.message);
             });
         });
    }
});


// --- Add Game Modal Logic (for index.html) ---
document.addEventListener('DOMContentLoaded', function() {
    const addGameModalIndex = document.getElementById("addGameModal");
    if (addGameModalIndex) {
        const addBtnIndex = document.getElementById("addGameBtn");
        const addCloseSpanIndex = addGameModalIndex.querySelector(".close-button");
        const addCancelButtonIndex = addGameModalIndex.querySelector(".cancel-button");
        const addFormIndex = document.getElementById("addGameForm");

        // Event listeners for add game modal
        if(addBtnIndex) {
            addBtnIndex.addEventListener('click', function(event) {
                event.preventDefault();
                showModal(addGameModalIndex);
            });
        }
        if(addCloseSpanIndex) addCloseSpanIndex.addEventListener('click', function() { hideModal(addGameModalIndex); });
        if(addCancelButtonIndex) addCancelButtonIndex.addEventListener('click', function() { hideModal(addGameModalIndex); });


        // AJAX form submit for add game modal
        if(addFormIndex) {
            addFormIndex.addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(addFormIndex);
                fetch(addFormIndex.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                         return response.json().then(data => {
                            throw new Error(data.error || `HTTP error! Status: ${response.status}`);
                        }).catch(() => { // Catch JSON parse error
                           return response.text().then(text => {
                               throw new Error(`Non-JSON error response: ${response.status} ${response.statusText} - ${text.substring(0, 200)}...`);
                           });
                        });
                    }
                    return response.json().catch(() => { // Catch JSON parse error on success
                         return response.text().then(text => {
                             throw new Error(`Unexpected non-JSON success response: ${response.status} ${response.statusText} - ${text.substring(0, 200)}...`);
                         });
                    });
                })
                .then(data => {
                    if (data.success) {
                        alert(data.message || "Game added successfully!");
                        hideModal(addGameModalIndex);
                        window.location.reload(); // Reload page to see new game
                    } else {
                        alert("Add Game Error: " + (data.error || "Failed to add game."));
                    }
                })
                .catch(error => {
                    console.error('Fetch Error:', error);
                    alert("An error occurred while adding game: " + error.message);
                });
            });
        }
    }
});

// --- Attach Edit Link Handler After DOM Load ---
document.addEventListener('DOMContentLoaded', function() {
     const editItemLinks = document.querySelectorAll(".edit-item-link");
     editItemLinks.forEach(link => {
         link.addEventListener('click', function(event) {
             handleEditItemClick(event, link); // Call the generic handler
         });
     });
});

// --- Attach Generic Edit Modal Close Button Handlers ---
document.addEventListener('DOMContentLoaded', function() {
    const genericEditModal = document.getElementById("genericEditModal");
    if (genericEditModal) {
        const genericEditCloseSpan = genericEditModal.querySelector(".close-button");
        const genericEditCancelButton = genericEditModal.querySelector(".cancel-button");
        if(genericEditCloseSpan) genericEditCloseSpan.addEventListener('click', function() { hideModal(genericEditModal); });
        if(genericEditCancelButton) genericEditCancelButton.addEventListener('click', function() { hideModal(genericEditModal); });
    }
});