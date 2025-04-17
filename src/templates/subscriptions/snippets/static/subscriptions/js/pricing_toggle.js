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