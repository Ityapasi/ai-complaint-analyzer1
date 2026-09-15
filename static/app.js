document.addEventListener("DOMContentLoaded", () => {
    // --- 1. SECURITY CHECK (JWT / Role-Based Access Control) ---
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    // If not logged in, redirect immediately to login page
    if (!token) {
        window.location.href = "/static/login.html";
        return;
    }

    // If logged in as admin, display the hidden admin analytics section
    if (role === "admin") {
        const adminSection = document.getElementById("adminSection");
        if (adminSection) {
            adminSection.style.display = "block";
        }
    }

    const form = document.getElementById("complaintForm");
    const responseMessage = document.getElementById("responseMessage");

    // --- 2. Handle Form Submission for Citizen Portal ---
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const description = document.getElementById("description").value;
            const category = document.getElementById("category").value;
            const imageFile = document.getElementById("imageFile").files[0];

            const formData = new FormData();
            formData.append("description", description);
            formData.append("category", category);
            formData.append("imageFile", imageFile);

            responseMessage.style.color = "blue";
            responseMessage.innerText = "Uploading complaint and analyzing via Deep Learning AI...";

            try {
                const res = await fetch("/api/submit-complaint", {
                    method: "POST",
                    body: formData
                });

                const result = await res.json();
                if (res.ok) {
                    responseMessage.style.color = "green";
                    responseMessage.innerText = "Success: " + result.message;
                    form.reset();

                    // Refresh charts if admin view is active
                    if (role === "admin") {
                        loadAnalytics();
                    }
                } else {
                    responseMessage.style.color = "red";
                    responseMessage.innerText = "Error: " + (result.detail || "Submission failed");
                }
            } catch (err) {
                responseMessage.style.color = "red";
                responseMessage.innerText = "Network Error: Could not connect to backend server.";
            }
        });
    }

    // --- 3. Load Data Visualization Charts for Admin Dashboard ---
    async function loadAnalytics() {
        try {
            const res = await fetch("/api/analytics");
            const data = await res.json();

            // --- Chart 1: Donut Chart (Categories Breakdown) ---
            const ctx1 = document.getElementById("categoryChart");
            if (ctx1) {
                if (window.myCategoryChart instanceof Chart) {
                    window.myCategoryChart.destroy();
                }

                window.myCategoryChart = new Chart(ctx1.getContext("2d"), {
                    type: 'doughnut',
                    data: {
                        labels: data.categories,
                        datasets: [{
                            label: 'Complaint Count by Category',
                            data: data.counts,
                            backgroundColor: [
                                '#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#e67e22'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'right' },
                            title: { display: true, text: 'Complaints Breakdown by Category' }
                        }
                    }
                });
            }

            // --- Chart 2: Trend Line Chart (Weekly Volume Spikes) ---
            const ctx2 = document.getElementById("trendChart");
            if (ctx2) {
                if (window.myTrendChart instanceof Chart) {
                    window.myTrendChart.destroy();
                }

                window.myTrendChart = new Chart(ctx2.getContext("2d"), {
                    type: 'line',
                    data: {
                        labels: data.trend_labels,
                        datasets: [{
                            label: 'Complaint Volume Spikes',
                            data: data.trend_data,
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.2)',
                            fill: true,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            title: { display: true, text: 'Infrastructure Load Trend (Weekly Spikes)' }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            }

        } catch (err) {
            console.error("Failed to load analytics charts data.", err);
        }
    }

    // Load analytics charts automatically if user is admin
    if (role === "admin") {
        loadAnalytics();
    }
});

// --- 4. Global Logout Function ---
window.logout = function() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "/static/login.html";
};