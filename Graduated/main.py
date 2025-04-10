import tkinter as tk
from tkinter import messagebox
import threading
from selenium_crl import selenium_crl
from BeautifulSoup import beautifulsoup_crl
from multiprocessing_crl import multiprocessing_crl
from deadlink_checker.deadlink_checker.spiders import scrapy_crl
from multiprocessing import freeze_support
import re
# Crawler method mapping
CRAWLER_METHODS = {
    "Scrapy": {
        "function": scrapy_crl,
        "description": "Use Scrapy framework for web crawling, suitable for complex crawling tasks."
    },
    "BeautifulSoup": {
        "function": beautifulsoup_crl,
        "description": "Use BeautifulSoupParse for static web pages , suitable for simple web crawling."
    },
    "Multiprocessing": {
        "function": multiprocessing_crl,
        "description": "Use multiprocessing, suitable for large-scale crawling tasks."
    },
    "Selenium": {
        "function": selenium_crl,
        "description": "Use Selenium, suitable for dynamically loaded web pages."
    }
}

# start crawling
def start_crl():
    sele_method = method_var.get()  # get the selected method
    start_url = url_ent.get().strip()   # get the input url

    if not start_url:
        messagebox.showerror("Error", "Please enter a valid URL!")
        return
    # verify url format
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not re.match(url_pattern, start_url):
        messagebox.showerror("URL format error", "Please enter a valid URL format (e.g. https://www.abc.com).")
        return

    if sele_method in CRAWLER_METHODS:
        crl_fun = CRAWLER_METHODS[sele_method]["function"]

        # clear the log text box
        log_text.delete(1.0, tk.END)

        # display the log text box
        log_text.grid()

        # run the crawler task in a separate thread
        def run_crl():
            try:
                log_mess(f"Starting {sele_method} crawler with URL: {start_url}")
                result = crl_fun(start_url)  # calls the corresponding crawler method


                root.after(0, lambda: update_ui(result))
            except Exception as e:
                root.after(0, lambda e=e: log_mess(f"An error occurred: {e}"))
                root.after(0, lambda e=e: messagebox.showerror("Error", f"An error occurred: {e}"))

        # updates the UI
        def update_ui(result):
            if result is None:
                log_mess(f"{sele_method} crawler finished with no results.")
                messagebox.showinfo("Success", f"{sele_method} crawler finished with no results.")
            else:
                log_mess(f"{sele_method} crawler finished! Results: {len(result)} dead links found.")
                log_mess("Dead links:")
                for item in result:
                    log_mess(f"Source: {item['source']}, Dead Link: {item['dead_link']}, Status: {item['status']}")
                messagebox.showinfo("Success", f"{sele_method} crawler finished! Results: {len(result)} dead links found.")

        # create and start threads
        crl_thread = threading.Thread(target=run_crl)
        crl_thread.start()
    else:
        messagebox.showerror("Error", "Invalid crawler method selected!")

# output information in the log text box
def log_mess(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)  # automatically scroll to the bottom

# create main window
root = tk.Tk()
root.title("Web Crawler UI")

# set window adaptive
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)  # four columns evenly distribute space
root.rowconfigure(4, weight=1)  # adapts row

# URL input
url_lab = tk.Label(root, text="Enter URL:")
url_lab.grid(row=0, column=0, padx=10, pady=10, sticky="w")
url_ent = tk.Entry(root, width=50)
url_ent.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky="ew")  # the input field spans three columns

# Method Select an option box
method_lab = tk.Label(root, text="Select Crawler Method:")
method_lab.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="w")  # the label spans four columns


method_var = tk.StringVar(value="Scrapy")   # default selection

# hover prompt
for i, method in enumerate(CRAWLER_METHODS.keys()):
    rb = tk.Radiobutton(root, text=method, variable=method_var, value=method)
    rb.grid(row=2, column=i, padx=10, pady=5, sticky="ew")


    def create_tooltip(widget, text):
        tooltip = None

        def enter(event):
            nonlocal tooltip
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(tooltip, text=text, background="gray", relief="solid", borderwidth=1)  # background color gray
            label.pack()

        def leave(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    create_tooltip(rb, CRAWLER_METHODS[method]["description"])

# start button
start_butt = tk.Button(root, text="Start Crawler", command=start_crl)
start_butt.grid(row=3, column=0, columnspan=4, pady=10)

# initially hidden log text box
log_text = tk.Text(root, height=20, width=80)
log_text.grid(row=4, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
log_text.grid_remove()

if __name__ == "__main__":
    freeze_support()
    root.mainloop()