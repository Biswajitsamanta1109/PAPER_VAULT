// -----------------------------
// PAPERVAULT WB — MAIN JS SCRIPT
// -----------------------------

// ── STATS COUNTER ANIMATION (Dashboard) ──
function animateCount(el, target, duration) {
    let start = 0;
    const step = Math.ceil(target / (duration / 30));
    const timer = setInterval(() => {
        start += step;
        if (start >= target) { start = target; clearInterval(timer); } //clearInterval(timer) stops the animation when the target count is reached, preventing further increments and ensuring the displayed count does not exceed the intended value.
        el.textContent = start + '+';
    }, 30);
}

const statEl = document.getElementById('stat-papers');
if (statEl) {
    fetch("/search/")                 //fetch("/search/") sends a GET request to the "/search/" endpoint to retrieve the HTML content of the search page. This is done to extract the total number of pages of papers available, which is then used to animate the count displayed in the dashboard statistics.
        .then(r => r.text())          //r.text() converts the response from the fetch request into a text format (HTML) so that it can be processed and searched for the relevant information (total number of pages).
        .then(html => {               //html => { ... } processes the retrieved HTML content to find the total number of pages of papers. It uses a regular expression to match the pattern "Page X of Y" and extracts the total number of pages (Y). If found, it calls animateCount to animate the count display; if not found, it defaults to displaying "50+".
            const match = html.match(/Page \d+ of (\d+)/); //html.match(/Page \d+ of (\d+)/) uses a regular expression to search the HTML content for the pattern "Page X of Y", where X is the current page number and Y is the total number of pages. It captures the total number of pages (Y) for use in the animation.
            if (match) {
                animateCount(statEl, parseInt(match[1]) * 10, 1000);
            } else {
                statEl.textContent = '50+';
            }
        })
        .catch(() => { statEl.textContent = '50+'; });
}

// ── SHOW MORE COLLEGES (Dashboard) ──
document.addEventListener('DOMContentLoaded', function() {
    const showMoreBtn = document.getElementById('showMoreBtn'); //const showMoreBtn = document.getElementById('showMoreBtn'); retrieves the "Show More" button element from the DOM, allowing the script to attach an event listener to it for handling user interactions.
    if (showMoreBtn) {
        showMoreBtn.addEventListener('click', function() {
            document.querySelectorAll('.college-card-wrapper').forEach(card => {
                card.style.display = '';
            });
            this.style.display = 'none';
        });
    }
});

// ── REUSABLE STREAM FILTER FUNCTION ──
// Works for any college+stream select pair using data-college attributes
function applyStreamFilter(collegeEl, streamEl, resetOnChange) {
    if (!collegeEl || !streamEl) return;

    function doFilter(reset) {
        const selected = collegeEl.value; //collegeEl.value retrieves the currently selected value from the college dropdown. This value is used to determine which streams belong to the selected college, allowing the script to filter the stream options accordingly.
        let hasVisible = false; // hasVisible is a boolean variable that tracks whether any stream options are visible after filtering. It starts as false and is set to true if at least one stream option matches the selected college, ensuring that the stream dropdown is only enabled when there are relevant options to display.

        Array.from(streamEl.options).forEach(opt => { //
            if (!opt.value) return;
            const belongs = !selected || opt.dataset.college === selected; //belongs is a boolean variable that checks if the current stream option belongs to the selected college. It evaluates to true if no college is selected (allowing all streams to be shown) or if the stream's data-college attribute matches the selected college's value, ensuring that only relevant streams are displayed in the dropdown.
            opt.style.display = belongs ? '' : 'none'; //opt.style.display = belongs ? '' : 'none'; sets the display style of each stream option based on whether it belongs to the selected college. If belongs is true, the option is shown (display: ''), otherwise it is hidden (display: 'none'), effectively filtering the stream options in the dropdown to match the selected college.
            if (belongs) hasVisible = true;//
        });

        // Lock stream dropdown if no college selected
        streamEl.disabled = !selected;

        if (reset) {//
            const current = streamEl.querySelector('option:checked'); //current is a variable that holds the currently selected option in the stream dropdown. It is used to check if the selected stream still belongs to the newly selected college. If it doesn't, the stream selection is reset to ensure that users don't have an invalid stream selected after changing the college.
            if (current && current.dataset.college && current.dataset.college !== selected) {//current.dataset.college !== selected checks if the currently selected stream's data-college attribute does not match the newly selected college. If they don't match, it indicates that the selected stream is no longer valid for the chosen college, prompting the script to reset the stream selection to maintain consistency and prevent user confusion.
                streamEl.value = ''; // Reset stream selection if it doesn't belong to the selected college. This ensures that users are not left with an invalid stream selection after changing the college, maintaining a logical and user-friendly interface.
            }// if we change college after selecting  a stream.
        }
    }

    collegeEl.addEventListener('change', () => doFilter(true)); //collegeEl.addEventListener('change', () => doFilter(true)); attaches an event listener to the college dropdown that triggers the doFilter function whenever the selected college changes. The argument true indicates that the stream selection should be reset if it no longer belongs to the newly selected college, ensuring that the stream options remain consistent with the user's college choice.
    // Small delay ensures Django's pre-selected values are read correctly
    setTimeout(() => doFilter(false), 50);
}

document.addEventListener('DOMContentLoaded', function() {// Wait for the DOM to be fully loaded before applying filters and event listeners, ensuring that all necessary elements are available for manipulation.

// ── PAPERS SEARCH PAGE filter ──
applyStreamFilter(
    document.getElementById('collegeSelect'),
    document.getElementById('streamSelect'),
    true
);

// ── PAPERS UPLOAD PAGE filter ──
applyStreamFilter(
    document.getElementById('uploadCollegeSelect'),
    document.getElementById('uploadStreamSelect'),
    true
);

// ── MATERIALS SEARCH PAGE filter ──
applyStreamFilter(
    document.getElementById('matCollegeSelect'),
    document.getElementById('matStreamSelect'),
    true
);

// ── AI LAB filter ──
const aiCollegeSelect = document.querySelector('#dbSection select[name="institution"]');
const aiStreamSelect = document.querySelector('#dbSection select[name="stream"]');
if (aiCollegeSelect && aiStreamSelect) { //aiCollegeSelect && aiStreamSelect checks if both the college and stream select elements exist in the DOM. This ensures that the filtering logic is only applied when both elements are present, preventing errors in cases where one or both elements might be missing from the page.
    function filterAiStreams() {
        const selected = aiCollegeSelect.value; //icollegeSelect.value retrieves the currently selected value from the AI lab college dropdown. This value is used to determine which streams belong to the selected college, allowing the script to filter the stream options accordingly.
        Array.from(aiStreamSelect.options).forEach(opt => { 
            if (!opt.value || opt.value === 'All') return; //opt.value === 'All' checks if the current stream option is the "All" option. If it is, the function returns early, skipping the filtering logic for this option. This ensures that the "All" option remains visible regardless of the selected college, allowing users to view all streams without restriction.
            opt.style.display = (!selected || selected === 'All' || opt.dataset.college === selected) ? '' : 'none'; //opt.style.display = (!selected || selected === 'All' || opt.dataset.college === selected) ? '' : 'none'; sets the display style of each stream option based on whether it belongs to the selected college. If no college is selected, or if "All" is selected, or if the stream's data-college attribute matches the selected college, the option is shown (display: ''). Otherwise, it is hidden (display: 'none'), effectively filtering the stream options in the dropdown to match the selected college.
        });
        // Lock stream if no college selected
        aiStreamSelect.disabled = (!selected || selected === 'All');
        aiStreamSelect.value = 'All';
    }
    aiCollegeSelect.addEventListener('change', filterAiStreams);//aiCollegeSelect.addEventListener('change', filterAiStreams); attaches an event listener to the AI lab college dropdown that triggers the filterAiStreams function whenever the selected college changes. This ensures that the stream options are dynamically filtered based on the user's college selection, providing a responsive and user-friendly interface.
    // Run on page load
    setTimeout(() => filterAiStreams(), 50);
}

// ── UPLOAD MATERIAL: Hide semester for Placement Notes ──
const materialTypeSelect = document.getElementById('materialTypeSelect');
const uploadSemesterField = document.getElementById('uploadSemesterField');
if (materialTypeSelect && uploadSemesterField) {
    function toggleSemester() { //toggleSemester() checks If the selected material type is "PLACEMENT", the semester field is hidden; otherwise, it is shown. This ensures that users are only presented with relevant fields based on their material type selection, improving the form's usability and preventing confusion.
        uploadSemesterField.style.display = materialTypeSelect.value === 'PLACEMENT' ? 'none' : '';
    }
    materialTypeSelect.addEventListener('change', toggleSemester);
    toggleSemester(); // Call on page load to set initial visibility based on pre-selected value, ensuring that the semester field is correctly displayed or hidden when the page first loads, reflecting the current selection of the material type.
}

// ── MATERIALS PAGE: Toggle fields by type ──
const matTypeSelect = document.getElementById('matTypeSelect'); // document.getElementById('materialTypeSelect') is only on upload page, matTypeSelect is for materials search page,
const streamField = document.getElementById('streamField');
const semesterField = document.getElementById('semesterField');
const subjectField = document.getElementById('subjectField');
const placementSubjectSelect = document.getElementById('placementSubjectSelect');

if (matTypeSelect) {
    function toggleMaterialFields() { //Toggle visibility of stream/semester vs subject fields based on material type
        const isPlacement = matTypeSelect.value === 'PLACEMENT';
        if (streamField) streamField.classList.toggle('d-none', isPlacement); //Placement notes don't have streams or semesters, so we hide those fields and show the subject field instead. For other material types, we show stream/semester and hide subject.
        if (semesterField) semesterField.classList.toggle('d-none', isPlacement);
        if (subjectField) subjectField.classList.toggle('d-none', !isPlacement);
        if (isPlacement && placementSubjectSelect && placementSubjectSelect.options.length <= 1) {  // Only load placement subjects when needed and if not already loaded (to avoid unnecessary API calls),placementsubjectSelect.options.length is 1 when only the default "All Subjects" option is present
            loadPlacementSubjects();//loadPlacementSubjects() is called to fetch the list of placement subjects from the server and populate the placementSubjectSelect dropdown with the retrieved subjects. This ensures that users have access to the relevant subject options when they select "PLACEMENT" as the material type.
        }
    }

    function loadPlacementSubjects() {
        fetch('/materials/api/placement-subjects/')//fetch('/materials/api/placement-subjects/') sends a GET request to the specified API endpoint to retrieve a list of placement subjects in JSON format. This allows the script to dynamically populate the placementSubjectSelect dropdown with the relevant subjects based on the server's response.
            .then(r => r.json()) //r.json() converts the response from the fetch request into a JSON object, allowing the script to easily access the list of subjects returned by the API. This enables the subsequent code to iterate over the subjects and create corresponding option elements for the dropdown.
            .then(data => {
                placementSubjectSelect.innerHTML = '<option value="">All Subjects</option>';
                data.subjects.forEach(sub => {
                    const opt = document.createElement('option');
                    opt.value = sub;
                    opt.textContent = sub;
                    placementSubjectSelect.appendChild(opt);
                });
            })
            .catch(() => {}); //catch(() => {}) handles any errors that may occur during the fetch request or JSON parsing. In this case, it does nothing, effectively ignoring the error and preventing the script from crashing. This ensures that the page remains functional even if the API call fails, although it may result in an empty placementSubjectSelect dropdown.
    }

    matTypeSelect.addEventListener('change', toggleMaterialFields);
    toggleMaterialFields();
}

// ── AI LAB FORM: Continue to Analysis button ──
const continueForm = document.querySelector('form[action*="ai-lab/select-subject"]'); //form[action*="ai-lab/select-subject"] selects the form element that has an action attribute containing the substring "ai-lab/select-subject". This is used to identify the specific form on the AI Lab page that allows users to continue to the analysis step after selecting a subject, enabling the script to attach an event listener for handling the form submission.
    continueForm.addEventListener('submit', function() {
        const btn = document.getElementById('continueBtn');
        if (btn) {
            document.getElementById('continueBtnText')?.classList.add('d-none'); //document.getElementById('continueBtnText')?.classList.add('d-none'); hides the text of the "Continue to Analysis" button by adding the 'd-none' class, which is typically used in Bootstrap to apply display: none; This provides visual feedback to the user that the form submission is in progress, preventing further interaction with the button while the request is being processed.
            document.getElementById('continueBtnLoading')?.classList.remove('d-none');
            btn.disabled = true;
        }
    });
}

// ── AI SELECT SUBJECT: Analyze Now button ──
const analyzeForm = document.querySelector('form[action*="ai-lab/analyze"]');
if (analyzeForm) {
    analyzeForm.addEventListener('submit', function() {
        const btn = document.getElementById('analyzeBtn');
        if (btn) {
            document.getElementById('btnText')?.classList.add('d-none');
            document.getElementById('btnLoading')?.classList.remove('d-none');
            btn.disabled = true;
        }
    });
}
});