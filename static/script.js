async function deleteMovie(movie_id){
    if (confirm("Are you sure you want to delete this movie?") == true) {
        await fetch(`/movie/delete/${movie_id}`);
        window.location.href = "/";
    }
}

// below section was created with help of Gemini - google AI tool
document.addEventListener('DOMContentLoaded', () => {
    // Getting all the elements from HTML
    const reviewContainer = document.getElementById("review-container");
    const movieId = reviewContainer.dataset.movieId;

    // User clicked 'edit' button and now:
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains("edit-button")) {
            const target = event.target.dataset.target;
            const section = document.getElementById(`${target}-section`);
            const displayElement = section.querySelector(target == "rating"? "#current-rating" : "#current-review");
            const editControls = document.getElementById(`edit-${target}-controls`);
            const inputElement = section.querySelector(target === "rating" ? "#edit-rating-input" : "#edit-review-textarea");
            inputElement.value = displayElement.textContent.replace("stars", "");
            displayElement.style.display = "none";
            event.target.style.display = "none";
            editControls.style.display = "block";

        }

    });

    // User clicked 'save' botton and now:
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains("save-button")) {
            const target = event.target.dataset.target;
            const section = document.getElementById(`${target}-section`);
            const displayElement = section.querySelector(target == "rating"? "#current-rating" : "#current-review");
            const editControls = document.getElementById(`edit-${target}-controls`);
            const inputElement = section.querySelector(target === "rating" ? "#edit-rating-input" : "#edit-review-textarea");
            const newValue = inputElement.value;
            const endpoint = target === "rating" ? '/update_rating' : '/update_review';
            const dataToSend = { movie_id: movieId, [target]: newValue };

            fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dataToSend)
            })
            .then(response => {
                if (response.ok) {
                    displayElement.textContent = target === 'rating' ? `${newValue} /10` : newValue;
                    displayElement.style.display = "block";
                    editControls.style.display = "none";
                    section.querySelector(".edit-button").style.display = "inline-block";
                } else {
                    console.error(`Failed to update ${target}:`, response.status);
                }
                return response.json()
            })
            .then(data => {
                console.log("Backed response:", data);
            })
            .catch(error => {
                console.error(`Error sending update request for ${target}:`, error);
            });
        }  
    });
    // Possible extension like 'cancel' button:
    document.addEventListener('click', (event) => {
    if (event.target.classList.contains('cancel-button')) {
        const target = event.target.dataset.target;
        const section = document.getElementById(`${target}-section`);
        const displayElement = section.querySelector(target === 'rating' ? '#current-rating' : '#current-review');
        const editControls = document.getElementById(`edit-${target}-controls`);

        displayElement.style.display = 'block';
        editControls.style.display = 'none';
        section.querySelector('.edit-button').style.display = 'inline-block';
    }
    });
})