document.querySelectorAll(".local-datetime").forEach((element) => {
    const date = new Date(element.dateTime);

    element.textContent = new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(date);
});