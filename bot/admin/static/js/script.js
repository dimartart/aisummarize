document.addEventListener('DOMContentLoaded', function() {
    // Users table filtering and pagination
    let currentPage = 1;
    const rowsPerPage = 20;
    let allRows = [];
    let filteredRows = [];
    
    function initializeUsersTable() {
        allRows = Array.from(document.querySelectorAll('.users-table tbody tr'));
        filteredRows = [...allRows];
        applyFiltersAndPagination();
        
        // Filter inputs
        const filterTelegram = document.getElementById('filter-telegram');
        const filterUsername = document.getElementById('filter-username');
        const filterCreated = document.getElementById('filter-created');
        const filterClear = document.getElementById('filter-clear');
        
        if (filterTelegram) filterTelegram.addEventListener('input', handleFilter);
        if (filterUsername) filterUsername.addEventListener('input', handleFilter);
        if (filterCreated) filterCreated.addEventListener('change', handleFilter);
        if (filterClear) filterClear.addEventListener('click', clearFilters);
        
        // Pagination buttons
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        if (prevBtn) prevBtn.addEventListener('click', () => changePage(-1));
        if (nextBtn) nextBtn.addEventListener('click', () => changePage(1));
    }
    
    function handleFilter() {
        const telegramQuery = document.getElementById('filter-telegram').value.toLowerCase().trim();
        const usernameQuery = document.getElementById('filter-username').value.toLowerCase().trim();
        const createdDate = document.getElementById('filter-created').value;
        
        filteredRows = allRows.filter(row => {
            const telegramId = row.querySelector('.telegram-id')?.textContent.toLowerCase() || '';
            const username = row.querySelector('.username')?.textContent.toLowerCase() || '';
            const createdAt = row.querySelector('.date')?.textContent || '';
            
            let matchesTelegram = !telegramQuery || telegramId.includes(telegramQuery);
            let matchesUsername = !usernameQuery || username.includes(usernameQuery);
            let matchesCreated = true;
            
            if (createdDate) {
                // Extract date from created_at (format: YYYY-MM-DD HH:MM:SS)
                const dateMatch = createdAt.match(/(\d{4}-\d{2}-\d{2})/);
                if (dateMatch) {
                    matchesCreated = dateMatch[1] === createdDate;
                }
            }
            
            return matchesTelegram && matchesUsername && matchesCreated;
        });
        
        currentPage = 1;
        applyFiltersAndPagination();
    }
    
    function clearFilters() {
        document.getElementById('filter-telegram').value = '';
        document.getElementById('filter-username').value = '';
        document.getElementById('filter-created').value = '';
        handleFilter();
    }
    
    function changePage(direction) {
        currentPage += direction;
        applyFiltersAndPagination();
    }
    
    function applyFiltersAndPagination() {
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        const startIdx = (currentPage - 1) * rowsPerPage;
        const endIdx = startIdx + rowsPerPage;
        
        // Hide all rows
        allRows.forEach(row => row.style.display = 'none');
        
        // Show only filtered and paginated rows
        filteredRows.slice(startIdx, endIdx).forEach(row => row.style.display = '');
        
        // Update pagination UI
        document.getElementById('current-page').textContent = currentPage;
        document.getElementById('total-pages').textContent = totalPages || 1;
        document.getElementById('showing-count').textContent = Math.min(endIdx, filteredRows.length);
        document.getElementById('total-count').textContent = filteredRows.length;
        
        // Update button states
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        if (prevBtn) prevBtn.disabled = currentPage === 1;
        if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
    }
    
    // Initialize users table
    initializeUsersTable();
    loadSummaryStats();
    
    async function loadSummaryStats() {
        try {
            const response = await fetch('/api/summary-stats');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Update total summaries card
            const totalSummariesEl = document.getElementById('total-summaries-card');
            if (totalSummariesEl) {
                totalSummariesEl.textContent = data.total_summaries || 0;
            }
        } catch (error) {
            console.error('Error loading summary stats:', error);
        }
    }
    
    // Tabs toggle
    const tabButtons = document.querySelectorAll('.tab-button');
    const sections = document.querySelectorAll('[data-tab-content]');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const tab = btn.getAttribute('data-tab');
            sections.forEach(sec => {
                const isActive = sec.getAttribute('data-tab-content') === tab;
                if (isActive) {
                    sec.classList.remove('hidden');
                } else {
                    sec.classList.add('hidden');
                }
            });
            
            // Load statistics when switching to statistics tab
            if (tab === 'statistics' && !window.chartInitialized) {
                initializeStatistics();
            }
        });
    });
    
    // Statistics Chart
    let summariesChart = null;
    window.chartInitialized = false;
    
    function initializeStatistics() {
        window.chartInitialized = true;
        
        // Populate years dropdown (last 5 years)
        const yearSelect = document.getElementById('stats-year');
        const currentYear = new Date().getFullYear();
        for (let year = currentYear; year >= currentYear - 4; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            if (year === currentYear) option.selected = true;
            yearSelect.appendChild(option);
        }
        
        // Set current month
        const monthSelect = document.getElementById('stats-month');
        const currentMonth = new Date().getMonth() + 1;
        monthSelect.value = currentMonth;
        
        // Load initial data
        loadStatistics();
        loadMetrics();
        
        // Add event listeners for filters
        monthSelect.addEventListener('change', loadStatistics);
        yearSelect.addEventListener('change', loadStatistics);
    }
    
    async function loadMetrics() {
        try {
            const response = await fetch('/api/metrics');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Update metric cards
            const dauEl = document.getElementById('metric-dau');
            const mauEl = document.getElementById('metric-mau');
            const ratioEl = document.getElementById('metric-ratio');
            
            if (dauEl) dauEl.textContent = data.dau || 0;
            if (mauEl) mauEl.textContent = data.mau || 0;
            if (ratioEl) ratioEl.textContent = (data.dau_mau_ratio || 0) + '%';
        } catch (error) {
            console.error('Error loading metrics:', error);
            console.error('Full error:', error.message);
        }
    }
    
    async function loadStatistics() {
        const month = document.getElementById('stats-month').value;
        const year = document.getElementById('stats-year').value;
        
        try {
            const response = await fetch(`/api/statistics?year=${year}&month=${month}`);
            const data = await response.json();
            
            // Update total summaries
            document.getElementById('total-summaries').textContent = data.total;
            
            // Prepare chart data
            const labels = [];
            for (let i = 1; i <= data.days_in_month; i++) {
                labels.push(i.toString());
            }
            
            // Update or create chart
            updateChart(labels, data.data);
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }
    
    function updateChart(labels, data) {
        const ctx = document.getElementById('summaries-chart').getContext('2d');
        
        if (summariesChart) {
            summariesChart.data.labels = labels;
            summariesChart.data.datasets[0].data = data;
            summariesChart.update();
        } else {
            summariesChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Summaries',
                        data: data,
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                        pointBackgroundColor: '#4f46e5',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointHoverBackgroundColor: '#6366f1',
                        pointHoverBorderColor: '#ffffff',
                        pointHoverBorderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#4f46e5',
                            borderWidth: 1,
                            padding: 12,
                            displayColors: false,
                            callbacks: {
                                title: function(context) {
                                    return `Day ${context[0].label}`;
                                },
                                label: function(context) {
                                    return `${context.parsed.y} summaries`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Day of Month',
                                color: '#b3b3b3',
                                font: {
                                    size: 14,
                                    weight: '600'
                                }
                            },
                            grid: {
                                color: '#374151',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#b3b3b3',
                                maxRotation: 0,
                                autoSkipPadding: 10
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Summaries',
                                color: '#b3b3b3',
                                font: {
                                    size: 14,
                                    weight: '600'
                                }
                            },
                            grid: {
                                color: '#374151',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#b3b3b3',
                                stepSize: 1,
                                precision: 0
                            }
                        }
                    }
                }
            });
        }
    }
});


