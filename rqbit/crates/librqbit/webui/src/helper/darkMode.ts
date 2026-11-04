const saved = localStorage.getItem("enochian.finish.v1");
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
    localStorage.setItem("enochian.finish.v1", value ? "obsidian" : "ivory");
    return value;
  },
  toggle: () => {
    DarkMode.setDark(!darkMode);
  },
};
DarkMode.setDark(darkMode);
