// main.js

document.addEventListener("DOMContentLoaded", () => {
    handleCookieConsent();
    initAccordionHashLoader();
    initLoanCalculator();
});

// Cookie consent logic
function handleCookieConsent() {
    const banner = document.getElementById("cookie-banner");
    const acceptBtn = document.getElementById("accept-cookies");

    if (!banner || !acceptBtn) return;

    const consent = localStorage.getItem("cookie_consent");
    if (!consent) {
        banner.style.display = "flex";
    }

    acceptBtn.addEventListener("click", () => {
        localStorage.setItem("cookie_consent", "accepted");
        banner.style.display = "none";
    });
}

// Accordion Enhancer for Dashboard navigation by hash link
function initAccordionHashLoader() {
    const hash = window.location.hash;
    if (hash && document.querySelector(hash + ".accordion-collapse")) {
        const collapse = document.querySelector(hash + ".accordion-collapse");
        const button = collapse.previousElementSibling?.querySelector("button");
        if (collapse && button) {
            collapse.classList.add("show");
            button.classList.remove("collapsed");
            collapse.scrollIntoView({ behavior: "smooth" });
        }
    }
}

// Global Loan Calculator functionality
function initLoanCalculator() {
    const amountInput = document.getElementById("loanAmount");
    const termInput = document.getElementById("loanTerm");
    const incomeInput = document.getElementById("monthlyIncome");
    const expensesInput = document.getElementById("monthlyExpenses");

    if (!amountInput || !termInput || !incomeInput || !expensesInput) return;

    const resultsDiv = document.getElementById("results");
    const monthlyPaymentEl = document.getElementById("monthlyPayment");
    const totalRepaymentEl = document.getElementById("totalRepayment");
    const affordabilityMsg = document.getElementById("affordabilityCheck");
    const continueBtn = document.getElementById("continueBtn");
    const chartCanvas = document.getElementById("chartCanvas");
    let chartInstance = null;

    document.getElementById("loanCalcForm").addEventListener("submit", function (e) {
        e.preventDefault();

        const amount = parseFloat(amountInput.value);
        const term = parseInt(termInput.value);
        const income = parseFloat(incomeInput.value);
        const expenses = parseFloat(expensesInput.value);
        const interestRate = 0.1525;

        if (amount > 0 && term > 0 && income > 0 && expenses >= 0) {
            const totalRepayable = amount * (1 + interestRate);
            const monthlyPayment = totalRepayable / term;
            const availableFunds = income - expenses;

            monthlyPaymentEl.innerText = monthlyPayment.toFixed(2);
            totalRepaymentEl.innerText = totalRepayable.toFixed(2);
            resultsDiv.classList.remove("d-none");

            if (monthlyPayment <= availableFunds * 0.4) {
                affordabilityMsg.innerHTML = `<span class="text-success fw-semibold"><i class="fas fa-check-circle me-1"></i> You are likely to afford this loan.</span>`;
                continueBtn.classList.remove("d-none");
            } else if (monthlyPayment <= availableFunds * 0.6) {
                affordabilityMsg.innerHTML = `<span class="text-warning fw-semibold"><i class="fas fa-exclamation-circle me-1"></i> Loan might be borderline based on your expenses.</span>`;
                continueBtn.classList.add("d-none");
            } else {
                affordabilityMsg.innerHTML = `<span class="text-danger fw-semibold"><i class="fas fa-times-circle me-1"></i> This loan may not be affordable with your current financials.</span>`;
                continueBtn.classList.add("d-none");
            }

            const ctx = chartCanvas.getContext("2d");
            if (chartInstance) chartInstance.destroy();

            chartInstance = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: ["Principal", "Interest"],
                    datasets: [{
                        data: [amount, totalRepayable - amount],
                        backgroundColor: ["#007749", "#FF8C00"],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: "bottom" }
                    }
                }
            });
        }
    });
}
