document.addEventListener('DOMContentLoaded', function() {
    function setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('#sidebar .nav-item');
        
        // Remove active class from all items first
        navItems.forEach(item => item.classList.remove('active'));
        
        // Find the most specific matching path
        let bestMatch = null;
        let bestMatchLength = 0;
        
        navItems.forEach(item => {
            const link = item.querySelector('a');
            if (!link) return;
            
            const href = link.getAttribute('href');
            if (!href) return;
            
            // Normalize paths for comparison
            const normalizedHref = href.endsWith('/') ? href : href + '/';
            const normalizedCurrentPath = currentPath.endsWith('/') ? currentPath : currentPath + '/';
            
            // Check if this path matches and is more specific than our current best match
            if (normalizedCurrentPath.startsWith(normalizedHref) && href.length > bestMatchLength) {
                bestMatch = item;
                bestMatchLength = href.length;
            }
        });
        
        // Add active class to the best matching item
        if (bestMatch) {
            bestMatch.classList.add('active');
        }
    }
    
    // Set active state initially
    setActiveNavItem();
    
    // Handle mobile menu
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    if (mobileMenuBtn && sidebar && mobileOverlay) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-open');
            mobileOverlay.classList.toggle('show');
        });
        
        mobileOverlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-open');
            mobileOverlay.classList.remove('show');
        });
    }
    
    // Add click handlers to nav items
    document.querySelectorAll('#sidebar .nav-item').forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            document.querySelectorAll('#sidebar .nav-item').forEach(navItem => {
                navItem.classList.remove('active');
            });
            
            // Add active class to clicked item
            this.classList.add('active');
        });
    });
});
