// DOM element references
const form = document.getElementById('searchForm');
const loadingDiv = document.getElementById('loading');
const audioPlayer = document.getElementById('audioPlayer');
const nextButton = document.getElementById('nextButton');
const thumbnailDiv = document.getElementById('thumbnail');
const thumbnailImg = document.getElementById('thumbnailImg');
const songTitle = document.getElementById('songTitle');

// Event listener for form submission
form.addEventListener('submit', function(event) {
    event.preventDefault();
    const songName = document.getElementById('songName').value;
    loadingDiv.style.display = 'block';
    thumbnailDiv.classList.add('thumbnail-loading');
    thumbnailDiv.style.display = 'block';
    searchSong(songName);
});

// Event listener for next button click
nextButton.addEventListener('click', function() {
    if (!nextButton.disabled) {
        nextButton.disabled = true;
        loadingDiv.style.display = 'block';
        thumbnailDiv.classList.add('thumbnail-loading');
        thumbnailDiv.style.display = 'block';
        fetchNextSong().then(() => {
            nextButton.disabled = false;
            loadingDiv.style.display = 'none';
            thumbnailDiv.classList.remove('thumbnail-loading');
        });
    }
});

// Event listener for when the current song ends
audioPlayer.addEventListener('ended', function() {
    loadingDiv.style.display = 'block';
    thumbnailDiv.classList.add('thumbnail-loading');
    fetchNextSong().then(() => {
        loadingDiv.style.display = 'none';
        thumbnailDiv.classList.remove('thumbnail-loading');
    });
});

// Function to search for a song
async function searchSong(songName) {
    const response = await fetch(`/play?songName=${encodeURIComponent(songName)}`);
    const data = await response.json();

    loadingDiv.style.display = 'none';
    thumbnailDiv.classList.remove('thumbnail-loading');

    if (data.status === 'success') {
        audioPlayer.src = data.url;
        audioPlayer.play();
        if (data.thumbnail) {
            thumbnailImg.src = data.thumbnail;
        } else {
            thumbnailImg.src = 'https://avatarfiles.alphacoders.com/360/thumb-1920-360032.png';
        }
        songTitle.textContent = data.songName;
        thumbnailDiv.style.display = 'block';
    } else {
        console.error('Error:', data.message);
    }
}

// Function to fetch the next recommended song
async function fetchNextSong() {
    const response = await fetch('/nextsong');
    const data = await response.json();

    if (data.status === 'success') {
        audioPlayer.src = data.url;
        audioPlayer.play();
        if (data.thumbnail) {
            thumbnailImg.src = data.thumbnail;
        } else {
            thumbnailImg.src = 'https://avatarfiles.alphacoders.com/360/thumb-1920-360032.png';
        }
        songTitle.textContent = data.songName;
        thumbnailDiv.style.display = 'block';
    } else {
        console.error('Error fetching next song:', data.message);
    }
}
