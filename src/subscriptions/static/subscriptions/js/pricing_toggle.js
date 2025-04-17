// Define styles for active/inactive toggle buttons
const activeBtnClasses = 'bg-blue-600 text-white hover:bg-blue-700';
const inactiveBtnClasses = 'bg-gray-100 text-gray-700 hover:bg-gray-200';

function showPlans(type) {
    const monthlyPlans = document.getElementById('monthly-plans');
    const yearlyPlans = document.getElementById('yearly-plans');
    const monthlyBtn = document.getElementById('monthly-btn');
    const yearlyBtn = document.getElementById('yearly-btn');

    // Clear existing Tailwind classes before adding new ones
    const clearAndSetClasses = (element, classesToAdd) => {
        if (!element) return;
        element.classList.remove('bg-blue-600', 'text-white', 'hover:bg-blue-700', 'bg-gray-100', 'text-gray-700', 'hover:bg-gray-200');
        classesToAdd.split(' ').forEach(cls => {
            if (cls) element.classList.add(cls);
        });
    };


    if (type === 'monthly') {
        if (monthlyPlans) monthlyPlans.classList.remove('hidden');
        if (yearlyPlans) yearlyPlans.classList.add('hidden');
        // Check if buttons exist before trying to style them (in case yearly_qs is empty)
        if (monthlyBtn) clearAndSetClasses(monthlyBtn, activeBtnClasses);
        if (yearlyBtn) clearAndSetClasses(yearlyBtn, inactiveBtnClasses);
        if (monthlyBtn) monthlyBtn.classList.add('active');
        if (yearlyBtn) yearlyBtn.classList.remove('active');

    } else if (type === 'yearly') {
        if (monthlyPlans) monthlyPlans.classList.add('hidden');
        if (yearlyPlans) yearlyPlans.classList.remove('hidden');
        // Check if buttons exist
        if (monthlyBtn) clearAndSetClasses(monthlyBtn, inactiveBtnClasses);
        if (yearlyBtn) clearAndSetClasses(yearlyBtn, activeBtnClasses);
        if (monthlyBtn) monthlyBtn.classList.remove('active');
        if (yearlyBtn) yearlyBtn.classList.add('active');
    }
}

// Initialize view on page load
document.addEventListener('DOMContentLoaded', (event) => {
    const monthlyPlans = document.getElementById('monthly-plans');
    const yearlyPlans = document.getElementById('yearly-plans'); // Check if yearly plans exist for toggle logic
    const monthlyBtn = document.getElementById('monthly-btn');
    const yearlyBtn = document.getElementById('yearly-btn');

    // Add event listeners
    if (monthlyBtn) {
        monthlyBtn.addEventListener('click', () => showPlans('monthly'));
    }
    if (yearlyBtn) {
        yearlyBtn.addEventListener('click', () => showPlans('yearly'));
    }

    // Only run full toggle logic if both buttons/sections likely exist
    if (monthlyBtn && yearlyBtn && yearlyPlans) {
         if (monthlyPlans && !monthlyPlans.classList.contains('hidden')) {
             showPlans('monthly');
        } else if (yearlyPlans && !yearlyPlans.classList.contains('hidden')) {
             showPlans('yearly');
        } else {
             // Default to monthly if neither is explicitly visible (or yearlyPlans doesn't exist)
             showPlans('monthly');
        }
    } else if (monthlyBtn) {
        // If only monthly button exists, ensure it looks active (optional)
         clearAndSetClasses(monthlyBtn, activeBtnClasses);
         monthlyBtn.classList.add('active');
    }
}); 