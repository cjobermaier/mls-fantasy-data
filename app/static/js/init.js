/**
 * Centralized initialization script to ensure proper loading order
 */
document.addEventListener('DOMContentLoaded', function() {
    // Global app namespace
    window.MLSFantasy = window.MLSFantasy || {};
    
    // Initialize components in the correct order
    initDataTable();
    
    // Only initialize filters after table is ready
    if (window.MLSFantasy.dataTable) {
        initFilters();
    } else {
        console.error("DataTable not initialized, cannot load filters");
    }
    
    // Initialize dark mode (independent of other components)
    initDarkMode();
    
    // Function to initialize DataTable
    function initDataTable() {
        if ($('#player-stats').length === 0) {
            console.error('Table element #player-stats not found!');
            return;
        }
        
        try {
            var table = $('#player-stats').DataTable({
                scrollX: true,
                fixedHeader: true,
                colReorder: true,
                dom: '<"top"f>rt<"bottom"lip>',
                ordering: true,
                pageLength: 15,
                orderMulti: true,
                orderCellsTop: true,
                language: {
                    search: "<i class='fas fa-search'></i> Search:",
                    paginate: {
                        first: "<i class='fas fa-angle-double-left'></i>",
                        last: "<i class='fas fa-angle-double-right'></i>",
                        previous: "<i class='fas fa-angle-left'></i>",
                        next: "<i class='fas fa-angle-right'></i>"
                    }
                },
                columnDefs: [
                    { targets: [8, 12, 13, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30], visible: false }
                ],
                searchBuilder: {
                    container: $('#search-builder-container')
                }
            });
            
            // Store reference in global namespace
            window.MLSFantasy.dataTable = table;
            
            // Initialize table-specific features
            initTableFeatures(table);
            
            console.log('DataTable successfully initialized');
        } catch (e) {
            console.error('Error initializing DataTable:', e);
        }
    }
    
    // Function to initialize DataTable-specific features
    function initTableFeatures(table) {
        // Add sorting instructions
        $('.table-container').prepend(
            '<div class="alert alert-info mb-3">' +
            '<i class="fas fa-info-circle me-2"></i>' +
            '<strong>Multi-Column Sorting:</strong> ' +
            'Hold <kbd>Shift</kbd> while clicking column headers to sort by multiple columns. ' +
            'Example: Click "Key Passes" then Shift+Click "Goals" to sort by both.' +
            '</div>'
        );
        
        // Setup sorting indicators
        $('#player-stats thead th').on('click', function() {
            setTimeout(updateSortIndicators, 100);
        });
        
        // Column visibility toggles
        setupColumnToggles(table);
        
        // Advanced filters toggle
        $('#toggle-search-builder').on('click', function() {
            $('#search-builder-container').toggle();
            if ($('#search-builder-container').is(':visible')) {
                $(this).html('<i class="fas fa-times me-1"></i> Hide Advanced Filters');
                table.searchBuilder.rebuild();
            } else {
                $(this).html('<i class="fas fa-sliders me-1"></i> Advanced Filters');
            }
        });
        
        // Export CSV button
        $('#export-csv').on('click', setupExportCSV(table));
    }
    
    // Function to update sort indicators
    function updateSortIndicators() {
        var sortedColumns = [];
        $('#player-stats thead th').each(function(index) {
            if ($(this).hasClass('sorting_asc') || $(this).hasClass('sorting_desc')) {
                var direction = $(this).hasClass('sorting_asc') ? 'asc' : 'desc';
                sortedColumns.push({
                    index: index,
                    name: $(this).text(),
                    direction: direction
                });
            }
        });
        
        if (sortedColumns.length > 1) {
            var sortMessage = '<div class="current-sort-order mt-2 mb-2 text-primary">' +
                '<small><strong>Current Sort Order:</strong> ';
            
            sortedColumns.forEach(function(col, idx) {
                sortMessage += col.name + ' (' + (col.direction === 'asc' ? '↑' : '↓') + ')';
                if (idx < sortedColumns.length - 1) {
                    sortMessage += ' → ';
                }
            });
            
            sortMessage += '</small></div>';
            
            if ($('.current-sort-order').length) {
                $('.current-sort-order').remove();
            }
            $('.table-controls').prepend(sortMessage);
        } else {
            $('.current-sort-order').remove();
        }
    }
    
    // Function to setup column toggles
    function setupColumnToggles(table) {
        // Initialize button states
        syncButtonStates(table);
        
        // Column toggle buttons
        $('.column-toggle-btn').on('click', function() {
            const columnIndex = parseInt($(this).data('column'));
            const column = table.column(columnIndex);
            
            // Toggle column visibility
            column.visible(!column.visible());
            
            // Update this button's state
            $(this).toggleClass('active', column.visible());
        });
        
        // Show all columns
        $('#show-all-columns').on('click', function() {
            table.columns().visible(true);
            $('.column-toggle-btn').addClass('active');
            syncButtonStates(table);
        });
        
        // Hide all columns
        $('#hide-all-columns').on('click', function() {
            // Keep at least the name column visible
            table.columns().visible(false);
            table.column(1).visible(true);
            syncButtonStates(table);
            $('.column-toggle-btn').removeClass('active');
            $('.column-toggle-btn[data-column="1"]').addClass('active');
        });
        
        // Restore default view
        $('#restore-default-columns').on('click', function() {
            // First, hide all columns
            table.columns().visible(false);
            
            // Define which columns should be visible by default
            const visibleColumns = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 14, 15, 16, 24];
            
            // Make those columns visible
            table.columns(visibleColumns).visible(true);
            
            // Update all toggle buttons to match table state
            syncButtonStates(table);
        });
    }
    
    // Helper function to synchronize button states
    function syncButtonStates(table) {
        $('.column-toggle-btn').each(function() {
            const columnIndex = parseInt($(this).data('column'));
            const isVisible = table.column(columnIndex).visible();
            $(this).toggleClass('active', isVisible);
        });
    }
    
    // Function to setup CSV export
    function setupExportCSV(table) {
        return function() {
            // Get the current filtered data
            var filteredData = table.rows({ search: 'applied' }).data();
            
            // Convert to CSV format
            var csvContent = [];
            
            // Add header row
            var headerRow = [];
            $('#player-stats thead th').each(function() {
                if (table.column($(this).index()).visible()) {
                    headerRow.push('"' + $(this).text() + '"');
                }
            });
            csvContent.push(headerRow.join(','));
            
            // Add data rows
            table.rows({ search: 'applied' }).every(function(rowIdx) {
                var dataRow = [];
                var rowData = this.data();
                
                $('#player-stats thead th').each(function(colIdx) {
                    if (table.column(colIdx).visible()) {
                        dataRow.push('"' + rowData[colIdx] + '"');
                    }
                });
                
                csvContent.push(dataRow.join(','));
            });
            
            // Create downloadable link
            var csvString = csvContent.join('\n');
            var blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
            var link = document.createElement('a');
            
            // Create a URL for the blob
            var url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', 'player_stats_export.csv');
            link.style.visibility = 'hidden';
            
            // Append to the document, click it, and remove it
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };
    }
    
    // Function to initialize filters
    function initFilters() {
        const table = window.MLSFantasy.dataTable;
        
        if (!table) {
            console.error('DataTable not available for filters initialization');
            return;
        }
        
        // Apply filters button
        $('#apply-filters').on('click', function() {
            applyFilters(table);
        });
        
        // Reset filters button
        $('#reset-filters').on('click', function() {
            resetFilters(table);
        });
        
        // Add event listeners for pressing Enter key
        $('.filter-control input').on('keypress', function(e) {
            if (e.which === 13) { // Enter key
                applyFilters(table);
            }
        });
        
        console.log('Filters successfully initialized');
    }
    
    // Function to apply all filters
    function applyFilters(table) {
        let positionVal = $('#position-filter').val();
        let goalVal = $('#goal-filter').val();
        let assistVal = $('#assist-filter').val();
        let pointsVal = $('#points-filter').val();
        let priceMinVal = $('#price-filter').val();
        let priceMaxVal = $('#price-max-filter').val();
        
        console.log('Applying filters:', {
            position: positionVal,
            goals: goalVal,
            assists: assistVal,
            points: pointsVal,
            minPrice: priceMinVal,
            maxPrice: priceMaxVal
        });
        
        // Clear previous filters
        table.search('').columns().search('');
        $.fn.dataTable.ext.search = [];
        
        // Apply position filter
        if (positionVal) {
            table.column(7).search(positionVal, true, false);
        }
        
        // Setup numeric filters
        if (goalVal || assistVal || pointsVal || priceMinVal || priceMaxVal) {
            $.fn.dataTable.ext.search.push(
                function(settings, data, dataIndex) {
                    let pass = true;
                    
                    // Goals filter
                    if (goalVal && pass) {
                        let value = parseFloat(data[10]) || 0;
                        pass = value >= parseFloat(goalVal);
                    }
                    
                    // Assists filter
                    if (assistVal && pass) {
                        let value = parseFloat(data[11]) || 0;
                        pass = value >= parseFloat(assistVal);
                    }
                    
                    // Total Points filter
                    if (pointsVal && pass) {
                        let value = parseFloat(data[5]) || 0;
                        pass = value >= parseFloat(pointsVal);
                    }
                    
                    // Helper function to get cost value
                    let costValue;
                    function getCostValue() {
                        if (costValue === undefined) {
                            let costString = data[3];
                            costValue = parseFloat(costString.replace(/[^0-9.]/g, '')) * 1000000 || 0;
                        }
                        return costValue;
                    }
                    
                    // Min price filter
                    if (priceMinVal && pass) {
                        pass = getCostValue() >= parseFloat(priceMinVal);
                    }
                    
                    // Max price filter
                    if (priceMaxVal && pass) {
                        pass = getCostValue() <= parseFloat(priceMaxVal);
                    }
                    
                    return pass;
                }
            );
        }
        
        // Apply all filters
        table.draw();
    }
    
    // Function to reset filters
    function resetFilters(table) {
        // Reset text inputs
        $('#goal-filter').val('');
        $('#assist-filter').val('');
        $('#points-filter').val('');
        
        // Reset select elements
        $('#position-filter').val('').prop('selectedIndex', 0).trigger('change');
        $('#price-filter').val('').prop('selectedIndex', 0).trigger('change');
        $('#price-max-filter').val('').prop('selectedIndex', 0).trigger('change');
        
        // Clear all DataTables filters
        $.fn.dataTable.ext.search = [];
        table.search('').columns().search('').draw();
        
        console.log('Filters reset');
    }
    
    // Function to initialize dark mode
    function initDarkMode() {
        const darkModeSaved = localStorage.getItem('darkMode');
        const darkModeToggle = document.getElementById('toggleDarkMode');
        
        // Function to enable dark mode
        function enableDarkMode() {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'enabled');
            if (darkModeToggle) {
                darkModeToggle.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
            }
            
            // Add the dark mode stylesheet if it doesn't exist
            if (!document.getElementById('darkModeStyles')) {
                const link = document.createElement('link');
                link.id = 'darkModeStyles';
                link.rel = 'stylesheet';
                link.href = '/static/css/dark-mode.css';
                document.head.appendChild(link);
            }
        }
        
        // Function to disable dark mode
        function disableDarkMode() {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'disabled');
            if (darkModeToggle) {
                darkModeToggle.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
            }
            
            // Remove the dark mode stylesheet
            const darkModeStylesheet = document.getElementById('darkModeStyles');
            if (darkModeStylesheet) {
                darkModeStylesheet.remove();
            }
        }
        
        // Apply saved preference
        if (darkModeSaved === 'enabled') {
            enableDarkMode();
        }
        
        // Toggle dark mode on button click
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', function() {
                if (document.body.classList.contains('dark-mode')) {
                    disableDarkMode();
                } else {
                    enableDarkMode();
                }
            });
        }
        
        console.log('Dark mode initialized');
    }
});