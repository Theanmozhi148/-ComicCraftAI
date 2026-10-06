/**
 * ComicCraft - Client Interaction and Pipeline Manager
 */

document.addEventListener("DOMContentLoaded", () => {
  // Handle Comic Creation Form Submission
  const comicForm = document.getElementById("comicForm");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const loadingStep = document.getElementById("loadingStep");

  if (comicForm && loadingOverlay) {
    comicForm.addEventListener("submit", () => {
      loadingOverlay.style.display = "flex";

      const steps = [
        "Connecting to Gemini Flash AI...",
        "Crafting structured 5-panel comic outline...",
        "Calling Gemini Pro to write character dialogue & narration...",
        "Generating comic-style panel illustrations...",
        "Assembling panels and building exportable PDF..."
      ];

      let stepIndex = 0;
      const interval = setInterval(() => {
        stepIndex++;
        if (stepIndex < steps.length && loadingStep) {
          loadingStep.textContent = steps[stepIndex];
        } else {
          clearInterval(interval);
        }
      }, 2500);
    });
  }

  // Handle PDF Download and Redirect to Export Success
  const downloadBtns = document.querySelectorAll(".btn-download-pdf");
  downloadBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      const pdfPath = btn.getAttribute("data-pdf-path");
      if (pdfPath) {
        // Trigger browser download via direct download link
        const tempLink = document.createElement("a");
        tempLink.href = `/download-pdf?file_path=${encodeURIComponent(pdfPath)}`;
        tempLink.download = "";
        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);

        // Redirect user to export success page after a short delay
        setTimeout(() => {
          window.location.href = `/export-success?pdf_path=${encodeURIComponent(pdfPath)}`;
        }, 1200);
      }
    });
  });
});
