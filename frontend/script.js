console.log("script.js loaded");

let latestRankings = [];

document.addEventListener("DOMContentLoaded", () => {

    console.log("DOM Loaded");

    const rankBtn =
        document.getElementById("rankBtn");

    const exportBtn =
        document.getElementById("exportBtn");

    if (rankBtn) {

        rankBtn.addEventListener(
            "click",
            rankCandidates
        );
    }

    if (exportBtn) {

        exportBtn.addEventListener(
            "click",
            exportCSV
        );
    }
});


// -------------------------
// EXPORT CSV
// -------------------------
function exportCSV() {

    if (
        !latestRankings ||
        latestRankings.length === 0
    ) {

        alert(
            "No ranking data available"
        );

        return;
    }

    let csv =
        "Rank,Name,Email,Phone,Resume,Score,AI Match,Recommendation\n";

    latestRankings.forEach(
        (
            candidate,
            index
        ) => {

            csv +=
                `${index + 1},` +
                `"${candidate.name}",` +
                `"${candidate.email}",` +
                `"${candidate.phone}",` +
                `"${candidate.filename}",` +
                `${candidate.score},` +
                `${candidate.semantic_score},` +
                `"${candidate.recommendation}"\n`;
        }
    );

    const blob =
        new Blob(
            [csv],
            { type: "text/csv" }
        );

    const url =
        window.URL.createObjectURL(blob);

    const a =
        document.createElement("a");

    a.href = url;

    a.download =
        "RankCV_Report.csv";

    a.click();

    window.URL.revokeObjectURL(url);
}


// -------------------------
// RANK CANDIDATES
// -------------------------
async function rankCandidates() {

    const resultsDiv =
        document.getElementById(
            "results"
        );

    const statusDiv =
        document.getElementById(
            "status"
        );

    const jobDescription =
        document.getElementById(
            "jobDescription"
        ).value;

    const files =
        document.getElementById(
            "resumeFiles"
        ).files;

    if (!jobDescription.trim()) {

        alert(
            "Please enter a Job Description"
        );

        return;
    }

    if (files.length === 0) {

        alert(
            "Please select resumes"
        );

        return;
    }

    statusDiv.innerHTML =
        "Processing Resumes...";

    resultsDiv.innerHTML =
        "<h3>Analyzing Candidates...</h3>";

    const formData =
        new FormData();

    formData.append(
        "job_description",
        jobDescription
    );

    for (
        let i = 0;
        i < files.length;
        i++
    ) {

        formData.append(
            "files",
            files[i]
        );
    }

    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/rank",
                {
                    method: "POST",
                    body: formData
                }
            );

        if (!response.ok) {

            throw new Error(
                "Server returned " +
                response.status
            );
        }

        const data =
            await response.json();

        latestRankings =
            data.rankings;

        let html =
            "<h2>🏆 Candidate Rankings</h2>";

        if (
            !data.rankings ||
            data.rankings.length === 0
        ) {

            html +=
                "<p>No candidates found.</p>";

        } else {

            data.rankings.forEach(
                (
                    candidate,
                    index
                ) => {

                    let matchedSkills =
                        candidate.matched &&
                        candidate.matched.length > 0
                        ? candidate.matched.map(
                            skill =>
                            `<span class="skill-tag">${skill}</span>`
                          ).join("")
                        : "None";

                    let missingSkills =
                        candidate.missing &&
                        candidate.missing.length > 0
                        ? candidate.missing.map(
                            skill =>
                            `<span class="missing-tag">${skill}</span>`
                          ).join("")
                        : "None";

                    let badge = "";

                    if (index === 0) {

                        badge =
                            `<div style="
                                background:#16a34a;
                                color:white;
                                padding:8px;
                                border-radius:8px;
                                margin-bottom:10px;
                                font-weight:bold;
                            ">
                            ⭐ Best Candidate
                            </div>`;
                    }

                    html += `

                    <div class="candidate">

                        ${badge}

                        <h3>
                            Rank ${index + 1}
                        </h3>

                        <p>
                            <strong>Name:</strong>
                            ${candidate.name || "Not Found"}
                        </p>

                        <p>
                            <strong>Email:</strong>
                            ${candidate.email || "Not Found"}
                        </p>

                        <p>
                            <strong>Phone:</strong>
                            ${candidate.phone || "Not Found"}
                        </p>

                        <p>
                            <strong>Resume:</strong>
                            ${candidate.filename}
                        </p>

                        <p class="score">
                            ${candidate.score}%
                        </p>

                        <div class="progress-container">

                            <div
                                class="progress-bar"
                                style="
                                    width:${candidate.score}%;
                                ">
                            </div>

                        </div>

                        <p>
                            <strong>AI Match:</strong>
                            ${candidate.semantic_score || 0}%
                        </p>

                        <p>
                            <strong>Recommendation:</strong>
                            ${candidate.recommendation || "N/A"}
                        </p>

                        <p>
                            <strong>Matched Skills</strong>
                        </p>

                        <div>
                            ${matchedSkills}
                        </div>

                        <p>
                            <strong>Missing Skills</strong>
                        </p>

                        <div>
                            ${missingSkills}
                        </div>

                    </div>
                    `;
                }
            );
        }

        resultsDiv.innerHTML =
            html;

        statusDiv.innerHTML =
            "Completed Successfully";

    } catch (error) {

        console.error(error);

        statusDiv.innerHTML =
            "Failed";

        resultsDiv.innerHTML =
            `
            <h3 style="color:red">
                Error:
                ${error.message}
            </h3>
            `;
    }
}