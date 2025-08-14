// Experience Timeline Interaction
document.addEventListener('DOMContentLoaded', function() {
    const timelinePoints = document.querySelectorAll('.timeline-point');
    const experienceCards = document.querySelectorAll('.experience-card');
    const cardsContainer = document.querySelector('.experience-cards');
    let currentIndex = 0;
    let autoRotateInterval;
    
    // Calculate and set container height to prevent layout shift
    function setContainerHeight() {
        let maxHeight = 0;
        experienceCards.forEach(card => {
            // Temporarily show card to measure height
            card.style.visibility = 'hidden';
            card.style.display = 'block';
            card.style.position = 'relative';
            const height = card.offsetHeight;
            // Reset styles
            card.style.visibility = '';
            card.style.display = '';
            card.style.position = '';
            
            if (height > maxHeight) {
                maxHeight = height;
            }
        });
        
        if (cardsContainer && maxHeight > 0) {
            cardsContainer.style.minHeight = maxHeight + 'px';
        }
    }
    
    // Set initial container height
    setContainerHeight();
    
    // Recalculate on window resize
    window.addEventListener('resize', setContainerHeight);
    
    // Function to show specific experience
    function showExperience(index) {
        // Remove active class from all points and cards
        timelinePoints.forEach(p => p.classList.remove('active'));
        experienceCards.forEach(c => c.classList.remove('active'));
        
        // Add active class to current point and card
        if (timelinePoints[index]) {
            timelinePoints[index].classList.add('active');
            const targetExperience = timelinePoints[index].getAttribute('data-experience');
            const targetCard = document.getElementById(targetExperience);
            if (targetCard) {
                targetCard.classList.add('active');
            }
        }
        
        currentIndex = index;
    }
    
    // Auto-rotate function
    function startAutoRotate() {
        autoRotateInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % timelinePoints.length;
            showExperience(currentIndex);
        }, 4000); // Change every 4 seconds
    }
    
    // Stop auto-rotate function
    function stopAutoRotate() {
        if (autoRotateInterval) {
            clearInterval(autoRotateInterval);
        }
    }
    
    // Handle timeline point clicks
    timelinePoints.forEach((point, index) => {
        point.addEventListener('click', function() {
            stopAutoRotate(); // Stop auto-rotate on user interaction
            showExperience(index);
            
            // Restart auto-rotate after 10 seconds of inactivity
            setTimeout(startAutoRotate, 10000);
        });
    });
    
    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.target.classList.contains('timeline-point')) {
            const currentPoint = e.target;
            const allPoints = Array.from(timelinePoints);
            const currentIndex = allPoints.indexOf(currentPoint);
            
            if (e.key === 'ArrowRight' && currentIndex < allPoints.length - 1) {
                e.preventDefault();
                allPoints[currentIndex + 1].focus();
                allPoints[currentIndex + 1].click();
            } else if (e.key === 'ArrowLeft' && currentIndex > 0) {
                e.preventDefault();
                allPoints[currentIndex - 1].focus();
                allPoints[currentIndex - 1].click();
            }
        }
    });
    
    // Make timeline points keyboard accessible
    timelinePoints.forEach(point => {
        point.setAttribute('tabindex', '0');
        point.setAttribute('role', 'button');
        point.setAttribute('aria-label', 
            `View ${point.querySelector('.timeline-point-title').textContent} experience`
        );
        
        // Allow Enter/Space to activate
        point.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Stop auto-rotate when hovering over cards
    const experienceSection = document.querySelector('.experience');
    if (experienceSection) {
        experienceSection.addEventListener('mouseenter', stopAutoRotate);
        experienceSection.addEventListener('mouseleave', () => {
            stopAutoRotate(); // Clear any existing
            startAutoRotate(); // Start new rotation
        });
    }
    
    // Start auto-rotation
    startAutoRotate();
});