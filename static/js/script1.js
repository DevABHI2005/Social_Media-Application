document.getElementById('cover-photo-input').addEventListener('change', function(event) {
	const file = event.target.files[0];
	if (file) {
		const reader = new FileReader();
		reader.onload = function(e) {
			document.getElementById('cover-photo').src = e.target.result;
		};
		reader.readAsDataURL(file);
	}
});