function toggleLike(event, element) {
    event.preventDefault(); // Prevent page reload
    element.classList.toggle('liked');
}
