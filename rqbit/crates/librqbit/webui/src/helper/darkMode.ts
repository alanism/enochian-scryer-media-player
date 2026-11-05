let saved: string | null = null;
try {
  saved = localStorage.getItem("enochian.finish.v1");
} catch {
  /* The interface still works when storage is unavailable. */
}
let darkMode = saved !== "ivory";
export const DarkMode = {
  isDark: () => darkMode,
  setDark: (value: boolean) => {
    darkMode = value;
    document.body.classList.toggle("dark", value);
    document.documentElement.dataset.finish = value ? "obsidian" : "ivory";
    document
      .querySelectorAll("[data-enochian-finish]")
      .forEach((el) =>
        el.setAttribute("data-finish", value ? "obsidian" : "ivory"),
      );
    try {
      localStorage.setItem("enochian.finish.v1", value ? "obsidian" : "ivory");
    } catch {
      /* This session can still change finish. */
    }
    return value;
  },
  toggle: () => {
    DarkMode.setDark(!darkMode);
  },
};
DarkMode.setDark(darkMode);
